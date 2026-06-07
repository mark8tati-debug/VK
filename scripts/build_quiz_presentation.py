# -*- coding: utf-8 -*-
"""Презентация для сдачи проекта «Квизы» — live-платформа квизов."""

import sys
from datetime import datetime
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Квизы — презентация для сдачи.pptx"
SCREENSHOTS = ROOT / "docs" / "screenshots"
TOTAL_SLIDES = 16

# Палитра по макетам Figma
C_PRIMARY = RGBColor(0x6C, 0x5C, 0xE7)
C_PRIMARY_DARK = RGBColor(0x4A, 0x3D, 0xB8)
C_ACCENT = RGBColor(0xFF, 0x6B, 0x6B)
C_BG = RGBColor(0xF6, 0xF6, 0xFA)
C_PANEL = RGBColor(0xFF, 0xFF, 0xFF)
C_BORDER = RGBColor(0xE0, 0xE3, 0xEB)
C_TEXT = RGBColor(0x1A, 0x1F, 0x36)
C_MUTED = RGBColor(0x5C, 0x67, 0x7A)
C_SUCCESS = RGBColor(0x2E, 0xB8, 0x73)
C_HIGHLIGHT = RGBColor(0xF0, 0xEE, 0xFF)

FIGMA_URL = "https://www.figma.com/design/bowNce537o2YiRGUxFzpAH"
REPO_URL = "https://github.com/mark8tati-debug/VK"
DEMO_URL = "http://localhost:5173 (локальный запуск)"


def save_presentation(prs: Presentation) -> Path:
    candidates = [
        OUT,
        ROOT / "Квизы — презентация для сдачи (новая).pptx",
        ROOT / f"Квизы — презентация_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx",
    ]
    seen: set[Path] = set()
    last_err: PermissionError | None = None
    for path in candidates:
        if path in seen:
            continue
        seen.add(path)
        try:
            prs.save(path)
            if path != OUT:
                print(f"Сохранено как: {path}", file=sys.stderr)
            return path
        except PermissionError as e:
            last_err = e
    raise PermissionError(f"Закройте файл в PowerPoint: {OUT}") from last_err


