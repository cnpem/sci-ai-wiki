from pathlib import Path

from wiki_chat import WikiIndex, WikiTools, build_context


def make_wiki(tmp_path: Path) -> Path:
    wiki = tmp_path / "wiki"
    (wiki / "models").mkdir(parents=True)
    (wiki / "concepts").mkdir()
    (wiki / "index.md").write_text(
        "# Wiki Index\n\n- [[mace]] — equivariant model\n"
        "- [[nequip]] — E(3) model\n",
        encoding="utf-8",
    )
    (wiki / "models" / "mace.md").write_text(
        "# MACE\n\nHigher-order equivariant message passing.",
        encoding="utf-8",
    )
    (wiki / "models" / "nequip.md").write_text(
        "# NequIP\n\nDeep E(3)-equivariant neural network.",
        encoding="utf-8",
    )
    (wiki / "concepts" / "quaternions.md").write_text(
        "# Quaternions\n\nRotations in three dimensions.",
        encoding="utf-8",
    )
    return tmp_path


def test_search_prioritizes_relevant_pages_and_includes_index(tmp_path: Path):
    index = WikiIndex(make_wiki(tmp_path))

    pages = index.search("Compare MACE e NequIP")
    ids = [page.page_id for page in pages]

    assert ids[:2] == ["mace", "nequip"]
    assert "index" in ids
    assert "quaternions" not in ids


def test_search_falls_back_to_overview_or_index(tmp_path: Path):
    index = WikiIndex(make_wiki(tmp_path))

    pages = index.search("termo completamente ausente")

    assert [page.page_id for page in pages] == ["index"]


def test_context_has_explicit_page_boundaries(tmp_path: Path):
    index = WikiIndex(make_wiki(tmp_path))
    page = index.by_id["mace"]

    context = build_context([page])

    assert '<wiki-page id="mace" path="wiki/models/mace.md">' in context
    assert context.endswith("</wiki-page>")


def test_agent_tools_list_search_and_read_files(tmp_path: Path):
    tools = WikiTools(make_wiki(tmp_path))

    listed = tools.list_wiki_files("wiki/models")
    searched = tools.search_wiki("MACE")
    read = tools.read_wiki_file("wiki/models/mace.md")

    assert "wiki/models/mace.md" in listed["files"]
    assert searched["results"][0]["id"] == "mace"
    assert "Higher-order equivariant" in read["content"]
    assert any(page.page_id == "mace" for page in tools.sources())


def test_agent_tools_block_path_traversal(tmp_path: Path):
    tools = WikiTools(make_wiki(tmp_path))

    result = tools.read_wiki_file("../secret.md")

    assert "error" in result
    assert "fora da raiz" in result["error"]
