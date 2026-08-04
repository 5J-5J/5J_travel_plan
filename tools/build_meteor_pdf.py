from __future__ import annotations

import html
import os
import re
from pathlib import Path
from typing import Iterable, List

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_MD = ROOT / "英仙座流星雨内蒙机位调研.md"
OUTPUT_DIR = ROOT / "output" / "pdf"
TMP_DIR = ROOT / "tmp" / "pdfs"
OUTPUT_PDF = OUTPUT_DIR / "英仙座流星雨内蒙机位调研.pdf"

PAGE_W, PAGE_H = A4
LEFT = RIGHT = 17 * mm
TOP = 17 * mm
BOTTOM = 16 * mm
AVAILABLE_W = PAGE_W - LEFT - RIGHT


def register_fonts() -> tuple[str, str]:
    font_candidates = [
        Path(r"C:\Windows\Fonts\msyh.ttc"),
        Path(r"C:\Windows\Fonts\simsun.ttc"),
        Path(r"C:\Windows\Fonts\simhei.ttf"),
    ]
    bold_candidates = [
        Path(r"C:\Windows\Fonts\msyhbd.ttc"),
        Path(r"C:\Windows\Fonts\simhei.ttf"),
        Path(r"C:\Windows\Fonts\msyh.ttc"),
    ]

    base_font = next((p for p in font_candidates if p.exists()), None)
    bold_font = next((p for p in bold_candidates if p.exists()), None)
    if not base_font:
        raise RuntimeError("No Chinese font found under C:\\Windows\\Fonts")

    pdfmetrics.registerFont(TTFont("DocCJK", str(base_font)))
    if bold_font:
        pdfmetrics.registerFont(TTFont("DocCJKBold", str(bold_font)))
    else:
        pdfmetrics.registerFont(TTFont("DocCJKBold", str(base_font)))
    return "DocCJK", "DocCJKBold"


FONT, FONT_BOLD = register_fonts()


