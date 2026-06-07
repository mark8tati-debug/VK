import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Layout from "../components/Layout";
import { sessions } from "../api";

export default function Results() {
  const { sessionId } = useParams();
  const [rows, setRows] = useState([]);

  useEffect(() => {
    const cached = sessionStorage.getItem(`leaderboard:${sessionId}`);
    if (cached) {
      setRows(JSON.parse(cached));
      return;
    }
    sessions.leaderboard(sessionId).then(setRows).catch(console.error);
  }, [sessionId]);

  return (
    <Layout title="Итоги квиза">
      <div className="card">
        <h3>Лидерборд</h3>
        {rows.length === 0 && <p style={{ color: "var(--muted)" }}>Нет данных</p>}
        {rows.map((r) => (
          <div className="leaderboard-row" key={r.place}>
            <span>#{r.place} {r.name}</span>
            <strong>{r.score} баллов</strong>
          </div>
        ))}
      </div>
      <Link to="/profile" className="btn btn-secondary">В личный кабинет</Link>
    </Layout>
  );
}
