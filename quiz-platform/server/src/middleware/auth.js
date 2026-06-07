import jwt from "jsonwebtoken";

export function requireAuth(req, res, next) {
  const header = req.headers.authorization;
  if (!header?.startsWith("Bearer ")) {
    return res.status(401).json({ error: "Требуется авторизация" });
  }
  try {
    req.user = jwt.verify(header.slice(7), process.env.JWT_SECRET);
    next();
  } catch {
    res.status(401).json({ error: "Недействительный токен" });
  }
}

export function requireOrganizer(req, res, next) {
  if (req.user?.role !== "ORGANIZER") {
    return res.status(403).json({ error: "Доступ только для организатора" });
  }
  next();
}