def set_slide_bg(slide, color: RGBColor):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(slide, left, top, width, height, fill_rgb, line_rgb=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_rgb
    if line_rgb:
        shape.line.color.rgb = line_rgb
        shape.line.width = Pt(0.75)
    else:
        shape.line.fill.background()
    return shape


def add_round_rect(slide, left, top, width, height, fill_rgb, line_rgb=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_rgb
    if line_rgb:
        shape.line.color.rgb = line_rgb
        shape.line.width = Pt(0.75)
    else:
        shape.line.fill.background()
    return shape


def add_text(slide, left, top, width, height, text, size=14, bold=False,
             color=C_TEXT, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.name = "Segoe UI"
    p.font.color.rgb = color
    p.alignment = align
    return box


def add_bullets(slide, left, top, width, height, lines, size=14, color=C_TEXT, spacing=8):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.size = Pt(size)
        p.font.name = "Segoe UI"
        p.font.color.rgb = color
        p.space_after = Pt(spacing)
    return box


def header(slide, title, subtitle=None):
    add_rect(slide, Inches(0), Inches(0), Inches(13.33), Inches(0.9), C_PRIMARY)
    add_text(slide, Inches(0.55), Inches(0.2), Inches(11), Inches(0.5),
             title, size=24, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))
    if subtitle:
        add_text(slide, Inches(0.55), Inches(0.55), Inches(11), Inches(0.3),
                 subtitle, size=11, color=RGBColor(0xDD, 0xD6, 0xFF))


def add_screenshot(slide, image_path: Path, left, top, width, height):
    if image_path.exists():
        slide.shapes.add_picture(str(image_path), left, top, width=width, height=height)
        return True
    add_round_rect(slide, left, top, width, height, C_HIGHLIGHT, C_BORDER)
    add_text(slide, left + Inches(0.2), top + height / 2 - Inches(0.2), width - Inches(0.4), Inches(0.4),
             f"Скриншот: {image_path.name}", size=11, color=C_MUTED, align=PP_ALIGN.CENTER)
    return False


def slide_app_screenshot(prs, n, title, image_name, caption):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, C_BG)
    header(slide, title, "Скриншот работающего приложения")
    img = SCREENSHOTS / image_name
    add_screenshot(slide, img, Inches(0.7), Inches(1.15), Inches(11.9), Inches(5.35))
    add_text(slide, Inches(0.7), Inches(6.55), Inches(11.9), Inches(0.4), caption, size=12, color=C_MUTED)
    footer(slide, n, total=TOTAL_SLIDES)
    return slide


def footer(slide, n, total=TOTAL_SLIDES):
    add_text(slide, Inches(0.55), Inches(7.1), Inches(12), Inches(0.3),
             f"Квизы · MVP · 2026          {n} / {total}",
             size=9, color=C_MUTED)


def slide_title(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, C_PRIMARY_DARK)
    add_round_rect(slide, Inches(0.8), Inches(1.6), Inches(11.7), Inches(4.2), C_PANEL)
    add_text(slide, Inches(1.2), Inches(2.2), Inches(10.5), Inches(0.9),
             "Квизы", size=44, bold=True, color=C_PRIMARY)
    add_text(slide, Inches(1.2), Inches(3.1), Inches(10.5), Inches(0.7),
             "Веб-приложение для проведения live-квизов", size=22, color=C_TEXT)
    add_text(slide, Inches(1.2), Inches(4.0), Inches(10.5), Inches(0.5),
             "MVP · прототип для пилотного тестирования", size=16, color=C_MUTED)
    add_text(slide, Inches(1.2), Inches(4.8), Inches(10.5), Inches(0.4),
             "mark8tati-debug · 2026", size=13, color=C_MUTED)
    return slide


def slide_problem(prs, n):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, C_BG)
    header(slide, "Постановка задачи")
    add_bullets(slide, Inches(0.7), Inches(1.2), Inches(12), Inches(5.5), [
        "Разработать веб-приложение для проведения квизов в реальном времени.",
        "Две роли: организатор (создаёт и ведёт квиз) и участник (подключается по коду комнаты).",
        "Вопросы показываются синхронно всем участникам; ответы принимаются только во время демонстрации.",
        "По завершении — подсчёт баллов, лидерборд и сохранение истории в базе данных.",
        "Результат сдачи: презентация + макеты + репозиторий + работоспособный прототип.",
    ], size=16)
    footer(slide, n)
    return slide


def slide_mvp_result(prs, n):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, C_BG)
    header(slide, "Целевой результат MVP")
    cards = [
        ("Организатор", "Создаёт квиз, добавляет вопросы, запускает live-сессию по коду KVIZ-…"),
        ("Участник", "Входит по коду, отвечает на активные вопросы в браузере"),
        ("Real-time", "Socket.IO синхронизирует показ вопросов и приём ответов"),
        ("Итоги", "Лидерборд с баллами, история в личном кабинете"),
    ]
    for i, (title, desc) in enumerate(cards):
        col, row = i % 2, i // 2
        x = Inches(0.7) + Inches(col * 6.2)
        y = Inches(1.25) + Inches(row * 2.85)
        add_round_rect(slide, x, y, Inches(5.8), Inches(2.5), C_PANEL, C_BORDER)
        add_text(slide, x + Inches(0.25), y + Inches(0.25), Inches(5.3), Inches(0.4),
                 title, size=18, bold=True, color=C_PRIMARY)
        add_text(slide, x + Inches(0.25), y + Inches(0.75), Inches(5.3), Inches(1.5),
                 desc, size=13, color=C_MUTED)
    footer(slide, n)
    return slide


def slide_features(prs, n):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, C_BG)
    header(slide, "Функциональность и соответствие ТЗ")
    rows = [
        ("Регистрация / авторизация", "Роли PARTICIPANT и ORGANIZER, JWT"),
        ("Создание квиза", "Категории, время на вопрос, правила проведения"),
        ("Типы вопросов", "Текст и изображение; один или несколько ответов"),
        ("Live-сессия", "Код комнаты, WebSocket, флаг isQuestionActive"),
        ("Баллы", "База 500 + бонус за скорость ответа"),
        ("Личный кабинет", "История участия и проведённых квизов"),
    ]
    y0 = Inches(1.2)
    for i, (req, impl) in enumerate(rows):
        y = y0 + Inches(i * 0.92)
        add_round_rect(slide, Inches(0.7), y, Inches(12), Inches(0.78), C_PANEL if i % 2 else C_HIGHLIGHT, C_BORDER)
        add_text(slide, Inches(0.95), y + Inches(0.12), Inches(4.5), Inches(0.5), req, size=13, bold=True)
        add_text(slide, Inches(5.5), y + Inches(0.12), Inches(7), Inches(0.5), impl, size=13, color=C_MUTED)
    footer(slide, n)
    return slide


