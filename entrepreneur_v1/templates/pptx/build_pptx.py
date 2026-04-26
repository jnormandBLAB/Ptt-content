"""Idempotent PPTX builder for business_sober_v1 / entrepreneur_v1.

Reads master.json + a context dict, emits a single board slide
(situation + 3 risks + 3 levers + recommendation) on a 16:9 canvas.
Same input -> identical .pptx bytes.

Usage:
    python build_pptx.py --context fixture.json --out board_slide.pptx

Expected context:
    {
      "topic":           "...",
      "date":            "26.04.2026",
      "classification":  "BOARD-RESTRICTED",
      "situation":       "...",
      "risks":           [{"id": "R01", "title": "...", "chf_value_text": "CHF 4.2M"}, ...],
      "levers":          [{"id": "L01", "title": "...", "timeline": "Q3", "cost_chf_text": "CHF 280k"}, ...],
      "recommendation":  "...",
      "audit_url":       "...",
      "ekb_version":     "..."
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
        "python-pptx is required to build the business_sober_v1 PPTX kit. "
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
    p.alignment = {"right": PP_ALIGN.RIGHT, "center": PP_ALIGN.CENTER}.get(align, PP_ALIGN.LEFT)
    run = p.add_run()
    run.text = text
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = _hex_to_rgb(color_hex)
    if leading is not None:
        p.line_spacing = leading


def _add_filled_rect(slide, *, x_in, y_in, w_in, h_in, fill_hex: str) -> Any:
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


def build(context: dict, master: dict, out_path: Path) -> None:
    """Render the board slide to ``out_path``."""
    layout = master["layouts"]["board_slide"]
    colors = master["theme"]["colors"]
    fonts  = master["theme"]["fonts"]

    prs = Presentation()
    prs.slide_width  = Emu(master["slide_size"]["width_emu"])
    prs.slide_height = Emu(master["slide_size"]["height_emu"])

    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Background
    _add_filled_rect(slide, x_in=0, y_in=0,
                     w_in=master["slide_size"]["width_in"],
                     h_in=master["slide_size"]["height_in"],
                     fill_hex=colors["bg_paper"])

    # Header brand
    r = layout["regions"]["header_brand"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame, "PTT  ·  BOARD MEMO",
              font_name=fonts["heading"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], bold=True)

    # Classification badge
    r = layout["regions"]["header_classification"]
    _add_filled_rect(slide, x_in=r["x_in"], y_in=r["y_in"],
                     w_in=r["w_in"], h_in=r["h_in"],
                     fill_hex=colors[r["fill"]])
    tb = _add_textbox(slide, x_in=r["x_in"] + 0.05, y_in=r["y_in"] + 0.04,
                      w_in=r["w_in"] - 0.10, h_in=r["h_in"] - 0.08)
    _set_text(tb.text_frame, context.get("classification", "BOARD-RESTRICTED"),
              font_name=fonts["heading"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], bold=True, align="center")

    # Date
    r = layout["regions"]["header_date"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame, context.get("date", "—"),
              font_name=fonts["body"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], align="right")

    # Title
    r = layout["regions"]["title"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame, context.get("topic", "—"),
              font_name=fonts["heading"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], bold=True,
              leading=r.get("leading"))

    # Header rule
    r = layout["regions"]["rule_under_header"]
    _add_filled_rect(slide, x_in=r["x_in"], y_in=r["y_in"],
                     w_in=r["w_in"], h_in=r["h_in"],
                     fill_hex=colors[r["fill"]])

    # Situation block
    r_label = layout["regions"]["situation_label"]
    tb = _add_textbox(slide, x_in=r_label["x_in"], y_in=r_label["y_in"],
                      w_in=r_label["w_in"], h_in=r_label["h_in"])
    _set_text(tb.text_frame, "LAGE",
              font_name=fonts["heading"], size_pt=r_label["size_pt"],
              color_hex=colors[r_label["color"]], bold=True)

    r = layout["regions"]["situation_panel"]
    _add_filled_rect(slide, x_in=r["x_in"], y_in=r["y_in"],
                     w_in=r["w_in"], h_in=r["h_in"],
                     fill_hex=colors[r["fill"]])
    _add_filled_rect(slide, x_in=r["x_in"], y_in=r["y_in"],
                     w_in=0.04, h_in=r["h_in"],
                     fill_hex=colors[r["border_left"]["color"]])
    r_text = layout["regions"]["situation_text"]
    tb = _add_textbox(slide, x_in=r_text["x_in"], y_in=r_text["y_in"],
                      w_in=r_text["w_in"], h_in=r_text["h_in"])
    _set_text(tb.text_frame, context.get("situation", "—"),
              font_name=fonts["body"], size_pt=r_text["size_pt"],
              color_hex=colors[r_text["color"]], leading=r_text.get("leading"))

    # Risk + Lever band labels
    for label_key, text in [("risks_label", "STRATEGISCHE RISIKEN"),
                             ("levers_label", "MITIGATIONSHEBEL")]:
        r = layout["regions"][label_key]
        tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
        _set_text(tb.text_frame, text,
                  font_name=fonts["heading"], size_pt=r["size_pt"],
                  color_hex=colors[r["color"]], bold=True)

    # Risk tiles (3)
    band = layout["regions"]["risk_band"]
    risks = (context.get("risks") or [])[:3]
    while len(risks) < 3:
        risks.append({"id": "—", "title": "—", "chf_value_text": "—"})
    for i, risk in enumerate(risks):
        x = band["x_first_in"] + i * (band["tile_w_in"] + band["tile_gap_in"])
        # Top rule
        _add_filled_rect(slide, x_in=x, y_in=band["y_in"],
                         w_in=band["tile_w_in"], h_in=0.04,
                         fill_hex=colors["navy"])
        # Tile body
        _add_filled_rect(slide, x_in=x, y_in=band["y_in"] + 0.04,
                         w_in=band["tile_w_in"], h_in=band["h_in"] - 0.04,
                         fill_hex=colors["white"])

        tb = _add_textbox(slide, x_in=x + 0.10, y_in=band["y_in"] + 0.10,
                          w_in=band["tile_w_in"] - 0.20, h_in=0.25)
        _set_text(tb.text_frame, risk.get("id", "—"),
                  font_name=fonts["heading"], size_pt=band["id"]["size_pt"],
                  color_hex=colors[band["id"]["color"]], bold=True)

        tb = _add_textbox(slide, x_in=x + 0.10, y_in=band["y_in"] + 0.34,
                          w_in=band["tile_w_in"] - 0.20, h_in=0.40)
        _set_text(tb.text_frame, risk.get("title", "—"),
                  font_name=fonts["heading"], size_pt=band["title"]["size_pt"],
                  color_hex=colors[band["title"]["color"]], bold=True)

        tb = _add_textbox(slide, x_in=x + 0.10, y_in=band["y_in"] + 0.74,
                          w_in=band["tile_w_in"] - 0.20, h_in=0.30)
        _set_text(tb.text_frame, risk.get("chf_value_text", "—"),
                  font_name=fonts["numeric"], size_pt=band["chf"]["size_pt"],
                  color_hex=colors[band["chf"]["color"]], bold=True)

    # Lever tiles (3)
    band = layout["regions"]["lever_band"]
    levers = (context.get("levers") or [])[:3]
    while len(levers) < 3:
        levers.append({"id": "—", "title": "—", "timeline": "—", "cost_chf_text": "—"})
    for i, lev in enumerate(levers):
        x = band["x_first_in"] + i * (band["tile_w_in"] + band["tile_gap_in"])
        # Left rule
        _add_filled_rect(slide, x_in=x, y_in=band["y_in"],
                         w_in=0.04, h_in=band["h_in"],
                         fill_hex=colors["navy"])
        # Tile body
        _add_filled_rect(slide, x_in=x + 0.04, y_in=band["y_in"],
                         w_in=band["tile_w_in"] - 0.04, h_in=band["h_in"],
                         fill_hex=colors["panel"])

        tb = _add_textbox(slide, x_in=x + 0.14, y_in=band["y_in"] + 0.10,
                          w_in=band["tile_w_in"] - 0.20, h_in=0.25)
        _set_text(tb.text_frame, lev.get("id", "—"),
                  font_name=fonts["heading"], size_pt=band["id"]["size_pt"],
                  color_hex=colors[band["id"]["color"]], bold=True)

        tb = _add_textbox(slide, x_in=x + 0.14, y_in=band["y_in"] + 0.34,
                          w_in=band["tile_w_in"] - 0.20, h_in=0.40)
        _set_text(tb.text_frame, lev.get("title", "—"),
                  font_name=fonts["heading"], size_pt=band["title"]["size_pt"],
                  color_hex=colors[band["title"]["color"]], bold=True)

        tb = _add_textbox(slide, x_in=x + 0.14, y_in=band["y_in"] + 0.74,
                          w_in=band["tile_w_in"] - 0.20, h_in=0.30)
        meta_text = f"{lev.get('timeline', '—')}  |  {lev.get('cost_chf_text', '—')}"
        _set_text(tb.text_frame, meta_text,
                  font_name=fonts["numeric"], size_pt=band["meta"]["size_pt"],
                  color_hex=colors[band["meta"]["color"]])

    # Recommendation
    r = layout["regions"]["recommendation_band"]
    _add_filled_rect(slide, x_in=r["x_in"], y_in=r["y_in"],
                     w_in=r["w_in"], h_in=r["h_in"],
                     fill_hex=colors[r["fill"]])
    _add_filled_rect(slide, x_in=r["x_in"], y_in=r["y_in"],
                     w_in=0.05, h_in=r["h_in"],
                     fill_hex=colors[r["border_left"]["color"]])
    tb = _add_textbox(slide, x_in=r["x_in"] + 0.20, y_in=r["y_in"] + 0.10,
                      w_in=r["w_in"] - 0.30, h_in=0.25)
    _set_text(tb.text_frame, "EMPFEHLUNG AN DEN VR",
              font_name=fonts[r["label_font"]], size_pt=r["label_size_pt"],
              color_hex=colors[r["label_color"]], bold=True)
    tb = _add_textbox(slide, x_in=r["x_in"] + 0.20, y_in=r["y_in"] + 0.40,
                      w_in=r["w_in"] - 0.30, h_in=r["h_in"] - 0.50)
    _set_text(tb.text_frame, context.get("recommendation", "—"),
              font_name=fonts[r["font"]], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], bold=True)

    # Audit
    r = layout["regions"]["audit_footer"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame,
              f"Audit: {context.get('audit_url', '—')}    |    "
              f"Lizenz: all_rights_reserved    |    "
              f"EKB v{context.get('ekb_version', '—')}",
              font_name=fonts["body"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out_path)


def _cli() -> None:
    p = argparse.ArgumentParser(description="Build business_sober_v1 single board slide PPTX.")
    p.add_argument("--context", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--master", type=Path, default=MASTER_PATH)
    args = p.parse_args()

    context = json.loads(args.context.read_text(encoding="utf-8"))
    master  = json.loads(args.master.read_text(encoding="utf-8"))
    build(context, master, args.out)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    _cli()
