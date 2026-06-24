import pytest
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
    
    # Assert that CSS styles are inlined as style attributes using the actual compressed format returned by premailer
    assert "color:#111" in inlined_html
    assert "font-size:24px" in inlined_html
    assert "border-bottom:2px solid #eaeaea" in inlined_html
    assert "background-color:#f9f9f9" in inlined_html or "background-color: #f9f9f9" in inlined_html
    assert "border:1px solid #ddd" in inlined_html or "border: 1px solid #ddd" in inlined_html
