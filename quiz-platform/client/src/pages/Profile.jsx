import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import { sessions } from "../api";

export default function Profile() {
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  const nav = useNavigate();
  const [history, setHistory] = useState(null);

  useEffect(() => {
    sessions.history().then(setHistory).catch(console.error);
  }, []);

  function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    nav("/");
  }

  return (
    <Layout title="Личный кабинет">
      <div className="card">
        <h3>{user.name}</h3>
        <p style={{ color: "var(--muted)" }}>{user.email} · {user.role === "ORGANIZER" ? "Организатор" : "Участник"}</p>
        <button className="btn btn-secondary" style={{ marginTop: 12 }} onClick={logout}>Выйти</button>
      </div>

      <h3>История</h3>
      {!history && <p>Загрузка…</p>}
      {history?.type === "organizer" && history.sessions.map((s) => (
        <div className="card" key={s.id}>
          <strong>{s.quiz.title}</strong>
          <p style={{ color: "var(--muted)", fontSize: 13 }}>{s.roomCode} · {s.status}</p>
        </div>
      ))}
      {history?.type === "participant" && history.participations.map((p) => (
        <div className="card" key={p.id}>
          <strong>{p.session.quiz.title}</strong>
          <p style={{ color: "var(--muted)", fontSize: 13 }}>Счёт: {p.score}</p>
        </div>
      ))}
    </Layout>
  );
}
