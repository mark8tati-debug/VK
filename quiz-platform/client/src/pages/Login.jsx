import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { auth } from "../api";

export default function Login() {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");

  async function submit(e) {
    e.preventDefault();
    try {
      const { token, user } = await auth.login({ email, password });
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
        <div className="promo">
          <h2>Квизы для команд</h2>
          <p>Управляйте квизами и анализируйте результаты в веб-приложении.</p>
        </div>
        <form className="auth-form" onSubmit={submit}>
          <h1>Вход</h1>
          {err && <p style={{ color: "var(--accent)" }}>{err}</p>}
          <div className="field"><label>Email</label><input value={email} onChange={(e) => setEmail(e.target.value)} /></div>
          <div className="field"><label>Пароль</label><input type="password" value={password} onChange={(e) => setPassword(e.target.value)} /></div>
          <button className="btn btn-primary btn-block" type="submit">Войти</button>
          <p style={{ marginTop: 16 }}>Нет аккаунта? <Link to="/register">Зарегистрироваться</Link></p>
        </form>
      </div>
    </div>
  );
}