def slide_stages(prs, n):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, C_BG)
    header(slide, "Этапы разработки")
    stages = [
        "1. UI-проектирование в Figma — 8 экранов + интерактивный прототип",
        "2. Модель БД — Prisma: User, Quiz, Question, Option, QuizSession, Answer",
        "3. Клиент — React 18 + Vite: 9 страниц по макетам",
        "4. Сервер — Node.js + Express, REST API, RBAC",
        "5. WebSocket — Socket.IO: комнаты, показ вопросов, ответы, лидерборд",
        "6. Тестирование — сценарий организатор + 3–5 участников",
    ]
    for i, text in enumerate(stages):
        y = Inches(1.25) + Inches(i * 0.95)
        add_round_rect(slide, Inches(0.7), y, Inches(0.55), Inches(0.55), C_PRIMARY)
        add_text(slide, Inches(0.7), y + Inches(0.08), Inches(0.55), Inches(0.4),
                 str(i + 1), size=16, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF), align=PP_ALIGN.CENTER)
        add_text(slide, Inches(1.45), y + Inches(0.1), Inches(11), Inches(0.5), text, size=14)
    footer(slide, n)
    return slide


def slide_stack(prs, n):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, C_BG)
    header(slide, "Технологический стек")
    stack = [
        ("UI-дизайн", "Figma", "Прототип до кода, согласование UX"),
        ("Клиент", "React 18 + Vite", "Популярный фреймворк, быстрая сборка"),
        ("Стили", "CSS variables", "Палитра #6c5ce7 по макетам"),
        ("Сервер", "Node.js + Express", "Единый язык с клиентом"),
        ("Real-time", "Socket.IO", "Комнаты, события, reconnect"),
        ("БД", "SQLite + Prisma", "MVP без отдельного сервера БД"),
        ("Auth", "JWT + bcrypt", "Роли и защита API"),
    ]
    y0 = Inches(1.15)
    for i, (layer, tech, why) in enumerate(stack):
        y = y0 + Inches(i * 0.82)
        add_text(slide, Inches(0.7), y, Inches(2.2), Inches(0.4), layer, size=12, bold=True, color=C_PRIMARY)
        add_round_rect(slide, Inches(2.9), y - Inches(0.05), Inches(2.4), Inches(0.42), C_HIGHLIGHT)
        add_text(slide, Inches(3.0), y, Inches(2.2), Inches(0.35), tech, size=12, bold=True)
        add_text(slide, Inches(5.5), y, Inches(7.2), Inches(0.4), why, size=12, color=C_MUTED)
    footer(slide, n)
    return slide


def slide_architecture(prs, n):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, C_BG)
    header(slide, "Архитектура системы", "client/server + REST + WebSocket")
    boxes = [
        (Inches(0.8), Inches(1.5), "Браузер", "React SPA\n9 маршрутов", C_HIGHLIGHT),
        (Inches(4.9), Inches(1.5), "API Server", "Express REST\nJWT auth", C_PANEL),
        (Inches(9.0), Inches(1.5), "Socket.IO", "Live-сессии\nкомнаты", C_PANEL),
        (Inches(4.9), Inches(4.0), "SQLite", "Prisma ORM\n7 моделей", C_PANEL),
    ]
    for x, y, title, body, fill in boxes:
        add_round_rect(slide, x, y, Inches(3.5), Inches(1.8), fill, C_BORDER)
        add_text(slide, x + Inches(0.2), y + Inches(0.2), Inches(3.1), Inches(0.4), title, size=16, bold=True, color=C_PRIMARY)
        add_text(slide, x + Inches(0.2), y + Inches(0.65), Inches(3.1), Inches(1), body, size=12, color=C_MUTED)
    add_text(slide, Inches(2.5), Inches(2.35), Inches(2), Inches(0.3), "HTTP /api", size=10, color=C_MUTED, align=PP_ALIGN.CENTER)
    add_text(slide, Inches(2.5), Inches(2.65), Inches(2), Inches(0.3), "WebSocket", size=10, color=C_MUTED, align=PP_ALIGN.CENTER)
    add_text(slide, Inches(6.5), Inches(3.45), Inches(2), Inches(0.3), "Prisma", size=10, color=C_MUTED, align=PP_ALIGN.CENTER)
    footer(slide, n)
    return slide


