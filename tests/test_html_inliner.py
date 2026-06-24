import json

import pytest

from src.core import validator as validator_module
from src.core.validator import inline_css_newsletter


def test_inline_css_newsletter_converts_markdown_and_inlines():
    markdown_content = """# Artigo Técnico
Este é um parágrafo.

> Um Staff insight super importante.

| Prós | Contras | Decisão Técnica |
| :--- | :--- | :--- |
| Alta Velocidade | Pouca Memória | Usar Redis |
"""

    inlined_html = inline_css_newsletter(markdown_content)

    assert "h1" in inlined_html
    assert "blockquote" in inlined_html
    assert "table" in inlined_html

    assert "color:#111" in inlined_html
    assert "font-size:24px" in inlined_html
    assert "border-bottom:2px solid #eaeaea" in inlined_html
    assert "background-color:#f9f9f9" in inlined_html or "background-color: #f9f9f9" in inlined_html
    assert "border:1px solid #ddd" in inlined_html or "border: 1px solid #ddd" in inlined_html


def test_inline_css_newsletter_persists_raw_markdown_and_metadata_on_failure(monkeypatch, tmp_path):
    def boom(*args, **kwargs):
        raise RuntimeError("premailer unavailable")

    monkeypatch.setattr(validator_module, "transform", boom)

    raw_markdown_path = tmp_path / "edition.md"
    metadata_path = tmp_path / "edition.metadata.json"
    markdown_content = """# Artigo Técnico\n\nConteúdo bruto da edição."""

    result = inline_css_newsletter(
        markdown_content,
        raw_markdown_path=str(raw_markdown_path),
        metadata_path=str(metadata_path),
    )

    assert result == markdown_content
    assert raw_markdown_path.read_text(encoding="utf-8") == markdown_content

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["status"] == "critical"
    assert metadata["stage"] == "html_inliner"
    assert metadata["markdown_saved"] is True
    assert "premailer unavailable" in metadata["error"]
