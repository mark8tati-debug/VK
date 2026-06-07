import "dotenv/config";
import http from "http";
import express from "express";
import cors from "cors";
import { Server } from "socket.io";
import { PrismaClient } from "@prisma/client";
import authRoutes from "./routes/auth.js";
import quizRoutes from "./routes/quizzes.js";
import sessionRoutes from "./routes/sessions.js";
import { registerSocketHandlers } from "./socket/handlers.js";

const prisma = new PrismaClient();
const app = express();
const server = http.createServer(app);

const io = new Server(server, {
  cors: { origin: process.env.CLIENT_URL || "http://localhost:5173", methods: ["GET", "POST"] },
});

app.use(cors({ origin: process.env.CLIENT_URL || "http://localhost:5173" }));
app.use(express.json());
app.set("prisma", prisma);
app.set("io", io);

app.get("/api/health", (_req, res) => res.json({ ok: true }));
app.use("/api/auth", authRoutes);
app.use("/api/quizzes", quizRoutes);
app.use("/api/sessions", sessionRoutes);

registerSocketHandlers(io, prisma);

const port = Number(process.env.PORT) || 3001;
server.listen(port, () => console.log(`Quiz API + Socket.IO → http://localhost:${port}`));
