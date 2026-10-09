"""
Generate blogger_intro.pdf — a synthetic non-technical Chinese document.

Content is entirely fictional (a hobby photography blogger intro) and is used
as a test fixture for ingesting short, non-technical Chinese documents that
contain embedded images.
"""
import io
from pathlib import Path

from PIL import Image, ImageDraw
import pymupdf

PAGE_W, PAGE_H = 595, 842  # A4, unit: pt
MARGIN = 50

FICTITIOUS_BLOGGER = "林一舟"
FICTITIOUS_BLOG = "光影漫游"


def _png_bytes(draw_fn, width=900, height=600):
    """Render a synthetic diagram to PNG bytes via PIL."""
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    draw_fn(draw, width, height)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def make_route_diagram():
    """Synthetic 'travel route' schematic: nodes connected by lines."""

    def draw_fn(draw, w, h):
        nodes = [(120, 480), (300, 400), (480, 300), (660, 200), (780, 120)]
        for i in range(len(nodes) - 1):
            draw.line([nodes[i], nodes[i + 1]], fill="#34495e", width=4)
        for i, (x, y) in enumerate(nodes, 1):
            r = 14
            draw.ellipse([x - r, y - r, x + r, y + r], fill="#2e86ab")
            draw.text((x + 18, y - 10), f"站点 {i}", fill="black")

    return _png_bytes(draw_fn)


def make_color_chart():
    """Synthetic 'color palette statistics' bar chart."""

    def draw_fn(draw, w, h):
        bars = [("#2e86ab", 320), ("#e67e22", 210), ("#27ae60", 260), ("#8e44ad", 150)]
        x0, baseline, bar_w, gap = 100, 500, 140, 40
        for i, (color, value) in enumerate(bars):
            x = x0 + i * (bar_w + gap)
            draw.rectangle([x, baseline - value, x + bar_w, baseline], fill=color)
            draw.text((x + 30, baseline - value - 30), str(value), fill="black")
        draw.line([(70, baseline), (w - 70, baseline)], fill="black", width=3)

    return _png_bytes(draw_fn)


def _heading(page, text, y):
    page.insert_textbox(
        pymupdf.Rect(MARGIN, y, PAGE_W - MARGIN, y + 40),
        text, fontname="china-s", fontsize=16, color=(0.15, 0.2, 0.3),
    )


def _body(page, text, y, height=160):
    page.insert_textbox(
        pymupdf.Rect(MARGIN, y, PAGE_W - MARGIN, y + height),
        text, fontname="china-s", fontsize=11, align=3,
    )


def generate_blogger_intro_pdf(output_path):
    doc = pymupdf.open()

    # ---- Page 1: cover ----
    page = doc.new_page(width=PAGE_W, height=PAGE_H)
    _heading(page, f"{FICTITIOUS_BLOG} — 博客介绍 & 内容说明", 200)
    _body(
        page,
        f"作者：{FICTITIOUS_BLOGGER}\n"
        "主题：风光摄影与旅行记录\n"
        "性质：虚构示例文档（仅用于测试）\n"
        "版本：v1.0",
        300,
        height=120,
    )

    # ---- Page 2: personal intro ----
    page = doc.new_page(width=PAGE_W, height=PAGE_H)
    _heading(page, "1. 博主介绍", 60)
    _body(
        page,
        f"{FICTITIOUS_BLOG} 的作者 {FICTITIOUS_BLOGGER} 是一个虚构的摄影爱好者形象：白天在一家小型"
        "设计工作室做平面设计，周末背着相机在城市周边爬山拍日出。接触摄影五年，最喜欢的"
        "是海边长曝光和山地星野题材。博客记录拍摄路线、器材使用心得和后期调色笔记。\n\n"
        "博客的主要内容分为三个系列：\n"
        "• 城市周边拍摄路线合集（附交通与机位说明）\n"
        "• 器材使用心得（镜头选择、三脚架、滤镜）\n"
        "• 后期调色笔记（色彩风格分析与示例参数）",
        110,
        height=300,
    )

    # ---- Page 3: route diagram ----
    page = doc.new_page(width=PAGE_W, height=PAGE_H)
    _heading(page, "图片1：示例拍摄路线示意", 60)
    page.insert_image(
        pymupdf.Rect(MARGIN, 120, PAGE_W - MARGIN, 580), stream=make_route_diagram()
    )
    _body(
        page,
        "上图为虚构的拍摄路线示意：从山脚观景台出发，依次经过三个机位，最终到达海崖日出点。",
        600,
        height=60,
    )

    # ---- Page 4: color chart ----
    page = doc.new_page(width=PAGE_W, height=PAGE_H)
    _heading(page, "图片2：调色风格样本统计", 60)
    page.insert_image(
        pymupdf.Rect(MARGIN, 120, PAGE_W - MARGIN, 560), stream=make_color_chart()
    )
    _body(
        page,
        "上图为虚构的调色风格统计：冷色系样本最多，其次是森林绿与暖橙色调。",
        580,
        height=60,
    )

    doc.save(str(output_path), deflate=True, garbage=4)
    doc.close()
    print(f"PDF generated successfully: {output_path}")


def main():
    output_dir = Path(__file__).parent / "sample_documents"
    output_dir.mkdir(exist_ok=True)
    generate_blogger_intro_pdf(output_dir / "blogger_intro.pdf")


if __name__ == "__main__":
    main()
