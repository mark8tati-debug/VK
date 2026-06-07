# -*- coding: utf-8 -*-
"""Создаёт демо-квиз через API и делает скриншоты приложения."""

import json
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / "docs" / "screenshots"
API = "http://localhost:3001/api"
CLIENT = "http://localhost:5174"

ORG = {
    "name": "Демо Организатор",
    "email": "demo-org@quiz.local",
    "password": "demo12345",
    "role": "ORGANIZER",
}


def api(method, path, token=None, **kwargs):
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.request(method, f"{API}{path}", headers=headers, timeout=15, **kwargs)
    data = r.json() if r.content else {}
    if not r.ok:
        raise RuntimeError(data.get("error") or f"{method} {path} → {r.status_code}")
    return data


def ensure_organizer():
    try:
        data = api("POST", "/auth/register", json=ORG)
    except RuntimeError:
        data = api("POST", "/auth/login", json={"email": ORG["email"], "password": ORG["password"]})
    return data["token"], data["user"]


def seed_quiz(token):
    quizzes = api("GET", "/quizzes", token)
    for q in quizzes:
        if q["title"] == "Демо-квиз для презентации":
            api("DELETE", f"/quizzes/{q['id']}", token)
            break

    quiz = api(
        "POST",
        "/quizzes",
        token,
        json={
            "title": "Демо-квиз для презентации",
            "categories": ["Общие", "Команда"],
            "timePerQuestionSec": 30,
            "answersOnlyWhenShown": True,
        },
    )

    questions = [
        {
            "text": "Какой год основания компании?",
            "answerType": "SINGLE",
            "options": [
                {"text": "2018", "isCorrect": False},
                {"text": "2020", "isCorrect": True},
                {"text": "2022", "isCorrect": False},
                {"text": "2024", "isCorrect": False},
            ],
        },
        {
            "text": "Какие инструменты использует команда? (несколько ответов)",
            "answerType": "MULTIPLE",
            "options": [
                {"text": "React", "isCorrect": True},
                {"text": "Figma", "isCorrect": True},
                {"text": "Excel", "isCorrect": False},
                {"text": "Socket.IO", "isCorrect": True},
            ],
        },
        {
            "text": "Главный принцип проведения квиза в MVP?",
            "answerType": "SINGLE",
            "options": [
                {"text": "Ответы только при показе вопроса", "isCorrect": True},
                {"text": "Ответы в любое время", "isCorrect": False},
                {"text": "Без таймера", "isCorrect": False},
                {"text": "Только офлайн", "isCorrect": False},
            ],
        },
    ]

    for q in questions:
        api("POST", f"/quizzes/{quiz['id']}/questions", token, json={**q, "type": "TEXT"})

    session = api("POST", "/sessions", token, json={"quizId": quiz["id"]})
    return quiz["id"], session["id"], session.get("roomCode", "")


def capture_with_playwright(token, user, quiz_id, session_id):
    from playwright.sync_api import sync_playwright

    SHOTS.mkdir(parents=True, exist_ok=True)
    auth = {"token": token, "user": user}

    shots = {
        "01-dashboard.png": f"{CLIENT}/dashboard",
        "02-quiz-editor.png": f"{CLIENT}/quiz/{quiz_id}/edit",
        "03-host-session.png": f"{CLIENT}/host/{session_id}",
    }

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        page.goto(CLIENT)
        page.evaluate(
            """([t, u]) => {
                localStorage.setItem('token', t);
                localStorage.setItem('user', JSON.stringify(u));
            }""",
            [auth["token"], auth["user"]],
        )

        for name, url in shots.items():
            page.goto(url, wait_until="networkidle")
            time.sleep(0.8)
            page.screenshot(path=str(SHOTS / name), full_page=False)

        browser.close()

    return list(shots.keys())


def wait_services():
    for url in ("http://localhost:3001/api/health", CLIENT):
        for _ in range(20):
            try:
                if requests.get(url, timeout=2).status_code < 500:
                    break
            except requests.RequestException:
                time.sleep(0.5)
        else:
            print(
                "Запустите сервер и клиент:\n"
                "  cd quiz-platform/server && npm run dev\n"
                "  cd quiz-platform/client && npm run dev",
                file=sys.stderr,
            )
            sys.exit(1)


def main():
    wait_services()

    token, user = ensure_organizer()
    quiz_id, session_id, room = seed_quiz(token)
    print(f"Демо-квиз создан: {quiz_id}, сессия: {session_id}, код: {room}")

    try:
        files = capture_with_playwright(token, user, quiz_id, session_id)
    except ImportError:
        print("Установите Playwright: pip install playwright && playwright install chromium", file=sys.stderr)
        sys.exit(1)

    meta = {"quizId": quiz_id, "sessionId": session_id, "roomCode": room, "screenshots": files}
    (SHOTS / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Скриншоты сохранены: {SHOTS}")
    for f in files:
        print(f"  - {f}")


if __name__ == "__main__":
    main()