def slide_websocket(prs, n):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, C_BG)
    header(slide, "Real-time: события Socket.IO")
    events = [
        ("join_session", "Участник / организатор подключается к комнате"),
        ("start_session", "Организатор запускает квиз"),
        ("show_question", "Показ вопроса всем клиентам"),
        ("submit_answer", "Ответ участника (только при активном вопросе)"),
        ("end_question", "Закрытие приёма ответов"),
        ("end_session", "Финиш + рассылка лидерборда"),
    ]
    for i, (ev, desc) in enumerate(events):
        y = Inches(1.2) + Inches(i * 0.95)
        add_round_rect(slide, Inches(0.7), y, Inches(3.2), Inches(0.72), C_PRIMARY_DARK)
        add_text(slide, Inches(0.85), y + Inches(0.15), Inches(2.9), Inches(0.45),
                 ev, size=12, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))
        add_text(slide, Inches(4.1), y + Inches(0.15), Inches(8.5), Inches(0.45), desc, size=13)
    add_round_rect(slide, Inches(0.7), Inches(6.0), Inches(12), Inches(0.65), C_HIGHLIGHT, C_PRIMARY)
    add_text(slide, Inches(0.95), Inches(6.12), Inches(11.5), Inches(0.4),
             "Формула баллов: 500 + бонус за скорость (до +500 при мгновенном ответе)",
             size=12, bold=True, color=C_PRIMARY_DARK)
    footer(slide, n)
    return slide


def slide_figma(prs, n):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, C_BG)
    header(slide, "UI-дизайн в Figma")
    screens = [
        "Лендинг", "Регистрация / Вход", "Дашборд организатора",
        "Редактор вопросов", "Live-сессия (хост)", "Экран участника",
        "Лидерборд", "Личный кабинет", "Прототип переходов",
    ]
    for i, name in enumerate(screens):
        col, row = i % 3, i // 3
        x = Inches(0.7) + Inches(col * 4.1)
        y = Inches(1.25) + Inches(row * 1.85)
        add_round_rect(slide, x, y, Inches(3.7), Inches(1.55), C_PANEL, C_BORDER)
        add_rect(slide, x + Inches(0.15), y + Inches(0.15), Inches(3.4), Inches(0.85), C_HIGHLIGHT)
        add_text(slide, x + Inches(0.15), y + Inches(1.05), Inches(3.4), Inches(0.4),
                 name, size=12, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, Inches(0.7), Inches(6.15), Inches(12), Inches(0.4),
             f"Макеты: {FIGMA_URL}", size=11, color=C_PRIMARY)
    footer(slide, n)
    return slide


def slide_scenario(prs, n):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, C_BG)
    header(slide, "Сценарий демонстрации MVP")
    steps = [
        "Организатор регистрируется → создаёт квиз → добавляет вопросы в редакторе.",
        "Нажимает «Запустить» → получает код комнаты KVIZ-XXXXXX.",
        "Участники на других устройствах: «Войти в квиз» → ввод кода.",
        "Организатор: «Старт сессии» → «Следующий вопрос».",
        "Участники отвечают, пока вопрос активен (таймер на клиенте).",
        "«Завершить квиз» → лидерборд на экране итогов + история в профиле.",
    ]
    for i, text in enumerate(steps):
        y = Inches(1.2) + Inches(i * 0.95)
        add_round_rect(slide, Inches(0.7), y, Inches(0.5), Inches(0.5), C_SUCCESS)
        add_text(slide, Inches(0.7), y + Inches(0.06), Inches(0.5), Inches(0.38),
                 str(i + 1), size=14, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF), align=PP_ALIGN.CENTER)
        add_text(slide, Inches(1.4), y + Inches(0.08), Inches(11.2), Inches(0.45), text, size=14)
    footer(slide, n)
    return slide


