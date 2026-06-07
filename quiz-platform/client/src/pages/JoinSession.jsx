import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import { sessions } from "../api";

export default function JoinSession() {
  const nav = useNavigate();
  const [code, setCode] = useState("");
  const [err, setErr] = useState("");

  async function join(e) {
    e.preventDefault();
    try {
      const { session, participant } = await sessions.join(code.trim().toUpperCase());
      sessionStorage.setItem(`participant:${session.id}`, participant.id);
      nav(`/play/${session.id}`);
    } catch (ex) {
      setErr(ex.message);
    }
  }

  return (
    <Layout title="Войти в квиз">
      <div className="card" style={{ maxWidth: 480 }}>
        <p style={{ color: "var(--muted)" }}>Введите код комнаты от организатора (например KVIZ-ABC123)</p>
        {err && <p style={{ color: "var(--accent)" }}>{err}</p>}
        <form onSubmit={join}>
          <div className="field">
            <label>Код комнаты</label>
            <input value={code} onChange={(e) => setCode(e.target.value)} placeholder="KVIZ-XXXXXX" required />
          </div>
          <button className="btn btn-primary btn-block" type="submit">Подключиться</button>
        </form>
      </div>
    </Layout>
  );
}
