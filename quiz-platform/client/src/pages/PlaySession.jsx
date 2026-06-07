import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Layout from "../components/Layout";
import { getSocket } from "../socket";

export default function PlaySession() {
  const { sessionId } = useParams();
  const nav = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  const participantId = sessionStorage.getItem(`participant:${sessionId}`);

  const [status, setStatus] = useState("Ожидание старта…");
  const [question, setQuestion] = useState(null);
  const [selected, setSelected] = useState([]);
  const [timeLeft, setTimeLeft] = useState(0);
  const [canAnswer, setCanAnswer] = useState(false);
  const [feedback, setFeedback] = useState("");

  useEffect(() => {
    if (!participantId) {
      nav("/join");
      return;
    }

    const socket = getSocket();
    socket.emit("join_session", { sessionId, userId: user.id });

    socket.on("session_started", () => setStatus("Сессия началась. Ждём вопрос…"));
    socket.on("question_shown", ({ question: q, timeLimitSec }) => {
      setQuestion(q);
      setSelected([]);
      setCanAnswer(true);
      setFeedback("");
      setTimeLeft(timeLimitSec);
      setStatus(`Вопрос активен · ${timeLimitSec} сек`);
    });
    socket.on("question_ended", () => {
      setCanAnswer(false);
      setStatus("Вопрос завершён");
    });
    socket.on("answer_accepted", ({ isCorrect, points }) => {
      setFeedback(isCorrect ? `Верно! +${points} баллов` : "Неверно");
      setCanAnswer(false);
    });
    socket.on("session_ended", ({ leaderboard }) => {
      sessionStorage.setItem(`leaderboard:${sessionId}`, JSON.stringify(leaderboard));
      nav(`/results/${sessionId}`);
    });
    socket.on("error_message", ({ message }) => setFeedback(message));

    return () => {
      socket.off("session_started");
      socket.off("question_shown");
      socket.off("question_ended");
      socket.off("answer_accepted");
      socket.off("session_ended");
      socket.off("error_message");
    };
  }, [sessionId, participantId, user.id, nav]);

  useEffect(() => {
    if (!canAnswer || timeLeft <= 0) return;
    const t = setInterval(() => setTimeLeft((s) => Math.max(0, s - 1)), 1000);
    return () => clearInterval(t);
  }, [canAnswer, timeLeft, question?.id]);

  function toggleOption(id) {
    if (!canAnswer || !question) return;
    if (question.answerType === "SINGLE") {
      setSelected([id]);
    } else {
      setSelected((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
    }
  }

  function submit() {
    if (!canAnswer || !question || selected.length === 0) return;
    getSocket().emit("submit_answer", {
      sessionId,
      participantId,
      questionId: question.id,
      optionIds: selected,
      timeLeftSec: timeLeft,
    });
  }

  return (
    <Layout title={`Участник · ${user.name || ""}`}>
      <p style={{ color: "var(--muted)" }}>{status}</p>
      {question && (
        <div className="card">
          <h2>{question.text}</h2>
          {question.imageUrl && <img src={question.imageUrl} alt="" style={{ maxWidth: "100%", borderRadius: 8 }} />}
          {canAnswer && <p>Осталось: {timeLeft} сек</p>}
          {question.options.map((o) => (
            <div
              key={o.id}
              className={`option ${selected.includes(o.id) ? "selected" : ""}`}
              onClick={() => toggleOption(o.id)}
            >
              {o.text}
            </div>
          ))}
          {canAnswer && (
            <button className="btn btn-primary" style={{ marginTop: 12 }} onClick={submit} disabled={selected.length === 0}>
              Отправить ответ
            </button>
          )}
          {feedback && <p style={{ marginTop: 12, color: feedback.startsWith("Верно") ? "var(--success)" : "var(--accent)" }}>{feedback}</p>}
        </div>
      )}
    </Layout>
  );
}
