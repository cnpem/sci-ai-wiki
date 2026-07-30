from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
import subprocess
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncIterator, Literal

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from pdf_context import (
    MAX_PDF_BYTES,
    AttachmentStore,
    PdfAttachment,
    PdfContextError,
    build_attachment_context,
    extract_pdf_attachment,
    validate_session_id,
)
from wiki_chat import WikiIndex


BASE_DIR = Path(__file__).parent.resolve()
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    wiki_path: Path
    agy_bin: str
    timeout_seconds: int
    model: str
    opencode_bin: str = "opencode"
    opencode_model: str = "ollama/gemma4:31b"
    opencode_timeout_seconds: int = 600
    codex_bin: str = "codex"
    codex_model: str = ""
    codex_timeout_seconds: int = 600

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            wiki_path=Path(
                os.getenv(
                    "WIKI_PATH",
                    "/Users/luizlopes/Documents/Mestrado/graph",
                )
            ).expanduser(),
            agy_bin=os.getenv("AGY_BIN", "agy").strip() or "agy",
            timeout_seconds=max(
                30,
                min(int(os.getenv("AGY_TIMEOUT_SECONDS", "300")), 600),
            ),
            model=os.getenv("AGY_MODEL", "").strip(),
            opencode_bin=os.getenv("OPENCODE_BIN", "opencode").strip()
            or "opencode",
            opencode_model=os.getenv(
                "OPENCODE_MODEL",
                "ollama/gemma4:31b",
            ).strip()
            or "ollama/gemma4:31b",
            opencode_timeout_seconds=max(
                60,
                min(
                    int(os.getenv("OPENCODE_TIMEOUT_SECONDS", "600")),
                    1_200,
                ),
            ),
            codex_bin=os.getenv("CODEX_BIN", "codex").strip() or "codex",
            codex_model=os.getenv("CODEX_MODEL", "").strip(),
            codex_timeout_seconds=max(
                60,
                min(
                    int(os.getenv("CODEX_TIMEOUT_SECONDS", "600")),
                    1_200,
                ),
            ),
        )


class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=30_000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=20_000)
    history: list[HistoryMessage] = Field(default_factory=list, max_length=12)
    engine: Literal["antigravity", "opencode", "codex"] = "antigravity"
    session_id: str | None = Field(
        default=None,
        min_length=8,
        max_length=128,
        pattern=r"^[A-Za-z0-9_-]+$",
    )
    attachment_ids: list[str] = Field(default_factory=list, max_length=5)


def resolve_executable(command: str) -> str | None:
    if Path(command).is_absolute():
        return command if Path(command).is_file() else None
    return shutil.which(command)


def build_agent_prompt(
    request: ChatRequest,
    workspace: Path,
    attachment_context: str = "",
) -> str:
    history = "\n\n".join(
        f"{'Researcher' if item.role == 'user' else 'Assistant'}: {item.content}"
        for item in request.history[-8:]
    )
    conversation = f"{history}\n\n" if history else ""
    workspace_root = workspace.resolve()
    file_access_rule = (
        "- Use only read-only listing, search, and file-reading commands inside "
        f"{workspace_root}. Never run commands that write, execute project code, "
        "install packages, access the network, or invoke git mutations."
        if request.engine == "codex"
        else "- Do not use shell or command tools. Use native file-reading "
        "capabilities only."
    )
    return f"""
You are the research agent behind a minimal chat interface.

The only workspace you may inspect is this exact directory:
{workspace_root}

Follow all workspace instructions in GEMINI.md. Inspect the available
.agents/skills and decide whether the llm-wiki-query skill applies. For research
questions, follow that skill and consult the wiki files needed to answer.

Safety and response rules:
- This session is strictly read-only.
- Never create, edit, delete, move, or save files.
- Never offer to save the answer.
{file_access_rule}
- Every file read, directory listing, and search path must be {workspace_root}
  or a descendant of it. Never inspect or search its parent directories,
  including /Users/luizlopes.
- Start with {workspace_root / "GEMINI.md"} and, for a research query,
  {workspace_root / ".agents/skills/llm-wiki-query/SKILL.md"}.
- Answer in the same language as the researcher's latest message.
- Ground claims in the wiki and/or the temporary PDF evidence.
- Cite wiki pages as [[page_id]]. Cite attached PDFs exactly as
  [PDF: filename, p. N].
- State clearly when the wiki does not contain enough evidence.
- Return only the answer for the researcher, without implementation details.

{attachment_context}

Conversation:
{conversation}Researcher: {request.message}
""".strip()


