# -*- coding: utf-8 -*-
"""MVP-прототип надстройки «Корпоративная библиотека презентаций»."""

import sys
from datetime import datetime
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Корпоративная библиотека презентаций.pptx"


def save_presentation(prs: Presentation, target: Path | None = None) -> Path:
    """Сохраняет .pptx; при блокировке файла — под резервным именем."""
    candidates = [target] if target else []
    candidates.append(OUT)
    candidates.append(ROOT / "Корпоративная библиотека презентаций (новая).pptx")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    candidates.append(ROOT / f"Корпоративная библиотека презентаций_{stamp}.pptx")

    seen: set[Path] = set()
    last_err: PermissionError | None = None

    for path in candidates:
        if path is None or path in seen:
            continue
        seen.add(path)
        try:
            prs.save(path)
            if path != OUT:
                print(
                    f"Не удалось перезаписать «{OUT.name}» (файл занят).\n"
                    f"Сохранено как: {path}",
                    file=sys.stderr,
                )
            return path
        except PermissionError as e:
            last_err = e

    msg = (
        f"Нет доступа для записи: {OUT}\n"
        "Закройте файл в PowerPoint (и проводнике с предпросмотром), затем запустите снова."
    )
    raise PermissionError(msg) from last_err

# Корпоративная палитра
C_PRIMARY = RGBColor(0x00, 0x5B, 0xA8)
C_PRIMARY_DARK = RGBColor(0x00, 0x3D, 0x73)
C_ACCENT = RGBColor(0x00, 0xA3, 0xE0)
C_BG = RGBColor(0xF4, 0xF7, 0xFA)
C_PANEL = RGBColor(0xFF, 0xFF, 0xFF)
C_BORDER = RGBColor(0xD0, 0xD7, 0xDE)
C_TEXT = RGBColor(0x1A, 0x1F, 0x36)
C_MUTED = RGBColor(0x5C, 0x67, 0x7A)
C_SUCCESS = RGBColor(0x0D, 0x7A, 0x4A)
C_HIGHLIGHT = RGBColor(0xE8, 0xF4, 0xFC)
C_ORANGE = RGBColor(0xE6, 0x5C, 0x00)


def set_slide_bg(slide, color: RGBColor):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(slide, left, top, width, height, fill_rgb, line_rgb=None, line_pt=0.75):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_rgb
    if line_rgb:
        shape.line.color.rgb = line_rgb
        shape.line.width = Pt(line_pt)
    else:
        shape.line.fill.background()
    return shape


def add_round_rect(slide, left, top, width, height, fill_rgb, line_rgb=None):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_rgb
    if line_rgb:
        shape.line.color.rgb = line_rgb
        shape.line.width = Pt(0.75)
    else:
        shape.line.fill.background()
    return shape


def add_text_box(slide, left, top, width, height, text, size=12, bold=False,
                 color=C_TEXT, align=PP_ALIGN.LEFT, font_name="Segoe UI"):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.name = font_name
    p.font.color.rgb = color
    p.alignment = align
    return box


def add_bullet_block(slide, left, top, width, height, lines, size=14, color=C_TEXT):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.level = 0
        p.font.size = Pt(size)
        p.font.name = "Segoe UI"
        p.font.color.rgb = color
        p.space_after = Pt(6)
    return box


def add_header_bar(slide, title, subtitle=None):
    add_rect(slide, Inches(0), Inches(0), Inches(13.33), Inches(0.95), C_PRIMARY)
    add_text_box(
        slide, Inches(0.5), Inches(0.22), Inches(10), Inches(0.5),
        title, size=22, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF)
    )
    if subtitle:
        add_text_box(
            slide, Inches(0.5), Inches(0.58), Inches(10), Inches(0.35),
            subtitle, size=11, color=RGBColor(0xCC, 0xE5, 0xFF)
        )


def add_footer(slide, text):
    add_text_box(
        slide, Inches(0.5), Inches(7.05), Inches(12), Inches(0.35),
        text, size=9, color=C_MUTED
    )


