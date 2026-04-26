"""Idempotent PPTX builder for parliamentary_classic / policy_advisor_v1.

Reads master.json + a context dict, emits a multi-slide commission briefing
deck (title slide -> one_pager -> Q&A pairs -> legal citation slides).
Same input -> identical .pptx bytes (deterministic ordering, fixed
timestamps via python-pptx defaults).

Usage:
    python build_pptx.py --context fixture.json --out commission_brief.pptx

Expected context schema (all keys optional, sensible defaults applied):
    {
      "topic":        "...",
      "committee":    "CSP-N",
      "date":         "26.04.2026",
      "draft_label":  "DRAFT",
      "headline":     "...",
      "levers":       [{"title": "...", "actor": "...", "legal_ref": "..."}, ...],
      "recommendation": "...",
      "qa":           [{"question": "...", "answer": "...", "source": "..."}, ...],
      "legal_slides": [{"article_ref": "...", "verbatim": "...", "gloss": "..."}, ...],
      "audit_url":    "...",
      "license":      "all_rights_reserved",
      "ekb_version":  "..."
    }

Dependencies: python-pptx >= 0.6.21
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.enum.shapes import MSO_SHAPE
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "python-pptx is required to build the parliamentary_classic PPTX kit. "
        "Install it with: pip install 'python-pptx>=0.6.21'"
    ) from exc


HERE = Path(__file__).resolve().parent
MASTER_PATH = HERE / "master.json"


def _hex_to_rgb(hex6: str) -> RGBColor:
    return RGBColor.from_string(hex6.upper().lstrip("#"))


def _set_text(frame, text: str, *, font_name: str, size_pt: int,
              color_hex: str, bold: bool = False, italic: bool = False,
              align: str = "left", leading: float | None = None) -> None:
    frame.clear()
    p = frame.paragraphs[0]
    if align == "right":
        p.alignment = PP_ALIGN.RIGHT
    elif align == "center":
        p.alignment = PP_ALIGN.CENTER
    else:
        p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = text
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = _hex_to_rgb(color_hex)
    if leading is not None:
        p.line_spacing = leading


def _add_filled_rect(slide, *, x_in, y_in, w_in, h_in,
                     fill_hex: str) -> Any:
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(x_in), Inches(y_in), Inches(w_in), Inches(h_in),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = _hex_to_rgb(fill_hex)
    shape.line.fill.background()
    return shape


def _add_textbox(slide, *, x_in, y_in, w_in, h_in) -> Any:
    return slide.shapes.add_textbox(
        Inches(x_in), Inches(y_in), Inches(w_in), Inches(h_in),
    )


def _bg(slide, master) -> None:
    _add_filled_rect(
        slide,
        x_in=0, y_in=0,
        w_in=master["slide_size"]["width_in"],
        h_in=master["slide_size"]["height_in"],
        fill_hex=master["theme"]["colors"]["bg_paper"],
    )


def _build_title_slide(prs, master, context) -> None:
    layout = master["layouts"]["title_slide"]
    colors = master["theme"]["colors"]
    fonts  = master["theme"]["fonts"]

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(slide, master)

    r = layout["regions"]["draft_badge"]
    _add_filled_rect(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"],
                     fill_hex=colors[r["fill"]])
    tb = _add_textbox(slide, x_in=r["x_in"] + 0.05, y_in=r["y_in"] + 0.04,
                      w_in=r["w_in"] - 0.10, h_in=r["h_in"] - 0.08)
    _set_text(tb.text_frame, context.get("draft_label", "DRAFT").upper(),
              font_name=fonts["heading"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], bold=True, align="center")

    r = layout["regions"]["title"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame, context.get("topic", "—"),
              font_name=fonts["heading"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], bold=True,
              leading=r.get("leading"))

    r = layout["regions"]["subtitle"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame,
              f"Parlamentarische Notiz — {context.get('committee', '—')}",
              font_name=fonts["body"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], italic=True)

    r = layout["regions"]["rule"]
    _add_filled_rect(slide, x_in=r["x_in"], y_in=r["y_in"],
                     w_in=r["w_in"], h_in=r["h_in"],
                     fill_hex=colors[r["fill"]])

    r = layout["regions"]["meta"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    meta_text = (
        f"Adressat: {context.get('prepared_for', '—')}    "
        f"Autor: {context.get('prepared_by', '—')}    "
        f"Datum: {context.get('date', '—')}"
    )
    _set_text(tb.text_frame, meta_text,
              font_name=fonts["body"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]])


def _build_one_pager(prs, master, context) -> None:
    layout = master["layouts"]["one_pager"]
    colors = master["theme"]["colors"]
    fonts  = master["theme"]["fonts"]

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(slide, master)

    # Header
    r = layout["regions"]["header_brand"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame, "PTT  ·  POLITIKBERATUNG",
              font_name=fonts["heading"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], bold=True)

    r = layout["regions"]["header_topic"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame, context.get("topic", "—"),
              font_name=fonts["body"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], italic=True)

    r = layout["regions"]["header_date"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame, context.get("date", "—"),
              font_name=fonts["body"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], align="right")

    r = layout["regions"]["rule_under_header"]
    _add_filled_rect(slide, x_in=r["x_in"], y_in=r["y_in"],
                     w_in=r["w_in"], h_in=r["h_in"],
                     fill_hex=colors[r["fill"]])

    # Headline
    r = layout["regions"]["headline_label"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame, "ANALYSE",
              font_name=fonts["heading"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]])

    r = layout["regions"]["headline"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame, context.get("headline", "—"),
              font_name=fonts["body"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], leading=r.get("leading"))

    # Lever band
    band = layout["regions"]["lever_band"]
    levers = (context.get("levers") or [])[:3]
    while len(levers) < 3:
        levers.append({"title": "—", "actor": "—", "legal_ref": "—"})

    for i, lev in enumerate(levers):
        x = band["x_first_in"] + i * (band["tile_w_in"] + band["tile_gap_in"])
        # Gold left rule
        _add_filled_rect(slide, x_in=x, y_in=band["y_in"],
                         w_in=0.03, h_in=band["h_in"],
                         fill_hex=colors["gold"])
        # White tile
        _add_filled_rect(slide, x_in=x + 0.03, y_in=band["y_in"],
                         w_in=band["tile_w_in"] - 0.03, h_in=band["h_in"],
                         fill_hex=colors["white"])

        # Label = HEBEL N
        tb = _add_textbox(slide, x_in=x + 0.20, y_in=band["y_in"] + 0.15,
                          w_in=band["tile_w_in"] - 0.30, h_in=0.30)
        _set_text(tb.text_frame, f"HEBEL {i + 1}",
                  font_name=fonts["heading"], size_pt=band["label"]["size_pt"],
                  color_hex=colors[band["label"]["color"]], bold=True)

        # Title
        tb = _add_textbox(slide, x_in=x + 0.20, y_in=band["y_in"] + 0.50,
                          w_in=band["tile_w_in"] - 0.30, h_in=0.90)
        _set_text(tb.text_frame, str(lev.get("title", "—")),
                  font_name=fonts["body"], size_pt=band["title"]["size_pt"],
                  color_hex=colors[band["title"]["color"]], bold=True,
                  leading=band["title"].get("leading"))

        # Legal ref
        tb = _add_textbox(slide, x_in=x + 0.20, y_in=band["y_in"] + 1.50,
                          w_in=band["tile_w_in"] - 0.30, h_in=0.30)
        _set_text(tb.text_frame, f"« {lev.get('legal_ref', '—')} »",
                  font_name=fonts["body"], size_pt=band["legal"]["size_pt"],
                  color_hex=colors[band["legal"]["color"]], italic=True)

        # Actor
        tb = _add_textbox(slide, x_in=x + 0.20, y_in=band["y_in"] + 1.80,
                          w_in=band["tile_w_in"] - 0.30, h_in=0.30)
        _set_text(tb.text_frame, f"Akteur: {lev.get('actor', '—')}",
                  font_name=fonts["body"], size_pt=band["actor"]["size_pt"],
                  color_hex=colors[band["actor"]["color"]])

    # Recommendation
    r = layout["regions"]["recommendation_band"]
    _add_filled_rect(slide, x_in=r["x_in"], y_in=r["y_in"],
                     w_in=r["w_in"], h_in=r["h_in"],
                     fill_hex=colors[r["fill"]])
    _add_filled_rect(slide, x_in=r["x_in"], y_in=r["y_in"],
                     w_in=0.04, h_in=r["h_in"],
                     fill_hex=colors[r["border_left"]["color"]])
    tb = _add_textbox(slide, x_in=r["x_in"] + 0.20, y_in=r["y_in"] + 0.10,
                      w_in=r["w_in"] - 0.30, h_in=r["h_in"] - 0.20)
    _set_text(tb.text_frame,
              f"Empfehlung: {context.get('recommendation', '—')}",
              font_name=fonts["body"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], bold=True)

    # Audit
    _audit_footer(slide, layout["regions"]["audit_footer"], colors, fonts, context)


def _build_qa_slide(prs, master, context, *, idx: int, qa: dict) -> None:
    layout = master["layouts"]["qa_pair"]
    colors = master["theme"]["colors"]
    fonts  = master["theme"]["fonts"]

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(slide, master)

    r = layout["regions"]["q_num"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame, f"F{idx:02d}",
              font_name=fonts["heading"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], bold=True)

    r = layout["regions"]["question"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame, qa.get("question", "—"),
              font_name=fonts["body"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], bold=True,
              leading=r.get("leading"))

    r = layout["regions"]["answer"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame, qa.get("answer", "—"),
              font_name=fonts["body"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], leading=r.get("leading"))

    r = layout["regions"]["source"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame,
              f"claim: {qa.get('claim_id', '—')} · {qa.get('source', '—')}",
              font_name=fonts["body"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], italic=True)


def _build_legal_slide(prs, master, context, *, citation: dict) -> None:
    layout = master["layouts"]["legal_citation"]
    colors = master["theme"]["colors"]
    fonts  = master["theme"]["fonts"]

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(slide, master)

    r = layout["regions"]["label"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame, "RECHTSGRUNDLAGE",
              font_name=fonts["heading"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], bold=True)

    r = layout["regions"]["article_ref"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame, f"« {citation.get('article_ref', '—')} »",
              font_name=fonts["body"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], italic=True)

    r = layout["regions"]["rule_under_ref"]
    _add_filled_rect(slide, x_in=r["x_in"], y_in=r["y_in"],
                     w_in=r["w_in"], h_in=r["h_in"],
                     fill_hex=colors[r["fill"]])

    # Verbatim block
    r_label = layout["regions"]["verbatim_label"]
    tb = _add_textbox(slide, x_in=r_label["x_in"], y_in=r_label["y_in"],
                      w_in=r_label["w_in"], h_in=r_label["h_in"])
    _set_text(tb.text_frame, "WORTLAUT",
              font_name=fonts["heading"], size_pt=r_label["size_pt"],
              color_hex=colors[r_label["color"]])

    r = layout["regions"]["verbatim"]
    _add_filled_rect(slide, x_in=r["x_in"], y_in=r["y_in"],
                     w_in=r["w_in"], h_in=r["h_in"],
                     fill_hex=colors[r["fill"]])
    tb = _add_textbox(slide, x_in=r["x_in"] + r.get("padding_in", 0.2),
                      y_in=r["y_in"] + r.get("padding_in", 0.2),
                      w_in=r["w_in"] - 2 * r.get("padding_in", 0.2),
                      h_in=r["h_in"] - 2 * r.get("padding_in", 0.2))
    _set_text(tb.text_frame, citation.get("verbatim", "—"),
              font_name=fonts["body"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], italic=True,
              leading=r.get("leading"))

    # Gloss block
    r_label = layout["regions"]["gloss_label"]
    tb = _add_textbox(slide, x_in=r_label["x_in"], y_in=r_label["y_in"],
                      w_in=r_label["w_in"], h_in=r_label["h_in"])
    _set_text(tb.text_frame, "ANALYTISCHE NOTE",
              font_name=fonts["heading"], size_pt=r_label["size_pt"],
              color_hex=colors[r_label["color"]])

    r = layout["regions"]["gloss"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"],
                      w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame, citation.get("gloss", "—"),
              font_name=fonts["body"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], leading=r.get("leading"))

    _audit_footer(slide, layout["regions"]["audit_footer"], colors, fonts, context)


def _audit_footer(slide, r, colors, fonts, context) -> None:
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"],
                      w_in=r["w_in"], h_in=r["h_in"])
    _set_text(
        tb.text_frame,
        f"Audit: {context.get('audit_url', '—')}    |    "
        f"Lizenz: {context.get('license', 'all_rights_reserved')}    |    "
        f"EKB v{context.get('ekb_version', '—')}",
        font_name=fonts["body"], size_pt=r["size_pt"],
        color_hex=colors[r["color"]],
    )


def build(context: dict, master: dict, out_path: Path) -> None:
    """Render the full commission briefing deck to ``out_path``."""
    prs = Presentation()
    prs.slide_width  = Emu(master["slide_size"]["width_emu"])
    prs.slide_height = Emu(master["slide_size"]["height_emu"])

    # 1. Title
    _build_title_slide(prs, master, context)

    # 2. One-pager
    _build_one_pager(prs, master, context)

    # 3. Q&A pack (one slide per pair, capped at 15)
    qa_list = (context.get("qa") or [])[:15]
    for i, qa in enumerate(qa_list, start=1):
        _build_qa_slide(prs, master, context, idx=i, qa=qa)

    # 4. Legal citation slides
    legal_list = context.get("legal_slides") or []
    for citation in legal_list:
        _build_legal_slide(prs, master, context, citation=citation)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out_path)


def _cli() -> None:
    p = argparse.ArgumentParser(description="Build parliamentary_classic PPTX commission briefing deck.")
    p.add_argument("--context", type=Path, required=True,
                   help="JSON file with the deck context.")
    p.add_argument("--out", type=Path, required=True,
                   help="Destination .pptx path.")
    p.add_argument("--master", type=Path, default=MASTER_PATH,
                   help="Override master.json location.")
    args = p.parse_args()

    context = json.loads(args.context.read_text(encoding="utf-8"))
    master  = json.loads(args.master.read_text(encoding="utf-8"))
    build(context, master, args.out)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    _cli()