def run_antigravity(
    *,
    executable: str,
    workspace: Path,
    prompt: str,
    timeout_seconds: int,
    model: str = "",
) -> str:
    log_path = Path(tempfile.gettempdir()) / "wiki-agent-ui-antigravity.log"
    command = [
        executable,
        f"--print={prompt}",
        "--mode",
        "plan",
        "--sandbox",
        "--print-timeout",
        f"{timeout_seconds}s",
        "--log-file",
        str(log_path),
    ]
    if model:
        command.extend(["--model", model])

    completed = subprocess.run(
        command,
        cwd=workspace,
        capture_output=True,
        text=True,
        timeout=timeout_seconds + 15,
        check=False,
    )
    output = completed.stdout.strip()
    error_output = completed.stderr.strip()

    if completed.returncode != 0:
        detail = error_output or output or f"agy terminou com código {completed.returncode}"
        raise RuntimeError(detail)
    if not output:
        raise RuntimeError(error_output or "O Antigravity não retornou uma resposta.")
    if output.startswith("jetski: no output produced"):
        raise RuntimeError(output)
    return output


def opencode_environment() -> dict[str, str]:
    permissions = {
        "read": "allow",
        "glob": "allow",
        "grep": "allow",
        "edit": "deny",
        "bash": "deny",
        "webfetch": "deny",
        "task": "deny",
        "skill": "deny",
        "external_directory": "deny",
    }
    runtime_config = {
        "snapshot": False,
        "share": "disabled",
        "enabled_providers": ["ollama"],
        "permission": permissions,
        "agent": {"plan": {"permission": permissions}},
    }
    environment = os.environ.copy()
    environment["OPENCODE_CONFIG_CONTENT"] = json.dumps(runtime_config)
    environment["OPENCODE_DISABLE_AUTOUPDATE"] = "true"
    return environment


def opencode_command(
    *,
    executable: str,
    workspace: Path,
    prompt: str,
    model: str,
) -> list[str]:
    return [
        executable,
        "--pure",
        "run",
        "--agent",
        "plan",
        "--model",
        model,
        "--format",
        "json",
        "--dir",
        str(workspace.resolve()),
        prompt,
    ]


def parse_opencode_answer(output: str) -> str:
    parts: list[str] = []
    for line in output.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "text":
            continue
        text = event.get("part", {}).get("text")
        if text:
            parts.append(str(text))
    return "".join(parts).strip()


def run_opencode(
    *,
    executable: str,
    workspace: Path,
    prompt: str,
    timeout_seconds: int,
    model: str,
) -> str:
    completed = subprocess.run(
        opencode_command(
            executable=executable,
            workspace=workspace,
            prompt=prompt,
            model=model,
        ),
        cwd=workspace,
        env=opencode_environment(),
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )
    output = parse_opencode_answer(completed.stdout)
    error_output = completed.stderr.strip()
    if completed.returncode != 0:
        raise RuntimeError(
            error_output
            or completed.stdout.strip()
            or f"opencode terminou com código {completed.returncode}"
        )
    if not output:
        raise RuntimeError(
            error_output or "O OpenCode não retornou uma resposta."
        )
    return output