def normalize_text(text: str) -> str:
    return (
        text.replace("\u2010", "-")
        .replace("\u2011", "-")
        .replace("\u2012", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2212", "-")
    )


def escape(text: str) -> str:
    return html.escape(normalize_text(text), quote=False)


def apply_inline_markdown(segment: str) -> str:
    segment = escape(segment)
    segment = re.sub(
        r"`([^`]+)`",
        lambda m: f'<font name="{FONT}" backColor="#EEF2F7">{html.escape(m.group(1), quote=False)}</font>',
        segment,
    )
    segment = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", segment)
    return segment


def inline_to_rl(text: str) -> str:
    text = normalize_text(text)
    pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    out: List[str] = []
    last = 0
    for match in pattern.finditer(text):
        out.append(apply_inline_markdown(text[last : match.start()]))
        label = apply_inline_markdown(match.group(1))
        url = html.escape(match.group(2), quote=True)
        out.append(f'<link href="{url}"><font color="#2563EB">{label}</font></link>')
        last = match.end()
    out.append(apply_inline_markdown(text[last:]))
    return "".join(out)


styles = getSampleStyleSheet()

TITLE = ParagraphStyle(
    "TitleCJK",
    parent=styles["Title"],
    fontName=FONT_BOLD,
    fontSize=20,
    leading=26,
    textColor=colors.HexColor("#0F172A"),
    spaceAfter=10,
    alignment=TA_LEFT,
    wordWrap="CJK",
)

H2 = ParagraphStyle(
    "H2CJK",
    parent=styles["Heading2"],
    fontName=FONT_BOLD,
    fontSize=14,
    leading=18,
    textColor=colors.HexColor("#123A5A"),
    spaceBefore=12,
    spaceAfter=7,
    borderPadding=(0, 0, 4, 0),
    wordWrap="CJK",
)

H3 = ParagraphStyle(
    "H3CJK",
    parent=styles["Heading3"],
    fontName=FONT_BOLD,
    fontSize=11.5,
    leading=15,
    textColor=colors.HexColor("#1F2937"),
    spaceBefore=8,
    spaceAfter=5,
    wordWrap="CJK",
)

BODY = ParagraphStyle(
    "BodyCJK",
    parent=styles["BodyText"],
    fontName=FONT,
    fontSize=9.5,
    leading=14.2,
    textColor=colors.HexColor("#111827"),
    spaceAfter=5,
    wordWrap="CJK",
)

BODY_SMALL = ParagraphStyle(
    "BodySmallCJK",
    parent=BODY,
    fontSize=8.5,
    leading=12.2,
    textColor=colors.HexColor("#334155"),
)

BULLET = ParagraphStyle(
    "BulletCJK",
    parent=BODY,
    leftIndent=13,
    firstLineIndent=-7,
    spaceAfter=3.5,
    bulletIndent=0,
)

CAPTION = ParagraphStyle(
    "CaptionCJK",
    parent=BODY_SMALL,
    alignment=TA_CENTER,
    textColor=colors.HexColor("#64748B"),
    spaceBefore=2,
    spaceAfter=8,
)

TABLE_CELL = ParagraphStyle(
    "TableCellCJK",
    parent=BODY_SMALL,
    fontSize=7.4,
    leading=10,
    wordWrap="CJK",
)

TABLE_HEAD = ParagraphStyle(
    "TableHeadCJK",
    parent=TABLE_CELL,
    fontName=FONT_BOLD,
    textColor=colors.white,
)


def para(text: str, style=BODY) -> Paragraph:
    return Paragraph(inline_to_rl(text), style)


def split_table_row(line: str) -> list[str]:
    raw = line.strip()
    if raw.startswith("|"):
        raw = raw[1:]
    if raw.endswith("|"):
        raw = raw[:-1]
    return [cell.strip() for cell in raw.split("|")]


def is_table_separator(line: str) -> bool:
    cells = split_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", c.strip()) for c in cells)


def build_table(lines: list[str]) -> Table:
    rows = [split_table_row(line) for line in lines if line.strip()]
    if len(rows) >= 2 and is_table_separator(lines[1]):
        header = rows[0]
        body = rows[2:]
    else:
        header = rows[0]
        body = rows[1:]

    max_cols = max(len(r) for r in [header] + body)
    fixed_rows = []
    for idx, row in enumerate([header] + body):
        row = row + [""] * (max_cols - len(row))
        style = TABLE_HEAD if idx == 0 else TABLE_CELL
        fixed_rows.append([Paragraph(inline_to_rl(cell), style) for cell in row])

    if max_cols >= 8:
        col_widths = [24, 73, 45, 85, 63, 62, 42, AVAILABLE_W - 394]
    elif max_cols == 4:
        col_widths = [AVAILABLE_W * 0.20, AVAILABLE_W * 0.28, AVAILABLE_W * 0.25, AVAILABLE_W * 0.27]
    else:
        col_widths = [AVAILABLE_W / max_cols] * max_cols

    table = Table(fixed_rows, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A5F")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
                ("FONTNAME", (0, 1), (-1, -1), FONT),
                ("FONTSIZE", (0, 0), (-1, -1), 7.4),
                ("LEADING", (0, 0), (-1, -1), 9.5),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ]
        )
    )
    return table


def prepare_image(source: Path, idx: int, w_pt: float, h_pt: float, is_map: bool) -> Path:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    out = TMP_DIR / f"md_image_{idx:02d}.jpg"
    dpi = 220 if is_map else 180
    target_w = max(1, int(w_pt / 72 * dpi))
    target_h = max(1, int(h_pt / 72 * dpi))
    with PILImage.open(source) as img:
        img = img.convert("RGB")
        img = img.resize((target_w, target_h), PILImage.Resampling.LANCZOS)
        img.save(out, "JPEG", quality=88 if is_map else 84, optimize=True, progressive=True)
    return out