def draw_ppt_canvas(slide, slide_title="Моя презентация.pptx"):
    """Левая часть — имитация окна PowerPoint."""
    add_rect(slide, Inches(0.45), Inches(1.15), Inches(8.55), Inches(5.75), C_PANEL, C_BORDER)
    add_rect(slide, Inches(0.45), Inches(1.15), Inches(8.55), Inches(0.42), RGBColor(0xF0, 0xF0, 0xF0), C_BORDER)
    add_text_box(
        slide, Inches(0.6), Inches(1.22), Inches(5), Inches(0.3),
        slide_title, size=10, color=C_MUTED
    )
    for i in range(3):
        y = Inches(1.75) + Inches(i * 1.55)
        add_rect(slide, Inches(0.75), y, Inches(7.95), Inches(1.35), C_BG, C_BORDER)
        add_text_box(
            slide, Inches(0.95), y + Inches(0.45), Inches(6), Inches(0.5),
            f"Слайд {i + 1} — рабочая область презентации",
            size=14, color=C_MUTED
        )


def draw_task_pane(slide, header, body_fn, badge="MVP"):
    """Правая панель — надстройка библиотеки."""
    px = Inches(9.15)
    add_rect(slide, px, Inches(1.15), Inches(3.75), Inches(5.75), C_PANEL, C_PRIMARY, 1.5)
    add_rect(slide, px, Inches(1.15), Inches(3.75), Inches(0.55), C_PRIMARY_DARK)
    add_text_box(
        slide, px + Inches(0.15), Inches(1.25), Inches(2.8), Inches(0.35),
        "Корп. библиотека", size=11, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF)
    )
    add_round_rect(
        slide, px + Inches(2.85), Inches(1.28), Inches(0.65), Inches(0.28),
        C_ACCENT
    )
    add_text_box(
        slide, px + Inches(2.9), Inches(1.3), Inches(0.55), Inches(0.25),
        badge, size=8, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF), align=PP_ALIGN.CENTER
    )
    add_text_box(
        slide, px + Inches(0.15), Inches(1.72), Inches(3.45), Inches(0.35),
        header, size=12, bold=True, color=C_PRIMARY_DARK
    )
    body_fn(slide, px)


def pane_search_box(slide, px, placeholder="Поиск слайдов, тегов, отделов…", active=False):
    fill = C_HIGHLIGHT if active else RGBColor(0xFF, 0xFF, 0xFF)
    add_round_rect(slide, px + Inches(0.15), Inches(2.1), Inches(3.45), Inches(0.42), fill, C_ACCENT if active else C_BORDER)
    add_text_box(
        slide, px + Inches(0.35), Inches(2.18), Inches(3.1), Inches(0.3),
        placeholder, size=9, color=C_MUTED if not active else C_PRIMARY
    )


def pane_chip_row(slide, px, labels, y=Inches(2.62)):
    x = px + Inches(0.15)
    for label in labels:
        w = Inches(0.55 + len(label) * 0.07)
        add_round_rect(slide, x, y, w, Inches(0.28), C_HIGHLIGHT, C_BORDER)
        add_text_box(slide, x + Inches(0.08), y + Inches(0.04), w, Inches(0.22), label, size=8, color=C_PRIMARY)
        x += w + Inches(0.08)


def pane_list_item(slide, px, y, title, meta, selected=False, thumb_color=C_ACCENT):
    bg = C_HIGHLIGHT if selected else RGBColor(0xFF, 0xFF, 0xFF)
    border = C_PRIMARY if selected else C_BORDER
    add_round_rect(slide, px + Inches(0.15), y, Inches(3.45), Inches(0.72), bg, border)
    add_rect(slide, px + Inches(0.28), y + Inches(0.12), Inches(0.55), Inches(0.48), thumb_color)
    add_text_box(slide, px + Inches(0.95), y + Inches(0.1), Inches(2.4), Inches(0.28), title, size=9, bold=selected)
    add_text_box(slide, px + Inches(0.95), y + Inches(0.38), Inches(2.4), Inches(0.22), meta, size=8, color=C_MUTED)


