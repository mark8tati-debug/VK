import { Router } from "express";
import { requireAuth, requireOrganizer } from "../middleware/auth.js";

const router = Router();

router.get("/", requireAuth, async (req, res) => {
  const prisma = req.app.get("prisma");
  const where = req.user.role === "ORGANIZER" ? { organizerId: req.user.id } : {};
  const quizzes = await prisma.quiz.findMany({
    where,
    include: { questions: { include: { options: true }, orderBy: { orderIndex: "asc" } } },
    orderBy: { updatedAt: "desc" },
  });
  res.json(quizzes);
});

router.post("/", requireAuth, requireOrganizer, async (req, res) => {
  const prisma = req.app.get("prisma");
  const {
    title,
    description,
    categories = [],
    timePerQuestionSec = 30,
    pauseBetweenSec = 5,
    answersOnlyWhenShown = true,
  } = req.body;

  const quiz = await prisma.quiz.create({
    data: {
      title,
      description,
      categories: JSON.stringify(categories),
      timePerQuestionSec,
      pauseBetweenSec,
      answersOnlyWhenShown,
      organizerId: req.user.id,
    },
  });
  res.status(201).json(quiz);
});

router.patch("/:id", requireAuth, requireOrganizer, async (req, res) => {
  const prisma = req.app.get("prisma");
  const quiz = await prisma.quiz.findFirst({
    where: { id: req.params.id, organizerId: req.user.id },
  });
  if (!quiz) return res.status(404).json({ error: "Квиз не найден" });

  const { title, description, categories, timePerQuestionSec, pauseBetweenSec, answersOnlyWhenShown } = req.body;
  if (title !== undefined && !String(title).trim()) {
    return res.status(400).json({ error: "Название квиза не может быть пустым" });
  }

  const data = {};
  if (title !== undefined) data.title = String(title).trim();
  if (description !== undefined) data.description = description;
  if (categories !== undefined) data.categories = JSON.stringify(categories);
  if (timePerQuestionSec !== undefined) data.timePerQuestionSec = timePerQuestionSec;
  if (pauseBetweenSec !== undefined) data.pauseBetweenSec = pauseBetweenSec;
  if (answersOnlyWhenShown !== undefined) data.answersOnlyWhenShown = answersOnlyWhenShown;

  const updated = await prisma.quiz.update({
    where: { id: quiz.id },
    data,
    include: { questions: { include: { options: true }, orderBy: { orderIndex: "asc" } } },
  });
  res.json(updated);
});

router.get("/:id", requireAuth, async (req, res) => {
  const prisma = req.app.get("prisma");
  const quiz = await prisma.quiz.findUnique({
    where: { id: req.params.id },
    include: { questions: { include: { options: true }, orderBy: { orderIndex: "asc" } } },
  });
  if (!quiz) return res.status(404).json({ error: "Квиз не найден" });
  res.json(quiz);
});

router.post("/:id/questions", requireAuth, requireOrganizer, async (req, res) => {
  const prisma = req.app.get("prisma");
  const quiz = await prisma.quiz.findFirst({
    where: { id: req.params.id, organizerId: req.user.id },
  });
  if (!quiz) return res.status(404).json({ error: "Квиз не найден" });

  const { text, type = "TEXT", imageUrl, answerType = "SINGLE", options = [] } = req.body;
  const count = await prisma.question.count({ where: { quizId: quiz.id } });
  const questionType = imageUrl ? "IMAGE" : type;

  const question = await prisma.question.create({
    data: {
      quizId: quiz.id,
      orderIndex: count,
      text,
      type: questionType,
      imageUrl: imageUrl || null,
      answerType,
      options: {
        create: options.map((o, i) => ({
          text: o.text,
          isCorrect: !!o.isCorrect,
          orderIndex: i,
        })),
      },
    },
    include: { options: true },
  });
  res.status(201).json(question);
});

router.delete("/:id", requireAuth, requireOrganizer, async (req, res) => {
  const prisma = req.app.get("prisma");
  const quiz = await prisma.quiz.findFirst({
    where: { id: req.params.id, organizerId: req.user.id },
  });
  if (!quiz) return res.status(404).json({ error: "Квиз не найден" });

  const sessionIds = (
    await prisma.quizSession.findMany({ where: { quizId: quiz.id }, select: { id: true } })
  ).map((s) => s.id);

  if (sessionIds.length) {
    await prisma.answer.deleteMany({ where: { sessionId: { in: sessionIds } } });
    await prisma.sessionParticipant.deleteMany({ where: { sessionId: { in: sessionIds } } });
    await prisma.quizSession.deleteMany({ where: { quizId: quiz.id } });
  }

  await prisma.quiz.delete({ where: { id: quiz.id } });
  res.json({ ok: true });
});

export default router;
