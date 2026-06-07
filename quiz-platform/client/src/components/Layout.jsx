import { NavLink } from "react-router-dom";

export default function Layout({ children, title, action }) {
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  const isOrg = user.role === "ORGANIZER";

  return (
    <div className="app-shell">
      <div className="dashboard">
        <aside className="sidebar">
          <div className="logo" style={{ marginBottom: 24 }}>Квизы</div>
          {isOrg && <NavLink to="/dashboard" className={({ isActive }) => isActive ? "active" : ""}>Мои квизы</NavLink>}
          {isOrg && <NavLink to="/dashboard">Создать квиз</NavLink>}
          <NavLink to="/join">Войти в квиз</NavLink>
          <NavLink to="/profile" className={({ isActive }) => isActive ? "active" : ""}>Профиль</NavLink>
        </aside>
        <div className="main">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
            <h1 style={{ margin: 0, fontSize: 22 }}>{title}</h1>
            {action}
          </div>
          {children}
        </div>
      </div>
    </div>
  );
}