def pane_button(slide, px, y, label, primary=True):
    fill = C_PRIMARY if primary else RGBColor(0xFF, 0xFF, 0xFF)
    text_c = RGBColor(0xFF, 0xFF, 0xFF) if primary else C_PRIMARY
    border = None if primary else C_PRIMARY
    add_round_rect(slide, px + Inches(0.15), y, Inches(3.45), Inches(0.38), fill, border)
    add_text_box(
        slide, px + Inches(0.15), y + Inches(0.08), Inches(3.45), Inches(0.28),
        label, size=10, bold=True, color=text_c, align=PP_ALIGN.CENTER
    )


def slide_title(prs, blank):
    s = prs.slides.add_slide(blank)
    set_slide_bg(s, C_PRIMARY_DARK)
    add_rect(s, Inches(0), Inches(0), Inches(13.33), Inches(0.12), C_ACCENT)
    add_text_box(
        s, Inches(0.8), Inches(2.2), Inches(11.5), Inches(1.2),
        "Корпоративная библиотека презентаций",
        size=40, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF), align=PP_ALIGN.LEFT
    )
    add_text_box(
        s, Inches(0.8), Inches(3.35), Inches(11), Inches(0.6),
        "MVP-прототип надстройки PowerPoint · интерактивная концепция",
        size=18, color=RGBColor(0xB3, 0xD9, 0xF2)
    )
    add_round_rect(s, Inches(0.8), Inches(4.35), Inches(4.2), Inches(0.55), C_ACCENT)
    add_text_box(
        s, Inches(1), Inches(4.48), Inches(3.8), Inches(0.35),
        "Готово к пилотному внедрению", size=14, bold=True,
        color=RGBColor(0xFF, 0xFF, 0xFF), align=PP_ALIGN.CENTER
    )
    add_text_box(
        s, Inches(0.8), Inches(5.5), Inches(10), Inches(1),
        "Централизованный доступ · Поиск · Просмотр · Вставка утверждённых слайдов",
        size=13, color=RGBColor(0xCC, 0xE5, 0xFF)
    )


def slide_metrics(prs, blank):
    s = prs.slides.add_slide(blank)
    set_slide_bg(s, C_BG)
    add_header_bar(s, "Метрики MVP", "Измеримые показатели для стейкхолдеров")
    metrics = [
        ("DAU в надстройке", "Активные пользователи/день", "Цель: 60% пилотной группы"),
        ("Время до вставки", "Поиск → вставка", "Цель: < 45 сек"),
        ("Доля утверждённого", "Вставки из библиотеки vs локальные", "Цель: > 70%"),
        ("Актуальность", "Слайды с просроченной версией", "Цель: 0%"),
    ]
    for i, (name, sub, goal) in enumerate(metrics):
        col = i % 2
        row = i // 2
        x = Inches(0.55) + Inches(col * 6.35)
        y = Inches(1.35) + Inches(row * 2.75)
        add_round_rect(s, x, y, Inches(6.0), Inches(2.35), C_PANEL, C_BORDER)
        add_text_box(s, x + Inches(0.25), y + Inches(0.25), Inches(5.5), Inches(0.4), name, size=16, bold=True, color=C_PRIMARY)
        add_text_box(s, x + Inches(0.25), y + Inches(0.75), Inches(5.5), Inches(0.35), sub, size=12, color=C_MUTED)
        add_text_box(s, x + Inches(0.25), y + Inches(1.35), Inches(5.5), Inches(0.5), goal, size=11, bold=True, color=C_SUCCESS)
    add_footer(s, "Слайд 10 · Метрики")


