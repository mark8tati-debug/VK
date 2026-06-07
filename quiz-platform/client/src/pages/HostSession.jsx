import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import { sessions } from "../api";
import { getSocket } from "../socket";

export default function HostSession() {
  const { sessionId } = useParams();
  const nav = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  const [session, setSession] = useState(null);
  const [idx, setIdx] = useState(-1);
  const [participants, setParticipants] = useState(0);

  useEffect(() => {
    sessions.get(sessionId).then(setSession).catch(console.error);

    const socket = getSocket();
    socket.emit("join_session", { sessionId, userId: user.id });
    socket.on("participant_count", ({ count }) => setParticipants(count));

    return () => socket.off("participant_count");
  }, [sessionId, user.id]);

  function start() {
    getSocket().emit("start_session", { sessionId });
  }

  function showNext() {
    const next = idx + 1;
    if (!session?.quiz?.questions?.[next]) return;
    setIdx(next);
    getSocket().emit("show_question", { sessionId, questionIndex: next });
  }

  function endQuestion() {
    getSocket().emit("end_question", { sessionId });
  }

  function finish() {
    getSocket().emit("end_session", { sessionId });
    nav(`/results/${sessionId}`);
  }

  if (!session) {
    return <Layout title="Live-сессия"><p>Загрузка…</p></Layout>;
  }

  const q = session.quiz?.questions?.[idx];
  const total = session.quiz?.questions?.length || 0;

  return (
    <Layout title="Live-сессия">
      <div className="card">
        <p>Код комнаты · участников: {participants}</p>
        <div className="code">{session.roomCode}</div>
        <p style={{ color: "var(--muted)", fontSize: 13 }}>Передайте код участникам для входа на странице «Войти в квиз»</p>
      </div>
      <div className="card" style={{ background: "#2a3558", color: "#fff" }}>
        {q ? (
          <>
            <p>Вопрос {idx + 1} из {total}</p>
            <h2>{q.text}</h2>
          </>
        ) : (
          <p>Нажмите «Следующий вопрос», чтобы показать задание участникам</p>
        )}
      </div>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <button className="btn btn-primary" onClick={start}>Старт сессии</button>
        <button className="btn btn-primary" onClick={showNext} disabled={idx + 1 >= total}>Следующий вопрос</button>
        <button className="btn btn-secondary" onClick={endQuestion}>Закрыть ответы</button>
        <button className="btn btn-secondary" onClick={finish}>Завершить квиз</button>
      </div>
    </Layout>
  );
}
