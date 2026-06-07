import { Link } from "react-router-dom";

export default function Landing() {
  return (
    <div className="app-shell">
      <header className="topnav">
        <span className="logo">Квизы</span>
        <div>
          <Link to="/login" className="btn btn-secondary" style={{ marginRight: 8 }}>Войти</Link>
          <Link to="/register" className="btn btn-primary">Регистрация</Link>
        </div>
      </header>
      <main style={{ display: "flex", padding: "64px 80px", gap: 48, alignItems: "center" }}>
        <div style={{ flex: 1 }}>
          <h1 style={{ fontSize: 48, marginBottom: 20 }}>Корпоративные квизы в браузере</h1>
          <p style={{ fontSize: 18, color: "var(--muted)", lineHeight: 1.6 }}>
            Создавайте опросы, проводите live-сессии по коду комнаты, считайте баллы и показывайте лидерборд.
          </p>
          <div style={{ display: "flex", gap: 12, marginTop: 28 }}>
            <Link to="/register?role=organizer" className="btn btn-primary">Начать как организатор</Link>
            <Link to="/join" className="btn btn-secondary">Войти как участник</Link>
          </div>
        </div>
        <div className="card" style={{ width: 480 }}>
          <h3>Функции MVP</h3>
          <ul style={{ lineHeight: 2, color: "var(--muted)" }}>
            <li>Регистрация участников и организаторов</li>
            <li>Редактор вопросов (текст / изображение)</li>
            <li>Live по коду комнаты (WebSocket)</li>
            <li>Лидерборд и история</li>
          </ul>
        </div>
      </main>
    </div>
  );
}
