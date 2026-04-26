"""Idempotent PPTX builder for executive_dark_compact / federal_councillor_v1.

Reads master.json + a context dict, emits a single-slide 16:9 hero card
to disk. Same input -> identical .pptx bytes (deterministic ordering,
fixed timestamps).

Usage:
    python build_pptx.py --context fixture.json --out hero.pptx

Dependencies: python-pptx >= 0.6.21

This module imports nothing from src/ — it is a self-contained renderer
that the stakeholder adapter calls via subprocess or registry binding.
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
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
    from pptx.enum.shapes import MSO_SHAPE
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "python-pptx is required to build the executive_dark_compact PPTX kit. "
        "Install it with: pip install 'python-pptx>=0.6.21'"
    ) from exc


HERE = Path(__file__).resolve().parent
MASTER_PATH = HERE / "master.json"


def _hex_to_rgb(hex6: str) -> RGBColor:
    """Convert a 6-char hex string to a python-pptx RGBColor."""
    return RGBColor.from_string(hex6.upper().lstrip("#"))


def _set_text(frame, text: str, *, font_name: str, size_pt: int,
              color_hex: str, bold: bool = False, italic: bool = False,
              align: str = "left", leading: float | None = None) -> None:
    """Write text into a TextFrame with explicit run-level styling."""
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
        # Approximate line-height via paragraph space-before
        p.line_spacing = leading


def _add_filled_rect(slide, *, x_in, y_in, w_in, h_in,
                     fill_hex: str, line: bool = False) -> Any:
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(x_in), Inches(y_in), Inches(w_in), Inches(h_in),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = _hex_to_rgb(fill_hex)
    if not line:
        shape.line.fill.background()
    return shape


def _add_textbox(slide, *, x_in, y_in, w_in, h_in) -> Any:
    return slide.shapes.add_textbox(
        Inches(x_in), Inches(y_in), Inches(w_in), Inches(h_in),
    )


def build(context: dict, master: dict, out_path: Path) -> None:
    """Render the hero card slide to ``out_path``."""
    layout = master["layouts"]["hero_card"]
    theme  = master["theme"]
    colors = theme["colors"]
    fonts  = theme["fonts"]

    prs = Presentation()
    prs.slide_width  = Emu(master["slide_size"]["width_emu"])
    prs.slide_height = Emu(master["slide_size"]["height_emu"])

    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)

    # --- 1. Cream background ---
    _add_filled_rect(
        slide,
        x_in=0, y_in=0,
        w_in=master["slide_size"]["width_in"],
        h_in=master["slide_size"]["height_in"],
        fill_hex=colors["bg_paper"],
    )

    # --- 2. Header ---
    r = layout["regions"]["header_brand"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame, "PTT  ·  BUNDESRAT",
              font_name=fonts["heading"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], bold=True)

    r = layout["regions"]["header_topic"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame, context.get("topic", "—"),
              font_name=fonts["body"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], italic=True)

    r = layout["regions"]["header_date"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame, context.get("vote_date", "—"),
              font_name=fonts["body"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], align="right")

    # Header rule (1pt navy line)
    r = layout["regions"]["rule_under_header"]
    _add_filled_rect(slide, x_in=r["x_in"], y_in=r["y_in"],
                     w_in=r["w_in"], h_in=r["h_in"],
                     fill_hex=colors[r["fill"]])

    # --- 3. Composite ---
    composite = context.get("composite", {})

    r = layout["regions"]["composite_label"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame, "COMPOSITE",
              font_name=fonts["heading"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], bold=False)

    r = layout["regions"]["composite_value"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame, str(composite.get("value", "—")),
              font_name=fonts["body"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], bold=True)

    r = layout["regions"]["composite_interval"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(
        tb.text_frame,
        f"Intervall: {composite.get('lo', '—')}–{composite.get('hi', '—')}",
        font_name=fonts["body"], size_pt=r["size_pt"],
        color_hex=colors[r["color"]],
    )

    r = layout["regions"]["headline"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame, composite.get("headline", "—"),
              font_name=fonts["body"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], leading=r.get("leading"))

    # --- 4. KPI tiles (3) ---
    band = layout["regions"]["kpi_band"]
    kpis = (context.get("kpis") or [])[:3]
    while len(kpis) < 3:
        kpis.append({"pillar": "—", "value": "—", "delta": "—"})

    for i, k in enumerate(kpis):
        x = band["x_first_in"] + i * (band["tile_w_in"] + band["tile_gap_in"])
        # Gold left border
        _add_filled_rect(slide, x_in=x, y_in=band["y_in"],
                         w_in=0.03, h_in=band["h_in"],
                         fill_hex=colors["gold"])
        # White tile bg
        _add_filled_rect(slide, x_in=x + 0.03, y_in=band["y_in"],
                         w_in=band["tile_w_in"] - 0.03, h_in=band["h_in"],
                         fill_hex=colors["white"])

        # Label
        tb = _add_textbox(slide, x_in=x + 0.20, y_in=band["y_in"] + 0.15,
                          w_in=band["tile_w_in"] - 0.30, h_in=0.30)
        _set_text(tb.text_frame, str(k.get("pillar", "—")).upper(),
                  font_name=fonts["heading"], size_pt=band["label"]["size_pt"],
                  color_hex=colors[band["label"]["color"]])

        # Value
        tb = _add_textbox(slide, x_in=x + 0.20, y_in=band["y_in"] + 0.55,
                          w_in=band["tile_w_in"] - 0.30, h_in=0.70)
        _set_text(tb.text_frame, str(k.get("value", "—")),
                  font_name=fonts["body"], size_pt=band["value"]["size_pt"],
                  color_hex=colors[band["value"]["color"]], bold=True)

        # Delta
        tb = _add_textbox(slide, x_in=x + 0.20, y_in=band["y_in"] + 1.30,
                          w_in=band["tile_w_in"] - 0.30, h_in=0.30)
        _set_text(tb.text_frame, str(k.get("delta", "—")),
                  font_name=fonts["body"], size_pt=band["delta"]["size_pt"],
                  color_hex=colors[band["delta"]["color"]])

    # --- 5. Recommendation band ---
    r = layout["regions"]["recommendation_band"]
    _add_filled_rect(slide, x_in=r["x_in"], y_in=r["y_in"],
                     w_in=r["w_in"], h_in=r["h_in"],
                     fill_hex=colors[r["fill"]])
    _add_filled_rect(slide, x_in=r["x_in"], y_in=r["y_in"],
                     w_in=0.04, h_in=r["h_in"],
                     fill_hex=colors[r["border_left"]["color"]])
    tb = _add_textbox(slide,
                      x_in=r["x_in"] + 0.20, y_in=r["y_in"] + 0.10,
                      w_in=r["w_in"] - 0.30, h_in=r["h_in"] - 0.20)
    _set_text(
        tb.text_frame,
        f"Empfehlung: {context.get('recommendation', '—')}",
        font_name=fonts["body"], size_pt=r["size_pt"],
        color_hex=colors[r["color"]], bold=True,
    )

    # --- 6. Audit footer ---
    r = layout["regions"]["audit_footer"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    audit_url   = context.get("audit_url", "—")
    license_id  = context.get("license", "all_rights_reserved")
    ekb_version = context.get("ekb_version", "—")
    _set_text(
        tb.text_frame,
        f"Audit: {audit_url}    |    Lizenz: {license_id}    |    EKB v{ekb_version}",
        font_name=fonts["body"], size_pt=r["size_pt"],
        color_hex=colors[r["color"]],
    )

    # --- 7. Personalised watermark (optional) ---
    watermark_text = context.get("watermark_text")
    if watermark_text:
        tb = _add_textbox(slide, x_in=2.0, y_in=3.0, w_in=9.5, h_in=1.5)
        _set_text(tb.text_frame, watermark_text.upper(),
                  font_name=fonts["heading"], size_pt=64,
                  color_hex="C7C0AC", bold=True, align="center")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out_path)


def _cli() -> None:
    p = argparse.ArgumentParser(description="Build executive_dark_compact PPTX hero card.")
    p.add_argument("--context", type=Path, required=True,
                   help="JSON file with the slide context.")
    p.add_argument("--out", type=Path, required=True,
                   help="Destination .pptx path.")
    p.add_argument("--master", type=Path, default=MASTER_PATH,
                   help="Override master.json location (default: alongside this script).")
    args = p.parse_args()

    context = json.loads(args.context.read_text(encoding="utf-8"))
    master  = json.loads(args.master.read_text(encoding="utf-8"))
    build(context, master, args.out)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    _cli()
