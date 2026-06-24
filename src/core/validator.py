import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

import markdown
from premailer import transform

logger = logging.getLogger(__name__)

DEFAULT_CSS = """
body {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    color: #333333;
    line-height: 1.6;
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
}
h1 {
    color: #111111;
    font-size: 24px;
    border-bottom: 2px solid #eaeaea;
    padding-bottom: 8px;
}
h2 {
    color: #222222;
    font-size: 20px;
    margin-top: 24px;
}
p {
    font-size: 16px;
    margin-bottom: 16px;
}
blockquote {
    background-color: #f9f9f9;
    border-left: 4px solid #0076ff;
    margin: 0 0 16px 0;
    padding: 10px 20px;
    font-style: italic;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
}
th, td {
    border: 1px solid #dddddd;
    text-align: left;
    padding: 8px;
    font-size: 14px;
}
th {
    background-color: #f2f2f2;
    font-weight: bold;
}
"""


def validate_essay_seniority(essay: str) -> list[str]:
    """
    Validates essay according to the Seniority Checklist:
    1. Word count between 1000 and 2500 words.
    2. Zero fluff (no 'revolutionary', 'incredible', etc.).
    3. Metrics/numbers present.
    4. Official documentation link present.
    5. Trade-offs table present with correct column headers.
    """
    errors = []

    words = essay.split()
    word_count = len(words)
    if word_count < 1000:
        errors.append(f"Word count ({word_count}) is below 1000 words.")
    elif word_count > 2500:
        errors.append(f"Word count ({word_count}) exceeds 2500 words.")

    fluff_words = ["revolutionary", "incredible", "amazing", "fantastic", "groundbreaking", "revolucionário", "incrível", "fantástico", "espetacular"]
    found_fluff = [f for f in fluff_words if re.search(r'\b' + re.escape(f) + r'\b', essay, re.IGNORECASE)]
    if found_fluff:
        errors.append(f"Contains fluff adjectives: {found_fluff}")

    if not re.search(r'\b\d+(\.\d+)?%?\b', essay):
        errors.append("Lacks concrete metrics or numbers.")

    if not re.search(r'https?://[^\s]+', essay):
        errors.append("Lacks official documentation reference links.")

    required_columns = ["Prós", "Contras", "Decisão Técnica"]
    has_table = all(column in essay for column in required_columns)
    if not has_table:
        errors.append("Lacks Pros/Cons/Decision technical table.")

    return errors


def _write_text_file(path: str, content: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def _write_json_file(path: str, payload: dict[str, object]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def inline_css_newsletter(
    markdown_content: str,
    custom_css: str = DEFAULT_CSS,
    *,
    raw_markdown_path: str | None = None,
    metadata_path: str | None = None,
) -> str:
    """
    Converts markdown content to HTML, wraps it with styles,
    and runs premailer to inline styles for maximum email compatibility.
    If the inline step fails, saves the raw Markdown and metadata for operator triage.
    """
    try:
        html_body = markdown.markdown(markdown_content, extensions=["tables"])
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Newsletter Edition</title>
    <style>
    {custom_css}
    </style>
</head>
<body>
{html_body}
</body>
</html>
"""
        return transform(full_html)
    except Exception as exc:  # pragma: no cover - exercised through failure-mode tests
        logger.critical("Newsletter inliner failed; preserving raw markdown", exc_info=True)

        if raw_markdown_path:
            _write_text_file(raw_markdown_path, markdown_content)

        if metadata_path:
            _write_json_file(
                metadata_path,
                {
                    "status": "critical",
                    "stage": "html_inliner",
                    "error": str(exc),
                    "markdown_saved": bool(raw_markdown_path),
                    "markdown_length": len(markdown_content),
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                },
            )

        return markdown_content
