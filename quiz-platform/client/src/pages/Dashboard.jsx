import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import { quizzes, sessions } from "../api";

export default function Dashboard() {
  const [list, setList] = useState([]);
  const nav = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "{}");

  useEffect(() => {
    if (user.role !== "ORGANIZER") nav("/join");
  }, [user.role, nav]);

  useEffect(() => {
    quizzes.list().then(setList).catch(console.error);
  }, []);

  async function createQuiz() {
    const q = await quizzes.create({
      title: "Новый квиз",
      categories: ["Общие"],
      timePerQuestionSec: 30,
      answersOnlyWhenShown: true,
    });
    nav(`/quiz/${q.id}/edit`);
  }

  async function launch(quizId) {
    const s = await sessions.create(quizId);
    nav(`/host/${s.id}`);
  }

  return (
    <Layout title="Мои квизы" action={<button className="btn btn-primary" onClick={createQuiz}>+ Новый квиз</button>}>
      {list.map((q) => (
        <div className="card" key={q.id}>
          <h3>{q.title}</h3>
          <p style={{ color: "var(--muted)" }}>{q.questions?.length || 0} вопросов</p>
          <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
            <Link to={`/quiz/${q.id}/edit`} className="btn btn-secondary">Редактор</Link>
            <button className="btn btn-primary" onClick={() => launch(q.id)}>Запустить</button>
          </div>
        </div>
      ))}
    </Layout>
  );
}
