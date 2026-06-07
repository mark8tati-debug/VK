import { Router } from "express";
import { customAlphabet } from "nanoid";
import { requireAuth, requireOrganizer } from "../middleware/auth.js";

const router = Router();
const genCode = customAlphabet("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", 6);

router.post("/", requireAuth, requireOrganizer, async (req, res) => {
  const prisma = req.app.get("prisma");
  const { quizId } = req.body;
  const quiz = await prisma.quiz.findFirst({
    where: { id: quizId, organizerId: req.user.id },
  });
  if (!quiz) return res.status(404).json({ error: "Квиз не найден" });

  let roomCode;
  do {
    roomCode = `KVIZ-${genCode()}`;
  } while (await prisma.quizSession.findUnique({ where: { roomCode } }));

  const session = await prisma.quizSession.create({
    data: { quizId, roomCode, status: "WAITING" },
    include: { quiz: { include: { questions: { include: { options: true } } } } },
  });
  res.status(201).json(session);
});

router.post("/join", requireAuth, async (req, res) => {
  const prisma = req.app.get("prisma");
  const { roomCode } = req.body;
  const session = await prisma.quizSession.findUnique({
    where: { roomCode: roomCode?.toUpperCase() },
    include: { quiz: true },
  });
  if (!session || session.status === "FINISHED") {
    return res.status(404).json({ error: "Комната не найдена или сессия завершена" });
  }

  const participant = await prisma.sessionParticipant.upsert({
    where: { sessionId_userId: { sessionId: session.id, userId: req.user.id } },
    create: { sessionId: session.id, userId: req.user.id },
    update: {},
    include: { user: { select: { id: true, name: true } } },
  });
  res.json({ session, participant });
});

router.get("/:id/leaderboard", requireAuth, async (req, res) => {
  const prisma = req.app.get("prisma");
  const rows = await prisma.sessionParticipant.findMany({
    where: { sessionId: req.params.id },
    include: { user: { select: { id: true, name: true } } },
    orderBy: { score: "desc" },
  });
  res.json(rows.map((r, i) => ({ place: i + 1, name: r.user.name, score: r.score, userId: r.user.id })));
});

router.get("/history/me", requireAuth, async (req, res) => {
  const prisma = req.app.get("prisma");
  if (req.user.role === "ORGANIZER") {
    const sessions = await prisma.quizSession.findMany({
      where: { quiz: { organizerId: req.user.id } },
      include: { quiz: { select: { title: true } } },
      orderBy: { createdAt: "desc" },
      take: 20,
    });
    return res.json({ type: "organizer", sessions });
  }
  const parts = await prisma.sessionParticipant.findMany({
    where: { userId: req.user.id },
    include: { session: { include: { quiz: { select: { title: true } } } } },
    orderBy: { joinedAt: "desc" },
    take: 20,
  });
  res.json({ type: "participant", participations: parts });
});

router.get("/:id", requireAuth, async (req, res) => {
  const prisma = req.app.get("prisma");
  const session = await prisma.quizSession.findUnique({
    where: { id: req.params.id },
    include: {
      quiz: {
        include: { questions: { include: { options: true }, orderBy: { orderIndex: "asc" } } },
      },
      participants: { include: { user: { select: { id: true, name: true } } } },
    },
  });
  if (!session) return res.status(404).json({ error: "Сессия не найдена" });
  const isOwner = session.quiz.organizerId === req.user.id;
  const joined = session.participants.some((p) => p.userId === req.user.id);
  if (!isOwner && !joined) return res.status(403).json({ error: "Нет доступа" });
  res.json(session);
});

export default router;
