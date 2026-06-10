"""Release metadata consistency checks."""

from __future__ import annotations

import json
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_manifest_version_matches_changelog_heading() -> None:
    root = _repo_root()
    manifest_path = root / "custom_components" / "digitransit" / "manifest.json"
    changelog_path = root / "CHANGELOG.md"

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    changelog = changelog_path.read_text(encoding="utf-8")

    version = manifest["version"]
    assert f"## [{version}]" in changelog


def test_changelog_has_unreleased_section() -> None:
    changelog = (_repo_root() / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [Unreleased]" in changelog
