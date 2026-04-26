"""Idempotent PPTX builder for editorial_press_v1 / media_v1.

Reads master.json + a context dict, emits a chart-pack-as-slides PPTX (one
chart per slide, 16:9, with title + transparent-bg figure + source caption).

Same input -> identical .pptx bytes (deterministic ordering).

Usage:
    python build_pptx.py --context fixture.json --out chart_pack.pptx

Expected context schema:
    {
      "embargo": {"release_at": "...", "tz": "CET"},  # optional banner
      "brand_label": "PTT Platform",
      "date":        "26.04.2026",
      "audit_url":   "...",
      "charts": [
        {
          "title":         "...",
          "subtitle":      "...",
          "image_path":    "/abs/path/to/chart.png",   # transparent PNG
          "alt_text":      "...",
          "caption":       "...",
          "source_label":  "BFS",
          "source_url":    "..."
        },
        ...
      ]
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
        "python-pptx is required to build the editorial_press_v1 PPTX kit. "
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


def _bg(slide, master) -> None:
    _add_filled_rect(
        slide,
        x_in=0, y_in=0,
        w_in=master["slide_size"]["width_in"],
        h_in=master["slide_size"]["height_in"],
        fill_hex=master["theme"]["colors"]["bg_paper"],
    )


def _build_chart_slide(prs, master, context, *, chart: dict) -> None:
    layout = master["layouts"]["chart_slide"]
    colors = master["theme"]["colors"]
    fonts  = master["theme"]["fonts"]

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(slide, master)

    # Embargo banner overlay
    embargo = context.get("embargo")
    if embargo:
        r = layout["regions"]["embargo_banner"]
        _add_filled_rect(slide, x_in=r["x_in"], y_in=r["y_in"],
                         w_in=r["w_in"], h_in=r["h_in"],
                         fill_hex=colors[r["fill"]])
        tb = _add_textbox(slide, x_in=r["x_in"] + 0.2, y_in=r["y_in"] + 0.05,
                          w_in=r["w_in"] - 0.4, h_in=r["h_in"] - 0.10)
        text = f"EMBARGO BIS {embargo.get('release_at', '—')} ({embargo.get('tz', 'CET')})"
        _set_text(tb.text_frame, text,
                  font_name=fonts["heading"], size_pt=r["size_pt"],
                  color_hex=colors[r["color"]], bold=True, align="center")
        # Push the rest of the layout down by 0.4in is implicit via region coords;
        # for v1 we accept slight overlap rather than recompute every region.

    # Brand
    r = layout["regions"]["brand"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame,
              f"{context.get('brand_label', 'PTT Platform')} · GRAFIKPAKET",
              font_name=fonts["heading"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], bold=True)

    # Date
    r = layout["regions"]["date"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame, context.get("date", "—"),
              font_name=fonts["byline"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], align="right")

    # Header rule
    r = layout["regions"]["rule_under_header"]
    _add_filled_rect(slide, x_in=r["x_in"], y_in=r["y_in"],
                     w_in=r["w_in"], h_in=r["h_in"],
                     fill_hex=colors[r["fill"]])

    # Title
    r = layout["regions"]["title"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame, chart.get("title", "—"),
              font_name=fonts["heading"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], bold=True,
              leading=r.get("leading"))

    # Subtitle
    if chart.get("subtitle"):
        r = layout["regions"]["subtitle"]
        tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
        _set_text(tb.text_frame, chart["subtitle"],
                  font_name=fonts["body"], size_pt=r["size_pt"],
                  color_hex=colors[r["color"]], italic=True)

    # Chart image
    image_path = chart.get("image_path")
    if image_path and Path(image_path).exists():
        r = layout["regions"]["chart_area"]
        slide.shapes.add_picture(
            str(image_path),
            Inches(r["x_in"]), Inches(r["y_in"]),
            Inches(r["w_in"]), Inches(r["h_in"]),
        )

    # Caption
    r = layout["regions"]["caption"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    _set_text(tb.text_frame, chart.get("caption", "—"),
              font_name=fonts["body"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], bold=True)

    # Source
    r = layout["regions"]["source"]
    tb = _add_textbox(slide, x_in=r["x_in"], y_in=r["y_in"], w_in=r["w_in"], h_in=r["h_in"])
    src_text = (
        f"Quelle: {chart.get('source_label', '—')}"
        f"{' (' + chart['source_url'] + ')' if chart.get('source_url') else ''}"
        f"  |  Audit: {context.get('audit_url', '—')}"
    )
    _set_text(tb.text_frame, src_text,
              font_name=fonts["byline"], size_pt=r["size_pt"],
              color_hex=colors[r["color"]], italic=True)


def build(context: dict, master: dict, out_path: Path) -> None:
    """Render the chart-pack PPTX to ``out_path``."""
    prs = Presentation()
    prs.slide_width  = Emu(master["slide_size"]["width_emu"])
    prs.slide_height = Emu(master["slide_size"]["height_emu"])

    charts = context.get("charts") or []
    if not charts:
        # Emit one placeholder slide so downstream consumers always get a deck.
        charts = [{
            "title": "(no charts in context)",
            "subtitle": "Provide context['charts'] = [...] to populate.",
            "caption": "",
            "source_label": "—",
        }]

    for chart in charts:
        _build_chart_slide(prs, master, context, chart=chart)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out_path)


def _cli() -> None:
    p = argparse.ArgumentParser(description="Build editorial_press_v1 chart pack PPTX.")
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