def slide_artifacts(prs, n):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, C_BG)
    header(slide, "Артефакты проекта")
    items = [
        ("Макеты UI (Figma)", FIGMA_URL),
        ("Репозиторий GitHub", REPO_URL),
        ("Пояснительная записка", "docs/POYASNITELNAYA_ZAPISKA.md"),
        ("Рабочий прототип", DEMO_URL),
        ("Структура кода", "quiz-platform/client + quiz-platform/server"),
    ]
    for i, (label, url) in enumerate(items):
        y = Inches(1.3) + Inches(i * 1.1)
        add_round_rect(slide, Inches(0.7), y, Inches(12), Inches(0.95), C_PANEL, C_BORDER)
        add_text(slide, Inches(0.95), y + Inches(0.12), Inches(3.5), Inches(0.4), label, size=14, bold=True, color=C_PRIMARY)
        add_text(slide, Inches(4.5), y + Inches(0.12), Inches(7.8), Inches(0.5), url, size=12, color=C_MUTED)
    footer(slide, n)
    return slide


def slide_future(prs, n):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, C_BG)
    header(slide, "Итоги и перспективы")
    add_bullets(slide, Inches(0.7), Inches(1.15), Inches(5.8), Inches(5.5), [
        "Реализован работоспособный MVP по ТЗ.",
        "Организатор создаёт и ведёт квиз в реальном времени.",
        "Участники подключаются по коду без установки ПО.",
        "Данные сессий и баллов сохраняются в БД.",
        "Дизайн согласован с Figma-прототипом.",
    ], size=15)
    add_round_rect(slide, Inches(6.8), Inches(1.15), Inches(5.9), Inches(5.5), C_PANEL, C_BORDER)
    add_text(slide, Inches(7.05), Inches(1.35), Inches(5.4), Inches(0.4),
             "Дальнейшее развитие", size=16, bold=True, color=C_PRIMARY)
    add_bullets(slide, Inches(7.05), Inches(1.85), Inches(5.4), Inches(4.5), [
        "Деплой на Vercel + Railway",
        "CDN / облачное хранилище изображений",
        "OAuth / корпоративный SSO",
        "Мобильная адаптация 375px",
        "Аналитика и экспорт результатов",
    ], size=13, color=C_MUTED)
    footer(slide, n)
    return slide


def slide_thanks(prs, n):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, C_PRIMARY)
    add_text(slide, Inches(1), Inches(2.8), Inches(11.3), Inches(0.8),
             "Спасибо за внимание!", size=36, bold=True,
             color=RGBColor(0xFF, 0xFF, 0xFF), align=PP_ALIGN.CENTER)
    add_text(slide, Inches(1), Inches(3.8), Inches(11.3), Inches(0.5),
             "Вопросы?", size=22,
             color=RGBColor(0xDD, 0xD6, 0xFF), align=PP_ALIGN.CENTER)
    add_text(slide, Inches(1), Inches(4.8), Inches(11.3), Inches(0.8),
             f"{FIGMA_URL}\n{REPO_URL}",
             size=11, color=RGBColor(0xCC, 0xC8, 0xFF), align=PP_ALIGN.CENTER)
    footer(slide, n, total=TOTAL_SLIDES)
    return slide


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)

    slide_title(prs)
    slide_problem(prs, 2)
    slide_mvp_result(prs, 3)
    slide_features(prs, 4)
    slide_stages(prs, 5)
    slide_stack(prs, 6)
    slide_architecture(prs, 7)
    slide_websocket(prs, 8)
    slide_figma(prs, 9)
    slide_scenario(prs, 10)
    slide_app_screenshot(
        prs, 11,
        "Дашборд организатора",
        "01-dashboard.png",
        "Список квизов: создание, редактирование, запуск и удаление.",
    )
    slide_app_screenshot(
        prs, 12,
        "Редактор вопросов",
        "02-quiz-editor.png",
        "Демо-квиз с вопросами, отметкой правильных вариантов и загрузкой изображений.",
    )
    slide_app_screenshot(
        prs, 13,
        "Live-сессия",
        "03-host-session.png",
        "Код комнаты KVIZ-… для подключения участников в реальном времени.",
    )
    slide_artifacts(prs, 14)
    slide_future(prs, 15)
    slide_thanks(prs, 16)

    path = save_presentation(prs)
    print(f"Презентация создана: {path}")
    print(f"Слайдов: {len(prs.slides)}")


if __name__ == "__main__":
    build()
