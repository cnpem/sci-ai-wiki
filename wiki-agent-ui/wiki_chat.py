from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_-]{2,}")
TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
LINK_RE = re.compile(r"\[\[([^\]|#]+)")
ALLOWED_TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".csv", ".toml"}
BLOCKED_PARTS = {".git", ".venv", "node_modules", "__pycache__"}
MAX_FILE_CHARS = 120_000

STOP_WORDS = {
    "about",
    "como",
    "com",
    "das",
    "dos",
    "esse",
    "essa",
    "esta",
    "este",
    "for",
    "from",
    "how",
    "mais",
    "para",
    "pela",
    "pelo",
    "por",
    "que",
    "qual",
    "quais",
    "the",
    "uma",
    "what",
    "with",
}


def normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(char for char in decomposed if not unicodedata.combining(char)).lower()


def tokens(text: str) -> set[str]:
    return {
        token
        for token in TOKEN_RE.findall(normalize(text))
        if token not in STOP_WORDS
    }


def token_matches(left: str, right: str) -> bool:
    if left == right:
        return True
    shared = min(len(left), len(right), 8)
    return shared >= 6 and left[:shared] == right[:shared]


def overlap_count(query_tokens: set[str], page_tokens: set[str]) -> int:
    return sum(
        1
        for query_token in query_tokens
        if any(token_matches(query_token, page_token) for page_token in page_tokens)
    )


@dataclass(frozen=True)
class WikiPage:
    page_id: str
    relative_path: str
    title: str
    content: str


class WikiIndex:
    def __init__(self, root: Path):
        self.root = root.expanduser().resolve()
        self.wiki_dir = self.root / "wiki"
        if not self.wiki_dir.is_dir():
            raise ValueError(f"Wiki não encontrada em: {self.wiki_dir}")

        self.pages = self._load_pages()
        if not self.pages:
            raise ValueError(f"Nenhuma página Markdown encontrada em: {self.wiki_dir}")
        self.by_id = {page.page_id: page for page in self.pages}

    def _load_pages(self) -> list[WikiPage]:
        pages: list[WikiPage] = []
        for path in sorted(self.wiki_dir.rglob("*.md")):
            content = path.read_text(encoding="utf-8", errors="replace")
            title_match = TITLE_RE.search(content)
            title = title_match.group(1).strip() if title_match else path.stem
            pages.append(
                WikiPage(
                    page_id=path.stem,
                    relative_path=path.relative_to(self.root).as_posix(),
                    title=title,
                    content=content,
                )
            )
        return pages

    def search(
        self,
        query: str,
        *,
        limit: int = 8,
        max_chars: int = 80_000,
    ) -> list[WikiPage]:
        query_normalized = normalize(query).strip()
        query_tokens = tokens(query)
        ranked: list[tuple[float, WikiPage]] = []

        for page in self.pages:
            title_text = normalize(f"{page.page_id} {page.title}")
            body_text = normalize(page.content)
            title_tokens = tokens(title_text)
            body_tokens = tokens(body_text)

            shared_title = overlap_count(query_tokens, title_tokens)
            shared_body = overlap_count(query_tokens, body_tokens)
            score = (shared_title * 12) + (shared_body * 2)
            score += sum(min(body_text.count(token), 8) * 0.25 for token in query_tokens)
            if query_normalized and query_normalized in title_text:
                score += 20
            if score:
                ranked.append((score, page))

        ranked.sort(key=lambda item: (-item[0], item[1].relative_path))
        selected = [page for _, page in ranked[:limit]]

        if not selected:
            selected = [
                page
                for fallback in ("overview", "index")
                if (page := self.by_id.get(fallback)) is not None
            ]

        index_page = self.by_id.get("index")
        if index_page and index_page not in selected:
            selected.append(index_page)

        return self._fit_context(selected, limit=limit + 1, max_chars=max_chars)

    @staticmethod
    def _fit_context(
        pages: Iterable[WikiPage],
        *,
        limit: int,
        max_chars: int,
    ) -> list[WikiPage]:
        result: list[WikiPage] = []
        used = 0
        for page in pages:
            if len(result) >= limit:
                break
            remaining = max_chars - used
            if remaining <= 0:
                break
            if result and len(page.content) > remaining:
                continue
            result.append(page)
            used += len(page.content)
        return result