def codex_command(
    *,
    executable: str,
    workspace: Path,
    prompt: str,
    model: str = "",
) -> list[str]:
    command = [
        executable,
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--sandbox",
        "read-only",
        "--skip-git-repo-check",
        "--json",
        "--cd",
        str(workspace.resolve()),
    ]
    if model:
        command.extend(["--model", model])
    command.append(prompt)
    return command


def parse_codex_answer(output: str) -> str:
    messages: list[str] = []
    for line in output.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "item.completed":
            continue
        item = event.get("item", {})
        if item.get("type") == "agent_message" and item.get("text"):
            messages.append(str(item["text"]))
    return messages[-1].strip() if messages else ""


def run_codex(
    *,
    executable: str,
    workspace: Path,
    prompt: str,
    timeout_seconds: int,
    model: str = "",
) -> str:
    completed = subprocess.run(
        codex_command(
            executable=executable,
            workspace=workspace,
            prompt=prompt,
            model=model,
        ),
        cwd=workspace,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )
    output = parse_codex_answer(completed.stdout)
    error_output = completed.stderr.strip()
    if completed.returncode != 0:
        raise RuntimeError(
            error_output
            or completed.stdout.strip()
            or f"codex terminou com código {completed.returncode}"
        )
    if not output:
        raise RuntimeError(error_output or "O Codex não retornou uma resposta.")
    return output


