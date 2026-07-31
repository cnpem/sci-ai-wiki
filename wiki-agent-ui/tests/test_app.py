import tomllib
from pathlib import Path

from fastapi.testclient import TestClient

import app as app_module
from app import Settings, create_app
from pdf_context import PdfAttachment, PdfChunk


def make_wiki(tmp_path: Path) -> Path:
    wiki = tmp_path / "wiki"
    (wiki / "concepts").mkdir(parents=True)
    (wiki / "index.md").write_text(
        "# Wiki Index\n\n- [[equivariance]] — symmetry\n",
        encoding="utf-8",
    )
    (wiki / "concepts" / "equivariance.md").write_text(
        "# Equivariance\n\nA transformation in the input produces a predictable "
        "transformation in the output.",
        encoding="utf-8",
    )
    return tmp_path


def test_requirements_match_pyproject_dependencies():
    project_root = Path(__file__).parents[1]
    project = tomllib.loads(
        (project_root / "pyproject.toml").read_text(encoding="utf-8")
    )
    declared = {
        *project["project"]["dependencies"],
        *project["dependency-groups"]["dev"],
    }
    requirements = {
        line.strip()
        for line in (project_root / "requirements.txt")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

    assert requirements == declared


def test_health_reports_antigravity_without_exposing_secrets(
    tmp_path: Path,
    monkeypatch,
):
    settings = Settings(
        wiki_path=make_wiki(tmp_path),
        agy_bin="agy-test",
        timeout_seconds=60,
        model="",
    )
    monkeypatch.setattr(app_module, "resolve_executable", lambda _: "/bin/agy-test")
    client = TestClient(create_app(settings))

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["ready"] is True
    assert response.json()["backend"] == "antigravity"
    assert response.json()["model"] == "Antigravity"
    assert {engine["id"] for engine in response.json()["engines"]} == {
        "antigravity",
        "opencode",
        "codex",
    }
    antigravity = next(
        engine
        for engine in response.json()["engines"]
        if engine["id"] == "antigravity"
    )
    assert antigravity["setupRequired"] is True
    assert response.json()["antigravityConfigured"] is False


def test_antigravity_setup_preserves_settings_and_is_idempotent(
    tmp_path: Path,
):
    workspace = make_wiki(tmp_path)
    settings_path = tmp_path / "antigravity" / "settings.json"
    settings_path.parent.mkdir()
    settings_path.write_text(
        app_module.json.dumps(
            {
                "colorScheme": "dark",
                "permissions": {"deny": ["write_file"]},
                "trustedWorkspaces": ["/another/wiki"],
            }
        ),
        encoding="utf-8",
    )

    first_state = app_module.prepare_antigravity_workspace(
        settings_path,
        workspace,
    )
    second_state = app_module.prepare_antigravity_workspace(
        settings_path,
        workspace,
    )
    saved = app_module.json.loads(settings_path.read_text(encoding="utf-8"))

    assert first_state["configured"] is True
    assert second_state["configured"] is True
    assert saved["colorScheme"] == "dark"
    assert saved["permissions"]["deny"] == ["write_file"]
    assert saved["trustedWorkspaces"].count(str(workspace.resolve())) == 1
    assert saved["permissions"]["allow"] == [
        app_module.antigravity_read_rule(workspace)
    ]


def test_antigravity_setup_endpoints_launch_and_prepare_locally(
    tmp_path: Path,
    monkeypatch,
):
    workspace = make_wiki(tmp_path)
    settings = Settings(
        wiki_path=workspace,
        agy_bin="agy-test",
        timeout_seconds=60,
        model="",
        agy_settings_path=tmp_path / "agy-settings.json",
    )
    launched = {}
    monkeypatch.setattr(
        app_module,
        "resolve_executable",
        lambda _: "/bin/agy-test",
    )

    def fake_launch(executable, launch_workspace):
        launched["executable"] = executable
        launched["workspace"] = launch_workspace
        return True

    monkeypatch.setattr(app_module, "launch_antigravity_login", fake_launch)
    client = TestClient(create_app(settings))

    initial = client.get("/api/setup/antigravity")
    started = client.post("/api/setup/antigravity/start")
    completed = client.post("/api/setup/antigravity/complete")
    health = client.get("/api/health")

    assert initial.status_code == 200
    assert initial.json()["installed"] is True
    assert initial.json()["configured"] is False
    assert str(workspace.resolve()) in initial.json()["command"]
    assert started.status_code == 200
    assert started.json()["launched"] is True
    assert launched == {
        "executable": "/bin/agy-test",
        "workspace": workspace,
    }
    assert completed.status_code == 200
    assert completed.json()["configured"] is True
    assert health.json()["antigravityConfigured"] is True


def test_antigravity_setup_mutations_reject_remote_clients(
    tmp_path: Path,
    monkeypatch,
):
    settings = Settings(
        wiki_path=make_wiki(tmp_path),
        agy_bin="agy-test",
        timeout_seconds=60,
        model="",
        agy_settings_path=tmp_path / "agy-settings.json",
    )
    monkeypatch.setattr(
        app_module,
        "resolve_executable",
        lambda _: "/bin/agy-test",
    )
    client = TestClient(
        create_app(settings),
        client=("198.51.100.9", 41234),
    )

    assert client.get("/api/setup/antigravity").status_code == 403
    assert client.post("/api/setup/antigravity/start").status_code == 403
    assert client.post("/api/setup/antigravity/complete").status_code == 403


def test_chat_runs_antigravity_and_resolves_cited_sources(
    tmp_path: Path,
    monkeypatch,
):
    settings = Settings(
        wiki_path=make_wiki(tmp_path),
        agy_bin="agy-test",
        timeout_seconds=60,
        model="",
    )
    captured = {}

    def fake_run(**kwargs):
        captured.update(kwargs)
        return "A resposta está na wiki [[equivariance]]."

    monkeypatch.setattr(app_module, "resolve_executable", lambda _: "/bin/agy-test")
    monkeypatch.setattr(app_module, "run_antigravity", fake_run)
    client = TestClient(create_app(settings))

    response = client.post(
        "/api/chat",
        json={"message": "O que é equivariância?", "history": []},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["backend"] == "antigravity"
    assert payload["sources"][0]["id"] == "equivariance"
    assert "O que é equivariância?" in captured["prompt"]
    assert f"The only workspace you may inspect is this exact directory:\n{settings.wiki_path.resolve()}" in captured["prompt"]
    assert f"{settings.wiki_path.resolve() / 'GEMINI.md'}" in captured["prompt"]
    assert captured["workspace"] == settings.wiki_path


def test_chat_runs_opencode_with_local_model(tmp_path: Path, monkeypatch):
    settings = Settings(
        wiki_path=make_wiki(tmp_path),
        agy_bin="agy-test",
        timeout_seconds=60,
        model="",
        opencode_bin="opencode-test",
        opencode_model="ollama/gemma4:31b",
    )
    captured = {}

    def fake_run(**kwargs):
        captured.update(kwargs)
        return "Resposta local [[equivariance]]."

    monkeypatch.setattr(
        app_module,
        "resolve_executable",
        lambda command: f"/bin/{command}",
    )
    monkeypatch.setattr(app_module, "run_opencode", fake_run)
    client = TestClient(create_app(settings))

    response = client.post(
        "/api/chat",
        json={
            "message": "Explique equivariância.",
            "history": [],
            "engine": "opencode",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["backend"] == "opencode"
    assert payload["model"] == "Gemma 4 31B · Ollama"
    assert payload["sources"][0]["id"] == "equivariance"
    assert captured["model"] == "ollama/gemma4:31b"
    assert captured["workspace"] == settings.wiki_path


def test_chat_runs_codex_with_saved_login(tmp_path: Path, monkeypatch):
    settings = Settings(
        wiki_path=make_wiki(tmp_path),
        agy_bin="agy-test",
        timeout_seconds=60,
        model="",
        codex_bin="codex-test",
        codex_model="",
    )
    captured = {}

    def fake_run(**kwargs):
        captured.update(kwargs)
        return "Resposta do Codex [[equivariance]]."

    monkeypatch.setattr(
        app_module,
        "resolve_executable",
        lambda command: f"/bin/{command}",
    )
    monkeypatch.setattr(app_module, "codex_authenticated", lambda _: True)
    monkeypatch.setattr(app_module, "run_codex", fake_run)
    client = TestClient(create_app(settings))

    response = client.post(
        "/api/chat",
        json={
            "message": "Explique equivariância.",
            "history": [],
            "engine": "codex",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["backend"] == "codex"
    assert payload["model"] == "Codex"
    assert payload["sources"][0]["id"] == "equivariance"
    assert captured["workspace"] == settings.wiki_path
    assert "Use only read-only listing" in captured["prompt"]


def test_codex_command_is_ephemeral_and_read_only(tmp_path: Path):
    command = app_module.codex_command(
        executable="/bin/codex",
        workspace=tmp_path,
        prompt="Pergunta",
    )

    assert command[:2] == ["/bin/codex", "exec"]
    assert "--ephemeral" in command
    assert "--ignore-user-config" in command
    assert command[command.index("--sandbox") + 1] == "read-only"
    assert "--skip-git-repo-check" in command
    assert "--json" in command
    assert command[-1] == "Pergunta"


def test_parse_codex_answer_uses_completed_agent_messages():
    output = "\n".join(
        [
            '{"type":"thread.started","thread_id":"thread-1"}',
            '{"type":"item.completed","item":{"type":"reasoning","text":"private"}}',
            '{"type":"item.completed","item":{"type":"agent_message","text":"Vou consultar a wiki."}}',
            '{"type":"item.completed","item":{"type":"agent_message","text":"Resposta [[equivariance]]."}}',
            '{"type":"turn.completed","usage":{"input_tokens":10}}',
        ]
    )

    assert (
        app_module.parse_codex_answer(output)
        == "Resposta [[equivariance]]."
    )


def test_opencode_runtime_permissions_are_read_only():
    environment = app_module.opencode_environment()
    runtime = app_module.json.loads(environment["OPENCODE_CONFIG_CONTENT"])

    assert runtime["enabled_providers"] == ["ollama"]
    assert runtime["permission"]["read"] == "allow"
    assert runtime["permission"]["edit"] == "deny"
    assert runtime["permission"]["bash"] == "deny"
    assert runtime["permission"]["webfetch"] == "deny"
    assert runtime["permission"]["task"] == "deny"


def test_parse_opencode_answer_uses_text_events():
    output = "\n".join(
        [
            '{"type":"step_start","part":{"type":"step-start"}}',
            '{"type":"text","part":{"text":"Resposta "}}',
            '{"type":"tool_use","part":{"tool":"read"}}',
            '{"type":"text","part":{"text":"[[equivariance]]."}}',
        ]
    )

    assert (
        app_module.parse_opencode_answer(output)
        == "Resposta [[equivariance]]."
    )


def test_chat_requires_antigravity_executable(tmp_path: Path, monkeypatch):
    settings = Settings(
        wiki_path=make_wiki(tmp_path),
        agy_bin="missing-agy",
        timeout_seconds=60,
        model="",
    )
    monkeypatch.setattr(app_module, "resolve_executable", lambda _: None)
    client = TestClient(create_app(settings))

    response = client.post(
        "/api/chat",
        json={"message": "Pergunta", "history": []},
    )

    assert response.status_code == 503
    assert "Antigravity CLI" in response.json()["detail"]


def test_wiki_page_endpoint_returns_markdown(tmp_path: Path):
    settings = Settings(
        wiki_path=make_wiki(tmp_path),
        agy_bin="agy-test",
        timeout_seconds=60,
        model="",
    )
    client = TestClient(create_app(settings))

    response = client.get("/api/wiki/equivariance")

    assert response.status_code == 200
    assert response.json()["title"] == "Equivariance"
    assert response.json()["content"].startswith("# Equivariance")
    assert client.get("/api/wiki/missing").status_code == 404


def test_index_loads_katex_from_local_static_assets(tmp_path: Path):
    settings = Settings(
        wiki_path=make_wiki(tmp_path),
        agy_bin="agy-test",
        timeout_seconds=60,
        model="",
    )
    client = TestClient(create_app(settings))

    response = client.get("/")

    assert response.status_code == 200
    assert "/static/vendor/katex/katex.min.css" in response.text
    assert "/static/vendor/katex/katex.min.js" in response.text
    assert 'id="engine"' in response.text
    assert 'value="opencode"' in response.text
    assert 'value="codex"' in response.text
    assert 'id="viewer-resizer"' in response.text
    assert 'role="separator"' in response.text
    assert 'id="attach-pdf"' in response.text
    assert 'id="pdf-input"' in response.text
    assert 'id="attachment-tray"' in response.text
    assert 'id="agy-setup"' in response.text
    assert 'id="start-agy-login"' in response.text
    assert 'id="complete-agy-login"' in response.text
    assert client.get("/static/vendor/katex/katex.min.js").status_code == 200


def test_pdf_upload_is_temporary_and_injected_into_both_engines(
    tmp_path: Path,
    monkeypatch,
):
    settings = Settings(
        wiki_path=make_wiki(tmp_path),
        agy_bin="agy-test",
        timeout_seconds=60,
        model="",
        opencode_bin="opencode-test",
        opencode_model="ollama/gemma4:31b",
    )
    captured_prompts = []

    def fake_extract(_data, filename):
        return PdfAttachment(
            attachment_id="attachment-1",
            filename=filename,
            page_count=3,
            character_count=80,
            chunks=(
                PdfChunk(2, "MACE predicts atomic energies with message passing."),
            ),
        )

    def fake_run(**kwargs):
        captured_prompts.append(kwargs["prompt"])
        return "O PDF descreve o MACE [PDF: paper.pdf, p. 2]."

    monkeypatch.setattr(
        app_module,
        "resolve_executable",
        lambda command: f"/bin/{command}",
    )
    monkeypatch.setattr(app_module, "extract_pdf_attachment", fake_extract)
    monkeypatch.setattr(app_module, "run_antigravity", fake_run)
    monkeypatch.setattr(app_module, "run_opencode", fake_run)
    monkeypatch.setattr(app_module, "run_codex", fake_run)
    monkeypatch.setattr(app_module, "codex_authenticated", lambda _: True)
    client = TestClient(create_app(settings))

    upload = client.post(
        "/api/attachments",
        data={"session_id": "session_alpha"},
        files={"file": ("paper.pdf", b"%PDF-1.7 fake", "application/pdf")},
    )

    assert upload.status_code == 201
    assert upload.json()["id"] == "attachment-1"
    for engine in ("antigravity", "opencode", "codex"):
        response = client.post(
            "/api/chat",
            json={
                "message": "Como o MACE prediz energia?",
                "history": [],
                "engine": engine,
                "session_id": "session_alpha",
                "attachment_ids": ["attachment-1"],
            },
        )
        assert response.status_code == 200
        assert response.json()["attachment_sources"] == [
            {"id": "attachment-1", "filename": "paper.pdf", "pages": [2]}
        ]

    assert len(captured_prompts) == 3
    assert all("[PDF: paper.pdf, p. 2]" in prompt for prompt in captured_prompts)
    assert all("MACE predicts atomic energies" in prompt for prompt in captured_prompts)

    cleared = client.delete("/api/sessions/session_alpha/attachments")
    assert cleared.status_code == 200
    expired = client.post(
        "/api/chat",
        json={
            "message": "Repita.",
            "session_id": "session_alpha",
            "attachment_ids": ["attachment-1"],
        },
    )
    assert expired.status_code == 400


def test_attachment_ids_require_a_session(tmp_path: Path, monkeypatch):
    settings = Settings(
        wiki_path=make_wiki(tmp_path),
        agy_bin="agy-test",
        timeout_seconds=60,
        model="",
    )
    monkeypatch.setattr(app_module, "resolve_executable", lambda _: "/bin/agy-test")
    client = TestClient(create_app(settings))

    response = client.post(
        "/api/chat",
        json={"message": "Pergunta", "attachment_ids": ["attachment-1"]},
    )
    stream_response = client.post(
        "/api/chat/stream",
        json={"message": "Pergunta", "attachment_ids": ["attachment-1"]},
    )

    assert response.status_code == 400
    assert stream_response.status_code == 400