class WikiTools:
    """Safe, read-only filesystem tools exposed to the Gemini agent."""

    def __init__(self, root: Path):
        self.root = root.expanduser().resolve()
        self.index = WikiIndex(self.root)
        self._accessed: dict[str, WikiPage] = {}

    def _resolve_text_file(self, relative_path: str) -> Path:
        if not relative_path or Path(relative_path).is_absolute():
            raise ValueError("Use um caminho relativo à raiz da wiki.")
        candidate = (self.root / relative_path).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as error:
            raise ValueError("O caminho solicitado está fora da raiz da wiki.") from error
        if any(part in BLOCKED_PARTS for part in candidate.parts):
            raise ValueError("Essa pasta não pode ser acessada.")
        if candidate.suffix.lower() not in ALLOWED_TEXT_SUFFIXES:
            raise ValueError("Somente arquivos de texto da pesquisa podem ser lidos.")
        if not candidate.is_file():
            raise ValueError(f"Arquivo não encontrado: {relative_path}")
        return candidate

    def _record(self, path: Path, content: str | None = None) -> None:
        try:
            wiki_relative = path.relative_to(self.root / "wiki")
        except ValueError:
            return
        if path.suffix.lower() != ".md":
            return
        page_id = path.stem
        page = self.index.by_id.get(page_id)
        if page is None and content is not None:
            title_match = TITLE_RE.search(content)
            page = WikiPage(
                page_id=page_id,
                relative_path=(Path("wiki") / wiki_relative).as_posix(),
                title=title_match.group(1).strip() if title_match else page_id,
                content=content,
            )
        if page:
            self._accessed[page.relative_path] = page

    def list_wiki_files(self, directory: str = "wiki", limit: int = 200) -> dict:
        """List readable research files below a directory.

        Args:
            directory: Relative directory such as "wiki", "wiki/models", or
                ".agents/skills/llm-wiki-query".
            limit: Maximum number of paths to return, from 1 to 300.
        """
        relative = Path(directory or "wiki")
        if relative.is_absolute():
            return {"error": "Use um diretório relativo à raiz da wiki."}
        base = (self.root / relative).resolve()
        try:
            base.relative_to(self.root)
        except ValueError:
            return {"error": "O diretório solicitado está fora da raiz da wiki."}
        if not base.is_dir() or any(part in BLOCKED_PARTS for part in base.parts):
            return {"error": f"Diretório não encontrado ou bloqueado: {directory}"}

        safe_limit = max(1, min(int(limit), 300))
        paths = [
            path.relative_to(self.root).as_posix()
            for path in sorted(base.rglob("*"))
            if path.is_file()
            and path.suffix.lower() in ALLOWED_TEXT_SUFFIXES
            and not any(part in BLOCKED_PARTS for part in path.parts)
        ][:safe_limit]
        return {"directory": relative.as_posix(), "files": paths, "count": len(paths)}

    def search_wiki(self, query: str, limit: int = 8) -> dict:
        """Search the indexed Markdown wiki and return relevant page excerpts.

        Args:
            query: Terms, model names, authors, or concepts to find.
            limit: Maximum number of results, from 1 to 12.
        """
        if not query.strip():
            return {"error": "A busca não pode estar vazia."}
        safe_limit = max(1, min(int(limit), 12))
        pages = self.index.search(query, limit=safe_limit, max_chars=60_000)
        results = []
        for page in pages:
            self._record(self.root / page.relative_path)
            excerpt = page.content[:6_000]
            results.append(
                {
                    "id": page.page_id,
                    "title": page.title,
                    "path": page.relative_path,
                    "excerpt": excerpt,
                    "truncated": len(page.content) > len(excerpt),
                }
            )
        return {"query": query, "results": results}

    def read_wiki_file(
        self,
        path: str,
        start_line: int = 1,
        max_lines: int = 400,
    ) -> dict:
        """Read a text file inside the research project with line numbers.

        Args:
            path: Relative path returned by list_wiki_files or search_wiki.
            start_line: First 1-based line to return.
            max_lines: Maximum lines to return, from 1 to 600.
        """
        try:
            resolved = self._resolve_text_file(path)
        except ValueError as error:
            return {"error": str(error)}

        content = resolved.read_text(encoding="utf-8", errors="replace")
        if len(content) > MAX_FILE_CHARS:
            content = content[:MAX_FILE_CHARS]
        self._record(resolved, content)

        lines = content.splitlines()
        safe_start = max(1, int(start_line))
        safe_count = max(1, min(int(max_lines), 600))
        selected = lines[safe_start - 1 : safe_start - 1 + safe_count]
        numbered = "\n".join(
            f"{number}: {line}"
            for number, line in enumerate(selected, start=safe_start)
        )
        return {
            "path": resolved.relative_to(self.root).as_posix(),
            "content": numbered,
            "startLine": safe_start,
            "endLine": safe_start + len(selected) - 1,
            "totalLines": len(lines),
            "truncated": safe_start - 1 + len(selected) < len(lines),
        }

    def sources(self) -> list[WikiPage]:
        return sorted(self._accessed.values(), key=lambda page: page.relative_path)


def build_context(pages: Iterable[WikiPage]) -> str:
    blocks = []
    for page in pages:
        blocks.append(
            f'<wiki-page id="{page.page_id}" path="{page.relative_path}">\n'
            f"{page.content}\n"
            "</wiki-page>"
        )
    return "\n\n".join(blocks)


def load_query_instructions(root: Path) -> str:
    skill_path = (
        root.expanduser().resolve()
        / ".agents"
        / "skills"
        / "llm-wiki-query"
        / "SKILL.md"
    )
    if skill_path.is_file():
        return skill_path.read_text(encoding="utf-8", errors="replace")
    return ""
