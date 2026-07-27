#!/usr/bin/env python3
"""Small, dependency-free checks for the documented SciAI Wiki format."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


FRONT_MATTER_MARKER = "---"
WIKI_LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")


def read_front_matter(path: Path) -> dict[str, Any]:
    """Read the YAML block using PyYAML, with a clear error when unavailable."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONT_MATTER_MARKER:
        return {}
    try:
        end = lines.index(FRONT_MATTER_MARKER, 1)
    except ValueError as exc:
        raise ValueError(f"{path}: front matter starts with --- but is not closed") from exc

    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - exercised by setup, not unit tests
        raise RuntimeError("PyYAML is required; run scripts/install_dependencies.sh") from exc

    data = yaml.safe_load("\n".join(lines[1:end]))
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: front matter must contain a YAML mapping")
    return data


def valid_author_name(value: Any) -> bool:
    """Return whether value follows the wiki's canonical full-name format."""
    if not isinstance(value, str):
        return False
    name = " ".join(value.split())
    if not name or "," in name or "[[" in name or "]]" in name:
        return False
    return len(name.split()) >= 2


def validate_author_fields(data: dict[str, Any], page_kind: str, path: Path) -> list[str]:
    errors: list[str] = []
    if page_kind == "paper":
        authors = data.get("authors")
        if not isinstance(authors, list) or not authors:
            return [f"{path}: 'authors' must be a non-empty list of full names"]
        for index, author in enumerate(authors, start=1):
            if not valid_author_name(author):
                errors.append(f"{path}: authors[{index}] is not a valid full name")
    elif page_kind == "author" and not valid_author_name(data.get("name")):
        errors.append(f"{path}: 'name' must be a full name such as 'Ada Lovelace'")
    return errors


def validate_wiki(root: Path) -> list[str]:
    """Validate author metadata in existing wiki pages; return objective errors only."""
    errors: list[str] = []
    for path in sorted((root / "wiki" / "papers").glob("*.md")):
        try:
            data = read_front_matter(path)
        except (RuntimeError, ValueError) as exc:
            errors.append(str(exc))
            continue
        errors.extend(validate_author_fields(data, "paper", path))
    for path in sorted((root / "wiki" / "authors").glob("*.md")):
        try:
            data = read_front_matter(path)
        except (RuntimeError, ValueError) as exc:
            errors.append(str(exc))
            continue
        errors.extend(validate_author_fields(data, "author", path))
    return errors


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validate SciAI Wiki author metadata.")
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    args = parser.parse_args()
    problems = validate_wiki(args.root.resolve())
    if problems:
        print("Validation failed:")
        print("\n".join(f"- {problem}" for problem in problems))
        raise SystemExit(1)
    print("Validation passed: no objective author-format errors found.")