def slide_next_steps(prs, blank):
    s = prs.slides.add_slide(blank)
    set_slide_bg(s, C_PRIMARY_DARK)
    add_text_box(
        s, Inches(0.8), Inches(1.2), Inches(11), Inches(0.7),
        "Следующие шаги", size=32, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF)
    )
    steps = [
        "Утвердить состав пилотной группы и владельцев контента",
        "Финализировать манифест Office Add-in и хостинг панели",
        "Подключить корпоративное хранилище слайдов (SharePoint / custom API)",
        "Провести UX-тест прототипа с 5–8 ключевыми пользователями",
        "Запустить пилот на 8 недель с еженедельной отчётностью",
    ]
    add_bullet_block(
        s, Inches(0.8), Inches(2.1), Inches(11), Inches(4.5),
        steps, size=16, color=RGBColor(0xE8, 0xF4, 0xFC)
    )
    add_footer(s, "Слайд 11 · Call to action")


def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # Порядок слайдов как в отредактированном .pptx
    slide_title(prs, blank)
    slide_metrics(prs, blank)
    slide_next_steps(prs, blank)

    # --- Ценность ---
    s = prs.slides.add_slide(blank)
    set_slide_bg(s, C_BG)
    add_header_bar(s, "Продуктовая ценность", "Единый источник утверждённых материалов")
    add_bullet_block(
        s, Inches(0.6), Inches(1.35), Inches(5.8), Inches(5.5),
        [
            "Проблема: разрозненные файлы, устаревшие логотипы, несогласованный тон.",
            "Решение: библиотека слайдов с версионированием и статусом «Утверждено».",
            "Доступ из PowerPoint без переключения контекста — панель задач (Task Pane).",
            "Контент-владельцы загружают пакеты; сотрудники только потребляют.",
            "Сокращение времени сборки презентации на 40–60% (целевая метрика пилота).",
        ],
        size=15
    )
    cols = [
        ("Утверждённые слайды", "Шаблоны разделов, титулы, KPI"),
        ("Визуальные материалы", "Иконки, диаграммы, фото бренда"),
        ("Метаданные", "Теги, отдел, язык, дата ревизии"),
        ("Контроль", "RBAC, аудит вставок, отзыв версий"),
    ]
    for i, (t, d) in enumerate(cols):
        col = i % 2
        row = i // 2
        x = Inches(6.5) + Inches(col * 3.35)
        y = Inches(1.55) + Inches(row * 2.35)
        add_round_rect(s, x, y, Inches(3.15), Inches(2.05), C_PANEL, C_BORDER)
        add_rect(s, x, y, Inches(3.15), Inches(0.08), C_PRIMARY)
        add_text_box(s, x + Inches(0.2), y + Inches(0.25), Inches(2.8), Inches(0.4), t, size=13, bold=True, color=C_PRIMARY)
        add_text_box(s, x + Inches(0.2), y + Inches(0.75), Inches(2.8), Inches(1), d, size=11, color=C_MUTED)
    add_footer(s, "Слайд 2 · Концепция")

    # --- Интеграция ---
    s = prs.slides.add_slide(blank)
    set_slide_bg(s, C_BG)
    add_header_bar(s, "Интеграция в PowerPoint", "Надстройка Office (Office Add-in) — архитектура MVP")
    steps = [
        ("1", "Ribbon", "Вкладка «Библиотека» → открыть панель"),
        ("2", "Task Pane", "HTML/JS UI внутри PowerPoint"),
        ("3", "API", "Graph / корп. CMS слайдов"),
        ("4", "Insert", "Office.js — вставка слайда в активную deck"),
    ]
    for i, (num, title, desc) in enumerate(steps):
        y = Inches(1.4) + Inches(i * 1.35)
        add_round_rect(s, Inches(0.6), y, Inches(0.55), Inches(0.55), C_PRIMARY)
        add_text_box(s, Inches(0.72), y + Inches(0.1), Inches(0.35), Inches(0.35), num, size=16, bold=True,
                     color=RGBColor(0xFF, 0xFF, 0xFF), align=PP_ALIGN.CENTER)
        add_text_box(s, Inches(1.35), y + Inches(0.05), Inches(2.5), Inches(0.35), title, size=14, bold=True, color=C_PRIMARY_DARK)
        add_text_box(s, Inches(1.35), y + Inches(0.38), Inches(4.5), Inches(0.35), desc, size=11, color=C_MUTED)
        if i < 3:
            add_rect(s, Inches(0.82), y + Inches(0.55), Inches(0.06), Inches(0.8), C_ACCENT)
    draw_ppt_canvas(s)
    def pane_home(sl, px):
        pane_search_box(sl, px)
        pane_chip_row(sl, px, ["Все", "Продажи", "HR"])
        pane_list_item(sl, px, Inches(3.05), "Титульный слайд — бренд", "Утверждено · v3.2 · Маркетинг")
        pane_list_item(sl, px, Inches(3.85), "KPI-квартал (диаграмма)", "Утверждено · v1.8 · Финансы", thumb_color=C_SUCCESS)
        pane_list_item(sl, px, Inches(4.65), "Команда / оргструктура", "Утверждено · v2.0 · HR")
        pane_button(sl, px, Inches(6.35), "Вставить выбранное")
    draw_task_pane(s, "Каталог утверждённых материалов", pane_home)
    add_footer(s, "Слайд 3 · Встроенный интерфейс")

    # --- Поиск ---
    s = prs.slides.add_slide(blank)
    set_slide_bg(s, C_BG)
    add_header_bar(s, "Сценарий: Поиск", "Быстрый доступ по названию, тегам и метаданным")
    draw_ppt_canvas(s, "Презентация_Продажи_Q2.pptx")

    def pane_search(sl, px):
        pane_search_box(sl, px, "диаграмма продажи", active=True)
        add_text_box(sl, px + Inches(0.15), Inches(2.58), Inches(3.2), Inches(0.25),
                     "12 результатов · 0.3 с", size=8, color=C_MUTED)
        pane_chip_row(sl, px, ["диаграмма", "продажи", "Q2"], y=Inches(2.88))
        pane_list_item(sl, px, Inches(3.25), "Воронка продаж B2B", "Утверждено · 4 слайда · Продажи", selected=True)
        pane_list_item(sl, px, Inches(4.05), "Динамика выручки Q2", "Утверждено · 1 слайд · Финансы", thumb_color=C_ORANGE)
        pane_list_item(sl, px, Inches(4.85), "Сравнение сегментов", "Утверждено · 2 слайда · Аналитика")
        pane_button(sl, px, Inches(5.65), "Предпросмотр", primary=False)
        pane_button(sl, px, Inches(6.1), "Вставить в презентацию")
    draw_task_pane(s, "Поиск", pane_search)
    add_text_box(
        s, Inches(0.55), Inches(6.55), Inches(8), Inches(0.4),
        "Фильтры: отдел · статус · язык · период обновления",
        size=10, color=C_MUTED
    )
    add_footer(s, "Слайд 4 · Пользовательский сценарий — Поиск")

    # --- Просмотр ---
    s = prs.slides.add_slide(blank)
    set_slide_bg(s, C_BG)
    add_header_bar(s, "Сценарий: Просмотр", "Превью с метаданными до вставки")
    draw_ppt_canvas(s)

    def pane_preview(sl, px):
        pane_search_box(sl, px, "Воронка продаж B2B")
        add_round_rect(sl, px + Inches(0.15), Inches(2.55), Inches(3.45), Inches(2.05), C_BG, C_BORDER)
        add_text_box(
            sl, px + Inches(0.35), Inches(3.15), Inches(3.1), Inches(0.5),
            "[ Превью слайда ]", size=11, color=C_MUTED, align=PP_ALIGN.CENTER
        )
        add_rect(sl, px + Inches(0.35), Inches(2.7), Inches(3.05), Inches(1.35), C_ACCENT)
        meta = [
            "Статус: Утверждено",
            "Владелец: Департамент продаж",
            "Обновлено: 12.05.2026",
            "Слайдов в пакете: 4",
        ]
        y = Inches(4.72)
        for line in meta:
            add_text_box(sl, px + Inches(0.2), y, Inches(3.3), Inches(0.22), line, size=8, color=C_MUTED)
            y += Inches(0.24)
        pane_button(sl, px, Inches(5.95), "← Назад к результатам", primary=False)
        pane_button(sl, px, Inches(6.4), "Вставить все / выбранные")
    draw_task_pane(s, "Просмотр", pane_preview)
    add_footer(s, "Слайд 5 · Пользовательский сценарий — Просмотр")

    # --- Вставка ---
    s = prs.slides.add_slide(blank)
    set_slide_bg(s, C_BG)
    add_header_bar(s, "Сценарий: Вставка", "Слайд добавляется в активную презентацию одним действием")
    draw_ppt_canvas(s, "Презентация_Продажи_Q2.pptx")
    add_round_rect(s, Inches(0.75), Inches(4.35), Inches(7.95), Inches(1.35), C_HIGHLIGHT, C_PRIMARY)
    add_text_box(
        s, Inches(0.95), Inches(4.75), Inches(7.5), Inches(0.55),
        "✓ Вставлено: «Воронка продаж B2B» — слайд 4",
        size=14, bold=True, color=C_SUCCESS
    )

    def pane_insert(sl, px):
        add_round_rect(sl, px + Inches(0.15), Inches(2.1), Inches(3.45), Inches(1.1), RGBColor(0xE8, 0xF8, 0xEF), C_SUCCESS)
        add_text_box(
            sl, px + Inches(0.25), Inches(2.25), Inches(3.25), Inches(0.8),
            "Успешно вставлено\nЗапись в журнале аудита",
            size=10, bold=True, color=C_SUCCESS, align=PP_ALIGN.CENTER
        )
        add_text_box(sl, px + Inches(0.15), Inches(3.35), Inches(3.45), Inches(0.5),
                     "Параметры вставки:", size=9, bold=True, color=C_TEXT)
        opts = ["После текущего слайда", "Сохранить форматирование темы", "Связать с источником (обновления)"]
        y = Inches(3.85)
        for o in opts:
            add_text_box(sl, px + Inches(0.2), y, Inches(3.3), Inches(0.22), f"☑ {o}", size=8, color=C_MUTED)
            y += Inches(0.26)
        pane_button(sl, px, Inches(5.35), "Вставить ещё")
        pane_button(sl, px, Inches(5.8), "Закрыть", primary=False)
    draw_task_pane(s, "Вставка", pane_insert)
    add_footer(s, "Слайд 6 · Пользовательский сценарий — Вставка")

    # --- Каталог контента ---
    s = prs.slides.add_slide(blank)
    set_slide_bg(s, C_BG)
    add_header_bar(s, "Каталог утверждённых материалов", "Типы активов в корпоративной библиотеке")
    categories = [
        ("Слайды-шаблоны", "Титулы, повестка, разделители, thank you", "124"),
        ("Диаграммы и данные", "KPI, waterfall, funnel, timeline", "86"),
        ("Визуальный бренд", "Логотипы, паттерны, иконки", "210"),
        ("Текстовые блоки", "Дисклеймеры, цитаты, compliance", "45"),
        ("Локализации", "RU / EN / KZ наборы", "38"),
    ]
    for i, (title, desc, count) in enumerate(categories):
        y = Inches(1.25) + Inches(i * 1.15)
        add_round_rect(s, Inches(0.55), y, Inches(12.2), Inches(0.95), C_PANEL, C_BORDER)
        add_rect(s, Inches(0.55), y, Inches(0.1), Inches(0.95), C_PRIMARY)
        add_text_box(s, Inches(0.85), y + Inches(0.12), Inches(4), Inches(0.35), title, size=14, bold=True)
        add_text_box(s, Inches(0.85), y + Inches(0.48), Inches(8), Inches(0.35), desc, size=11, color=C_MUTED)
        add_round_rect(s, Inches(11.35), y + Inches(0.28), Inches(0.95), Inches(0.38), C_HIGHLIGHT, C_BORDER)
        add_text_box(s, Inches(11.4), y + Inches(0.33), Inches(0.85), Inches(0.3), count, size=11, bold=True,
                     color=C_PRIMARY, align=PP_ALIGN.CENTER)
    add_footer(s, "Слайд 7 · Контент")

    # --- Роли ---
    s = prs.slides.add_slide(blank)
    set_slide_bg(s, C_BG)
    add_header_bar(s, "Роли и централизованный доступ", "RBAC и жизненный цикл публикации")
    roles = [
        ("Сотрудник", "Поиск · просмотр · вставка", "Только «Утверждено»"),
        ("Контент-менеджер", "Загрузка · теги · отправка на ревью", "Черновик → На согласовании"),
        ("Администратор бренда", "Утверждение · отзыв · аудит", "Полный каталог + журнал"),
    ]
    for i, (role, actions, scope) in enumerate(roles):
        x = Inches(0.55) + Inches(i * 4.15)
        add_round_rect(s, x, Inches(1.4), Inches(3.85), Inches(4.8), C_PANEL, C_BORDER)
        add_rect(s, x, Inches(1.4), Inches(3.85), Inches(0.55), C_PRIMARY)
        add_text_box(s, x + Inches(0.2), Inches(1.52), Inches(3.4), Inches(0.35), role, size=14, bold=True,
                     color=RGBColor(0xFF, 0xFF, 0xFF))
        add_text_box(s, x + Inches(0.2), Inches(2.15), Inches(3.4), Inches(1.2), actions, size=12)
        add_text_box(s, x + Inches(0.2), Inches(3.5), Inches(3.4), Inches(0.8), scope, size=10, color=C_MUTED)
    add_text_box(
        s, Inches(0.55), Inches(6.35), Inches(12), Inches(0.5),
        "Интеграция: Azure AD / корп. SSO · единый вход из PowerPoint",
        size=11, color=C_PRIMARY_DARK, bold=True
    )
    add_footer(s, "Слайд 8 · Доступ")

    # --- Пилот ---
    s = prs.slides.add_slide(blank)
    set_slide_bg(s, C_BG)
    add_header_bar(s, "Пилотное внедрение", "Дорожная карта MVP → пилот → масштабирование")
    phases = [
        ("Недели 1–2", "Настройка каталога", "50 утверждённых слайдов, 3 отдела-пилота"),
        ("Недели 3–4", "Развёртывание add-in", "Office 365, группа 30–50 пользователей"),
        ("Недели 5–8", "Сбор обратной связи", "Метрики, NPS, доработка UX"),
        ("Месяц 3+", "Масштаб", "Все подразделения, интеграция CMS"),
    ]
    for i, (when, what, detail) in enumerate(phases):
        y = Inches(1.3) + Inches(i * 1.4)
        add_round_rect(s, Inches(0.55), y, Inches(12.2), Inches(1.15), C_PANEL, C_BORDER)
        add_text_box(s, Inches(0.75), y + Inches(0.15), Inches(1.8), Inches(0.35), when, size=12, bold=True, color=C_PRIMARY)
        add_text_box(s, Inches(2.6), y + Inches(0.15), Inches(3.5), Inches(0.35), what, size=13, bold=True)
        add_text_box(s, Inches(2.6), y + Inches(0.55), Inches(9.5), Inches(0.45), detail, size=11, color=C_MUTED)
    add_footer(s, "Слайд 9 · Пилот")

    return save_presentation(prs)


if __name__ == "__main__":
    out_arg = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else None
    path = build_presentation()
    if out_arg and path != out_arg:
        prs = Presentation(path)
        path = save_presentation(prs, out_arg)
    print(f"Created: {path}")

