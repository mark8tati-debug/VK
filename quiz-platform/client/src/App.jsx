import { Routes, Route, Navigate } from "react-router-dom";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import QuizEdit from "./pages/QuizEdit";
import HostSession from "./pages/HostSession";
import JoinSession from "./pages/JoinSession";
import PlaySession from "./pages/PlaySession";
import Results from "./pages/Results";
import Profile from "./pages/Profile";

function PrivateRoute({ children }) {
  return localStorage.getItem("token") ? children : <Navigate to="/login" />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
      <Route path="/quiz/:id/edit" element={<PrivateRoute><QuizEdit /></PrivateRoute>} />
      <Route path="/host/:sessionId" element={<PrivateRoute><HostSession /></PrivateRoute>} />
      <Route path="/join" element={<PrivateRoute><JoinSession /></PrivateRoute>} />
      <Route path="/play/:sessionId" element={<PrivateRoute><PlaySession /></PrivateRoute>} />
      <Route path="/results/:sessionId" element={<PrivateRoute><Results /></PrivateRoute>} />
      <Route path="/profile" element={<PrivateRoute><Profile /></PrivateRoute>} />
    </Routes>
  );
}
