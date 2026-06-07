import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { auth } from "../api";

export default function Register() {
  const nav = useNavigate();
  const [params] = useSearchParams();
  const [role, setRole] = useState(params.get("role") === "organizer" ? "ORGANIZER" : "PARTICIPANT");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");

  async function submit(e) {
    e.preventDefault();
    try {
      const { token, user } = await auth.register({ name, email, password, role });
      localStorage.setItem("token", token);
      localStorage.setItem("user", JSON.stringify(user));
      nav(user.role === "ORGANIZER" ? "/dashboard" : "/join");
    } catch (ex) {
      setErr(ex.message);
    }
  }

  return (
    <div className="app-shell">
      <header className="topnav"><span className="logo">Квизы</span></header>
      <div className="split-auth">
        <div className="promo"><h2>Регистрация</h2><p>Единый вход для участников и организаторов.</p></div>
        <form className="auth-form" onSubmit={submit}>
          <h1>Регистрация</h1>
          <div className="tabs">
            <div className={`tab ${role === "PARTICIPANT" ? "active" : ""}`} onClick={() => setRole("PARTICIPANT")}>Участник</div>
            <div className={`tab ${role === "ORGANIZER" ? "active" : ""}`} onClick={() => setRole("ORGANIZER")}>Организатор</div>
          </div>
          {err && <p style={{ color: "var(--accent)" }}>{err}</p>}
          <div className="field"><label>Имя</label><input value={name} onChange={(e) => setName(e.target.value)} required /></div>
          <div className="field"><label>Email</label><input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></div>
          <div className="field"><label>Пароль</label><input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required /></div>
          <button className="btn btn-primary btn-block" type="submit">Зарегистрироваться</button>
          <p style={{ marginTop: 16 }}><Link to="/login">Уже есть аккаунт? Войти</Link></p>
        </form>
      </div>
    </div>
  );
}
