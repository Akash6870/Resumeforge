from __future__ import annotations

import io
import logging
import re
from dataclasses import dataclass
from html import escape
from typing import List, Optional

from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

logger = logging.getLogger(__name__)


@dataclass
class ResumeContext:
    full_name:            str
    email:                str
    phone:                str
    location:             str
    linkedin_url:         str
    portfolio_url:        str
    professional_summary: str
    work_experience:      str
    education:            str
    skills:               str
    certifications:       str
    projects:             str
    awards:               str
    job_title:            str = ""
    company_name:         str = ""
    keywords_to_highlight: Optional[List[str]] = None


_ATS_PRINT_CSS = """
@page {
    size: A4;
    margin: 18mm 20mm 18mm 20mm;
}
body {
    font-family: 'Georgia', serif;
    font-size: 10.5pt;
    line-height: 1.45;
    color: #1a1a1a;
}
h1 { font-size: 20pt; margin: 0 0 2pt; }
h2 {
    font-size: 11pt;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    border-bottom: 1.5pt solid #1a1a1a;
    margin: 10pt 0 4pt;
    padding-bottom: 1pt;
}
h3 { font-size: 10.5pt; margin: 6pt 0 0; }
p, ul { margin: 2pt 0; }
ul { padding-left: 14pt; }
li { margin-bottom: 1.5pt; }
a { color: #1a1a1a; text-decoration: none; }
.contact-line { font-size: 9pt; color: #444; margin-top: 3pt; }
.highlight { font-weight: bold; }
section { page-break-inside: avoid; }
"""


def _highlight_keywords(text: str, keywords: List[str]) -> str:
    escaped = escape(text)
    for kw in sorted(keywords, key=len, reverse=True):
        pattern = re.compile(r"(?i)\b" + re.escape(kw) + r"\b")
        escaped = pattern.sub(
            lambda m: f'<strong class="highlight">{m.group(0)}</strong>',
            escaped,
        )
    return escaped


def compile_pdf(ctx: ResumeContext) -> bytes:
    keywords = ctx.keywords_to_highlight or []
    template_ctx = {
        "full_name":            ctx.full_name,
        "email":                ctx.email,
        "phone":                ctx.phone,
        "location":             ctx.location,
        "linkedin_url":         ctx.linkedin_url,
        "portfolio_url":        ctx.portfolio_url,
        "professional_summary": _highlight_keywords(ctx.professional_summary, keywords),
        "work_experience":      _highlight_keywords(ctx.work_experience, keywords),
        "education":            ctx.education,
        "skills":               _highlight_keywords(ctx.skills, keywords),
        "certifications":       ctx.certifications,
        "projects":             _highlight_keywords(ctx.projects, keywords),
        "awards":               ctx.awards,
        "job_title":            ctx.job_title,
        "company_name":         ctx.company_name,
    }
    logger.info("Rendering PDF for %s → %s", ctx.full_name, ctx.job_title)
    html_string = render_to_string("engine/ats_resume.html", template_ctx)
    font_config = FontConfiguration()
    base_css    = CSS(string=_ATS_PRINT_CSS, font_config=font_config)
    pdf_buffer  = io.BytesIO()
    HTML(string=html_string).write_pdf(
        pdf_buffer,
        stylesheets=[base_css],
        font_config=font_config,
        presentational_hints=True,
    )
    return pdf_buffer.getvalue()