def codex_authenticated(executable: str) -> bool:
    try:
        completed = subprocess.run(
            [executable, "login", "status"],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return completed.returncode == 0


async def codex_stream_events(
    *,
    executable: str,
    workspace: Path,
    prompt: str,
    timeout_seconds: int,
    model: str,
    wiki: WikiIndex,
    attachment_sources: list[dict] | None = None,
) -> AsyncIterator[dict]:
    yield {
        "type": "status",
        "phase": "starting",
        "message": "Iniciando o Codex",
    }
    process = await asyncio.create_subprocess_exec(
        *codex_command(
            executable=executable,
            workspace=workspace,
            prompt=prompt,
            model=model,
        ),
        cwd=workspace,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        limit=16 * 1024 * 1024,
    )
    stderr_task = asyncio.create_task(process.stderr.read())
    deadline = asyncio.get_running_loop().time() + timeout_seconds
    answer_parts: list[str] = []
    emitted_items: set[str] = set()

    try:
        while True:
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                raise asyncio.TimeoutError
            line = await asyncio.wait_for(
                process.stdout.readline(),
                timeout=remaining,
            )
            if not line:
                break
            try:
                event = json.loads(line.decode("utf-8", errors="replace"))
            except json.JSONDecodeError:
                continue

            event_type = event.get("type")
            item = event.get("item", {})
            item_type = item.get("type")
            item_id = str(item.get("id", ""))

            if event_type == "turn.started":
                yield {
                    "type": "status",
                    "phase": "codex-analysis",
                    "message": "Analisando a pergunta",
                }
            elif (
                event_type == "item.started"
                and item_id not in emitted_items
            ):
                emitted_items.add(item_id)
                if item_type == "command_execution":
                    message = "Pesquisando arquivos da wiki"
                elif item_type == "reasoning":
                    message = "Raciocinando sobre as evidências"
                else:
                    continue
                yield {
                    "type": "status",
                    "phase": f"codex-item-{item_id or len(emitted_items)}",
                    "message": message,
                }
            elif event_type == "item.completed":
                if item_type == "agent_message" and item.get("text"):
                    answer_parts.append(str(item["text"]))
            elif event_type in {"turn.failed", "error"}:
                detail = (
                    event.get("message")
                    or event.get("error", {}).get("message")
                    or "A execução do Codex falhou."
                )
                raise RuntimeError(str(detail))

        remaining = max(0.1, deadline - asyncio.get_running_loop().time())
        await asyncio.wait_for(process.wait(), timeout=remaining)
        error_output = (
            await stderr_task
        ).decode("utf-8", errors="replace").strip()
        if process.returncode != 0:
            raise RuntimeError(
                error_output
                or f"codex terminou com código {process.returncode}"
            )
        answer = answer_parts[-1].strip() if answer_parts else ""
        if not answer:
            raise RuntimeError(error_output or "O Codex não retornou uma resposta.")
        yield {
            "type": "result",
            **response_payload(
                answer,
                wiki,
                model,
                "codex",
                attachment_sources,
            ),
        }
    except asyncio.CancelledError:
        if process.returncode is None:
            process.kill()
            await process.wait()
        stderr_task.cancel()
        raise
    except asyncio.TimeoutError:
        if process.returncode is None:
            process.kill()
            await process.wait()
        stderr_task.cancel()
        yield {
            "type": "error",
            "message": "O Codex excedeu o tempo limite da consulta.",
        }
    except Exception as error:
        if process.returncode is None:
            process.kill()
            await process.wait()
        stderr_task.cancel()
        yield {
            "type": "error",
            "message": f"Falha ao consultar o Codex: {error}",
        }


async def opencode_stream_events(
    *,
    executable: str,
    workspace: Path,
    prompt: str,
    timeout_seconds: int,
    model: str,
    wiki: WikiIndex,
    attachment_sources: list[dict] | None = None,
) -> AsyncIterator[dict]:
    yield {
        "type": "status",
        "phase": "starting",
        "message": "Iniciando o OpenCode",
    }
    yield {
        "type": "status",
        "phase": "loading-model",
        "message": f"Carregando {opencode_model_label(model)}",
    }

    process = await asyncio.create_subprocess_exec(
        *opencode_command(
            executable=executable,
            workspace=workspace,
            prompt=prompt,
            model=model,
        ),
        cwd=workspace,
        env=opencode_environment(),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        limit=16 * 1024 * 1024,
    )
    stderr_task = asyncio.create_task(process.stderr.read())
    deadline = asyncio.get_running_loop().time() + timeout_seconds
    answer_parts: list[str] = []
    emitted_tools: set[str] = set()
    step_count = 0

    try:
        while True:
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                raise asyncio.TimeoutError
            line = await asyncio.wait_for(
                process.stdout.readline(),
                timeout=remaining,
            )
            if not line:
                break
            try:
                event = json.loads(line.decode("utf-8", errors="replace"))
            except json.JSONDecodeError:
                continue

            event_type = event.get("type")
            part = event.get("part", {})
            if event_type == "step_start":
                step_count += 1
                yield {
                    "type": "status",
                    "phase": f"opencode-step-{step_count}",
                    "message": (
                        "Analisando a pergunta"
                        if step_count == 1
                        else "Sintetizando as evidências"
                    ),
                }
            elif event_type == "tool_use":
                call_id = str(
                    part.get("callID")
                    or part.get("id")
                    or f"tool-{len(emitted_tools)}"
                )
                if call_id in emitted_tools:
                    continue
                emitted_tools.add(call_id)
                tool_name = str(part.get("tool", ""))
                tool_input = part.get("state", {}).get("input", {})
                if tool_name == "read":
                    raw_path = tool_input.get("filePath", "")
                    try:
                        relative_path = Path(raw_path).resolve().relative_to(
                            workspace.resolve()
                        )
                        message = f"Lendo {relative_path}"
                    except (ValueError, OSError):
                        message = "Lendo uma página da wiki"
                elif tool_name in {"grep", "glob"}:
                    message = "Pesquisando arquivos da wiki"
                else:
                    message = "Consultando a wiki"
                yield {
                    "type": "status",
                    "phase": f"opencode-tool-{call_id}",
                    "message": message,
                }
            elif event_type == "text":
                text = part.get("text")
                if text:
                    answer_parts.append(str(text))

        remaining = max(
            0.1,
            deadline - asyncio.get_running_loop().time(),
        )
        await asyncio.wait_for(process.wait(), timeout=remaining)
        error_output = (
            await stderr_task
        ).decode("utf-8", errors="replace").strip()
        if process.returncode != 0:
            raise RuntimeError(
                error_output
                or f"opencode terminou com código {process.returncode}"
            )
        answer = "".join(answer_parts).strip()
        if not answer:
            raise RuntimeError(
                error_output or "O OpenCode não retornou uma resposta."
            )
        yield {
            "type": "result",
            **response_payload(
                answer,
                wiki,
                model,
                "opencode",
                attachment_sources,
            ),
        }
    except asyncio.CancelledError:
        if process.returncode is None:
            process.kill()
            await process.wait()
        stderr_task.cancel()
        raise
    except asyncio.TimeoutError:
        if process.returncode is None:
            process.kill()
            await process.wait()
        stderr_task.cancel()
        yield {
            "type": "error",
            "message": "O OpenCode + Gemma excedeu o tempo limite da consulta.",
        }
    except Exception as error:
        if process.returncode is None:
            process.kill()
            await process.wait()
        stderr_task.cancel()
        yield {
            "type": "error",
            "message": f"Falha ao consultar o OpenCode + Gemma: {error}",
        }


def opencode_model_label(model: str) -> str:
    if model == "ollama/gemma4:31b":
        return "Gemma 4 31B · Ollama"
    return model


def response_payload(
    answer: str,
    wiki: WikiIndex,
    model: str = "",
    backend: Literal["antigravity", "opencode", "codex"] = "antigravity",
    attachment_sources: list[dict] | None = None,
) -> dict:
    cited_ids = list(dict.fromkeys(re.findall(r"\[\[([^\]|#]+)", answer)))
    sources = [
        {
            "id": page.page_id,
            "title": page.title,
            "path": page.relative_path,
        }
        for page_id in cited_ids
        if (page := wiki.by_id.get(page_id)) is not None
    ]
    pdf_citations: dict[str, set[int]] = {}
    for filename, page_number in re.findall(
        r"\[PDF:\s*([^,\]]+),\s*p\.\s*(\d+)\]",
        answer,
        flags=re.IGNORECASE,
    ):
        pdf_citations.setdefault(filename.strip().casefold(), set()).add(
            int(page_number)
        )
    resolved_attachment_sources = attachment_sources or []
    if pdf_citations:
        resolved_attachment_sources = [
            {
                **source,
                "pages": [
                    page
                    for page in source.get("pages", [])
                    if page
                    in pdf_citations.get(
                        str(source.get("filename", "")).casefold(),
                        set(),
                    )
                ],
            }
            for source in resolved_attachment_sources
            if pdf_citations.get(
                str(source.get("filename", "")).casefold(),
                set(),
            )
        ]
        resolved_attachment_sources = [
            source
            for source in resolved_attachment_sources
            if source["pages"]
        ]
    return {
        "answer": answer,
        "model": (
            opencode_model_label(model)
            if backend == "opencode"
            else model or ("Codex" if backend == "codex" else "Antigravity")
        ),
        "backend": backend,
        "sources": sources,
        "attachment_sources": resolved_attachment_sources,
    }


def encode_event(event: dict) -> bytes:
    return (json.dumps(event, ensure_ascii=False) + "\n").encode("utf-8")


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings.from_env()
    app = FastAPI(title="Wiki Research Chat", docs_url=None, redoc_url=None)
    app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

    app.state.settings = config
    app.state.wiki = None
    app.state.wiki_error = None
    app.state.agent_lock = asyncio.Lock()
    app.state.attachments = AttachmentStore()

    try:
        app.state.wiki = WikiIndex(config.wiki_path)
    except ValueError as error:
        app.state.wiki_error = str(error)

    @app.get("/", include_in_schema=False)
    async def index() -> FileResponse:
        return FileResponse(BASE_DIR / "static" / "index.html")

    def attachment_context_for_request(
        request: ChatRequest,
    ) -> tuple[str, list[dict]]:
        if not request.attachment_ids:
            return "", []
        if not request.session_id:
            raise HTTPException(
                status_code=400,
                detail="A conversa precisa de um identificador para usar PDFs.",
            )
        try:
            attachments = app.state.attachments.get_many(
                request.session_id,
                request.attachment_ids,
            )
            return build_attachment_context(attachments, request.message)
        except PdfContextError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    @app.post("/api/attachments", status_code=201)
    async def upload_attachment(
        session_id: str = Form(...),
        file: UploadFile = File(...),
    ) -> dict:
        try:
            session_id = validate_session_id(session_id)
            if file.content_type not in {
                "application/pdf",
                "application/x-pdf",
                "application/octet-stream",
                "",
                None,
            }:
                raise PdfContextError("Envie um arquivo no formato PDF.")
            data = await file.read(MAX_PDF_BYTES + 1)
            if len(data) > MAX_PDF_BYTES:
                raise PdfContextError("O PDF excede o limite de 20 MB.")
            attachment: PdfAttachment = await asyncio.to_thread(
                extract_pdf_attachment,
                data,
                file.filename or "documento.pdf",
            )
            app.state.attachments.add(session_id, attachment)
            return attachment.metadata()
        except PdfContextError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        finally:
            await file.close()

    @app.delete("/api/attachments/{attachment_id}")
    async def remove_attachment(
        attachment_id: str,
        session_id: str = Query(...),
    ) -> dict:
        try:
            removed = app.state.attachments.remove(
                session_id,
                attachment_id,
            )
        except PdfContextError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        return {"removed": removed}

    @app.delete("/api/sessions/{session_id}/attachments")
    async def clear_attachments(session_id: str) -> dict:
        try:
            app.state.attachments.clear(session_id)
        except PdfContextError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        return {"cleared": True}

    @app.get("/api/health")
    async def health() -> dict:
        wiki: WikiIndex | None = app.state.wiki
        antigravity_executable = resolve_executable(config.agy_bin)
        opencode_executable = resolve_executable(config.opencode_bin)
        codex_executable = resolve_executable(config.codex_bin)
        codex_auth_ready = bool(
            codex_executable and codex_authenticated(codex_executable)
        )
        engines = [
            {
                "id": "antigravity",
                "label": "Antigravity",
                "model": config.model or "Antigravity",
                "ready": bool(antigravity_executable and wiki),
            },
            {
                "id": "opencode",
                "label": "OpenCode · Gemma 4 31B",
                "model": opencode_model_label(config.opencode_model),
                "ready": bool(opencode_executable and wiki),
                "local": True,
            },
            {
                "id": "codex",
                "label": "Codex",
                "model": config.codex_model or "Modelo da conta",
                "ready": bool(codex_auth_ready and wiki),
            },
        ]
        return {
            "ready": any(engine["ready"] for engine in engines),
            "agentReady": bool(antigravity_executable),
            "opencodeReady": bool(opencode_executable),
            "codexReady": codex_auth_ready,
            "wikiReady": wiki is not None,
            "wikiError": app.state.wiki_error,
            "documents": len(wiki.pages) if wiki else 0,
            "model": config.model or "Antigravity",
            "backend": "antigravity",
            "engines": engines,
        }

    @app.get("/api/wiki/{page_id}")
    async def wiki_page(page_id: str) -> dict:
        wiki: WikiIndex | None = app.state.wiki
        if not wiki:
            raise HTTPException(status_code=503, detail=app.state.wiki_error)
        page = wiki.by_id.get(page_id)
        if not page:
            raise HTTPException(status_code=404, detail="Página não encontrada na wiki.")
        return {
            "id": page.page_id,
            "title": page.title,
            "path": page.relative_path,
            "content": page.content,
        }

    @app.post("/api/chat")
    async def chat(request: ChatRequest) -> dict:
        engine_options = {
            "antigravity": (
                config.agy_bin,
                run_antigravity,
                config.timeout_seconds,
                config.model,
                "Antigravity",
            ),
            "opencode": (
                config.opencode_bin,
                run_opencode,
                config.opencode_timeout_seconds,
                config.opencode_model,
                "OpenCode + Gemma",
            ),
            "codex": (
                config.codex_bin,
                run_codex,
                config.codex_timeout_seconds,
                config.codex_model,
                "Codex",
            ),
        }
        agent_bin, runner, timeout_seconds, model, agent_name = engine_options[
            request.engine
        ]
        executable = resolve_executable(agent_bin)
        if not executable:
            raise HTTPException(
                status_code=503,
                detail=f"{agent_name} CLI não encontrado neste computador.",
            )
        if request.engine == "codex" and not codex_authenticated(executable):
            raise HTTPException(
                status_code=503,
                detail="Codex não autenticado. Execute `codex login` neste computador.",
            )
        wiki: WikiIndex | None = app.state.wiki
        if not wiki:
            raise HTTPException(status_code=503, detail=app.state.wiki_error)
        attachment_context, attachment_sources = (
            attachment_context_for_request(request)
        )

        try:
            async with app.state.agent_lock:
                runner_options = {
                    "executable": executable,
                    "workspace": config.wiki_path,
                    "prompt": build_agent_prompt(
                        request,
                        config.wiki_path,
                        attachment_context,
                    ),
                    "timeout_seconds": timeout_seconds,
                    "model": model,
                }
                answer = await asyncio.to_thread(runner, **runner_options)
        except subprocess.TimeoutExpired as error:
            raise HTTPException(
                status_code=504,
                detail=f"O {agent_name} excedeu o tempo limite da consulta.",
            ) from error
        except Exception as error:
            raise HTTPException(
                status_code=502,
                detail=f"Falha ao consultar o {agent_name}: {error}",
            ) from error

        return response_payload(
            answer,
            wiki,
            model,
            request.engine,
            attachment_sources,
        )

    @app.post("/api/chat/stream")
    async def chat_stream(request: ChatRequest) -> StreamingResponse:
        wiki: WikiIndex | None = app.state.wiki
        if not wiki:
            raise HTTPException(status_code=503, detail=app.state.wiki_error)
        attachment_context, attachment_sources = (
            attachment_context_for_request(request)
        )
        prompt = build_agent_prompt(
            request,
            config.wiki_path,
            attachment_context,
        )

        async def events():
            if request.engine == "codex":
                executable = resolve_executable(config.codex_bin)
                if not executable:
                    yield encode_event(
                        {
                            "type": "error",
                            "message": "Codex CLI não encontrado.",
                        }
                    )
                    return
                if not codex_authenticated(executable):
                    yield encode_event(
                        {
                            "type": "error",
                            "message": (
                                "Codex não autenticado. Execute `codex login` "
                                "neste computador."
                            ),
                        }
                    )
                    return
                async with app.state.agent_lock:
                    async for event in codex_stream_events(
                        executable=executable,
                        workspace=config.wiki_path,
                        prompt=prompt,
                        timeout_seconds=config.codex_timeout_seconds,
                        model=config.codex_model,
                        wiki=wiki,
                        attachment_sources=attachment_sources,
                    ):
                        yield encode_event(event)
                return

            if request.engine == "opencode":
                executable = resolve_executable(config.opencode_bin)
                if not executable:
                    yield encode_event(
                        {
                            "type": "error",
                            "message": "OpenCode CLI não encontrado.",
                        }
                    )
                    return
                async with app.state.agent_lock:
                    async for event in opencode_stream_events(
                        executable=executable,
                        workspace=config.wiki_path,
                        prompt=prompt,
                        timeout_seconds=config.opencode_timeout_seconds,
                        model=config.opencode_model,
                        wiki=wiki,
                        attachment_sources=attachment_sources,
                    ):
                        yield encode_event(event)
                return

            executable = resolve_executable(config.agy_bin)
            if not executable:
                yield encode_event(
                    {
                        "type": "error",
                        "message": "Antigravity CLI (agy) não encontrado.",
                    }
                )
                return

            async with app.state.agent_lock:
                yield encode_event(
                    {
                        "type": "status",
                        "phase": "starting",
                        "message": "Iniciando o Antigravity",
                    }
                )
                log_path = (
                    Path(tempfile.gettempdir())
                    / f"wiki-agent-ui-{uuid.uuid4().hex}.log"
                )
                command = [
                    executable,
                    f"--print={prompt}",
                    "--mode",
                    "plan",
                    "--sandbox",
                    "--print-timeout",
                    f"{config.timeout_seconds}s",
                    "--log-file",
                    str(log_path),
                ]
                if config.model:
                    command.extend(["--model", config.model])

                process = await asyncio.create_subprocess_exec(
                    *command,
                    cwd=config.wiki_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                communicate_task = asyncio.create_task(process.communicate())
                log_offset = 0
                emitted: set[str] = {"starting"}
                generation_rounds = 0
                failed = False

                try:
                    while not communicate_task.done():
                        await asyncio.sleep(0.25)
                        if not log_path.is_file():
                            continue
                        log_text = log_path.read_text(
                            encoding="utf-8",
                            errors="replace",
                        )
                        new_log = log_text[log_offset:]
                        log_offset = len(log_text)

                        statuses: list[tuple[str, str]] = []
                        if (
                            "Reloading system slash commands and skills" in new_log
                            and "skills" not in emitted
                        ):
                            statuses.append(
                                (
                                    "skills",
                                    "Carregando instruções e skills",
                                )
                            )
                        if (
                            "sending message" in new_log
                            and "question" not in emitted
                        ):
                            statuses.append(
                                (
                                    "question",
                                    "Analisando a pergunta",
                                )
                            )

                        new_rounds = new_log.count("streamGenerateContent")
                        if new_rounds:
                            generation_rounds += new_rounds
                            phase = f"generation-{min(generation_rounds, 3)}"
                            if phase not in emitted:
                                messages = {
                                    "generation-1": "Planejando a consulta",
                                    "generation-2": "Consultando arquivos da wiki",
                                    "generation-3": "Sintetizando as evidências",
                                }
                                statuses.append((phase, messages[phase]))

                        for status in statuses:
                            phase, message = status
                            emitted.add(phase)
                            yield encode_event(
                                {
                                    "type": "status",
                                    "phase": phase,
                                    "message": message,
                                }
                            )

                    stdout, stderr = await asyncio.wait_for(
                        communicate_task,
                        timeout=config.timeout_seconds + 15,
                    )
                    output = stdout.decode("utf-8", errors="replace").strip()
                    error_output = stderr.decode(
                        "utf-8",
                        errors="replace",
                    ).strip()
                    if process.returncode != 0:
                        raise RuntimeError(
                            error_output
                            or output
                            or f"agy terminou com código {process.returncode}"
                        )
                    if not output or output.startswith("jetski: no output produced"):
                        raise RuntimeError(
                            output
                            or error_output
                            or "O Antigravity não retornou uma resposta."
                        )
                    yield encode_event(
                        {
                            "type": "result",
                            **response_payload(
                                output,
                                wiki,
                                config.model,
                                "antigravity",
                                attachment_sources,
                            ),
                        }
                    )
                except asyncio.CancelledError:
                    failed = True
                    if process.returncode is None:
                        process.kill()
                        await process.wait()
                    communicate_task.cancel()
                    raise
                except Exception as error:
                    failed = True
                    if process.returncode is None:
                        process.kill()
                        await process.wait()
                    yield encode_event(
                        {
                            "type": "error",
                            "message": f"Falha ao consultar o Antigravity: {error}",
                        }
                    )
                finally:
                    if not failed:
                        log_path.unlink(missing_ok=True)

        return StreamingResponse(
            events(),
            media_type="application/x-ndjson",
            headers={"Cache-Control": "no-cache"},
        )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