def image_flowable(rel_path: str, alt: str, idx: int):
    source = (ROOT / rel_path).resolve()
    if not source.exists():
        return para(f"[图片缺失：{rel_path}]", BODY_SMALL)

    with PILImage.open(source) as img:
        w_px, h_px = img.size

    is_map = any(token in alt for token in ["地图", "机位", "巧摄"])
    max_w = AVAILABLE_W * (0.76 if is_map else 0.70)
    max_h = 270 if is_map else 215
    scale = min(max_w / w_px, max_h / h_px, 1.0)
    w_pt = w_px * scale
    h_pt = h_px * scale

    image_path = prepare_image(source, idx, w_pt, h_pt, is_map)
    image = Image(str(image_path), width=w_pt, height=h_pt, hAlign="CENTER")
    caption = Paragraph(escape(alt), CAPTION)
    return KeepTogether([Spacer(1, 3), image, caption])


def flush_paragraph(buffer: list[str], story: list) -> None:
    if buffer:
        story.append(para(" ".join(x.strip() for x in buffer if x.strip())))
        buffer.clear()


def markdown_to_story(markdown: str) -> list:
    story: list = []
    lines = markdown.splitlines()
    i = 0
    paragraph_buffer: list[str] = []
    image_idx = 0

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped:
            flush_paragraph(paragraph_buffer, story)
            i += 1
            continue

        if stripped.startswith("# "):
            flush_paragraph(paragraph_buffer, story)
            story.append(Paragraph(inline_to_rl(stripped[2:].strip()), TITLE))
            story.append(Spacer(1, 4))
            i += 1
            continue

        if stripped.startswith("## "):
            flush_paragraph(paragraph_buffer, story)
            text = stripped[3:].strip()
            if text == "资料来源":
                story.append(PageBreak())
            story.append(Paragraph(inline_to_rl(text), H2))
            i += 1
            continue

        if stripped.startswith("### "):
            flush_paragraph(paragraph_buffer, story)
            story.append(Paragraph(inline_to_rl(stripped[4:].strip()), H3))
            i += 1
            continue

        image_match = re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)", stripped)
        if image_match:
            flush_paragraph(paragraph_buffer, story)
            image_idx += 1
            story.append(image_flowable(image_match.group(2), image_match.group(1), image_idx))
            i += 1
            continue

        if stripped.startswith("|") and i + 1 < len(lines) and is_table_separator(lines[i + 1]):
            flush_paragraph(paragraph_buffer, story)
            table_lines = [line]
            i += 1
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].rstrip())
                i += 1
            story.append(build_table(table_lines))
            story.append(Spacer(1, 8))
            continue

        bullet_match = re.match(r"^[-*]\s+(.*)$", stripped)
        if bullet_match:
            flush_paragraph(paragraph_buffer, story)
            story.append(Paragraph(inline_to_rl(bullet_match.group(1)), BULLET, bulletText="•"))
            i += 1
            continue

        numbered_match = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if numbered_match:
            flush_paragraph(paragraph_buffer, story)
            story.append(
                Paragraph(
                    inline_to_rl(numbered_match.group(2)),
                    BULLET,
                    bulletText=f"{numbered_match.group(1)}.",
                )
            )
            i += 1
            continue

        paragraph_buffer.append(stripped)
        i += 1

    flush_paragraph(paragraph_buffer, story)
    return story


def draw_page(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT, 8)
    canvas.setFillColor(colors.HexColor("#64748B"))
    footer = f"{doc.page}  |  2026 英仙座流星雨内蒙古机位调研"
    canvas.drawRightString(PAGE_W - RIGHT, 9 * mm, footer)
    canvas.setStrokeColor(colors.HexColor("#E2E8F0"))
    canvas.setLineWidth(0.35)
    canvas.line(LEFT, 13 * mm, PAGE_W - RIGHT, 13 * mm)
    canvas.restoreState()


def build_pdf() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    markdown = SOURCE_MD.read_text(encoding="utf-8")
    story = markdown_to_story(markdown)

    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        rightMargin=RIGHT,
        leftMargin=LEFT,
        topMargin=TOP,
        bottomMargin=BOTTOM,
        title="2026 英仙座流星雨内蒙古机位调研",
        author="Codex",
    )
    doc.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
    return OUTPUT_PDF


if __name__ == "__main__":
    pdf = build_pdf()
    print(pdf)
