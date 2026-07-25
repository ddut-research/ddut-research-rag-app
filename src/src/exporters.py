from __future__ import annotations

import io
import csv
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def to_txt(text: str) -> bytes:
    return (text or "").encode("utf-8")


def to_csv(df) -> bytes:
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")


def to_pdf(result: dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    x = 40
    y = height - 40
    line_height = 14

    def draw_line(text: str):
        nonlocal y
        for part in wrap_text(text, 95):
            if y < 50:
                c.showPage()
                y = height - 40
            c.drawString(x, y, part)
            y -= line_height

    def wrap_text(text: str, limit: int):
        words = (text or "").split()
        lines = []
        current = []
        length = 0
        for word in words:
            extra = len(word) + (1 if current else 0)
            if length + extra > limit:
                lines.append(" ".join(current))
                current = [word]
                length = len(word)
            else:
                current.append(word)
                length += extra
        if current:
            lines.append(" ".join(current))
        return lines or [""]

    draw_line("Research Report")
    draw_line(f"District: {result.get('district', '')}")
    draw_line(f"Question: {result.get('question', '')}")
    draw_line("")
    draw_line("Citizen Summary")
    draw_line(result.get("citizen_summary", ""))
    draw_line("")
    draw_line("Memorandum Brief")
    draw_line(result.get("memo_brief", ""))

    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
