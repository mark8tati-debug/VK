import { Router } from "express";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";

const router = Router();

router.post("/register", async (req, res) => {
  const prisma = req.app.get("prisma");
  const { email, password, name, role = "PARTICIPANT" } = req.body;
  if (!email || !password || !name) {
    return res.status(400).json({ error: "Заполните email, имя и пароль" });
  }
  const exists = await prisma.user.findUnique({ where: { email } });
  if (exists) return res.status(409).json({ error: "Email уже зарегистрирован" });

  const user = await prisma.user.create({
    data: {
      email,
      name,
      role: role === "ORGANIZER" ? "ORGANIZER" : "PARTICIPANT",
      passwordHash: await bcrypt.hash(password, 10),
    },
  });
  const token = jwt.sign(
    { id: user.id, email: user.email, role: user.role, name: user.name },
    process.env.JWT_SECRET,
    { expiresIn: "7d" }
  );
  res.status(201).json({ token, user: { id: user.id, email: user.email, name: user.name, role: user.role } });
});

router.post("/login", async (req, res) => {
  const prisma = req.app.get("prisma");
  const { email, password } = req.body;
  const user = await prisma.user.findUnique({ where: { email } });
  if (!user || !(await bcrypt.compare(password, user.passwordHash))) {
    return res.status(401).json({ error: "Неверный email или пароль" });
  }
  const token = jwt.sign(
    { id: user.id, email: user.email, role: user.role, name: user.name },
    process.env.JWT_SECRET,
    { expiresIn: "7d" }
  );
  res.json({ token, user: { id: user.id, email: user.email, name: user.name, role: user.role } });
});

export default router;
