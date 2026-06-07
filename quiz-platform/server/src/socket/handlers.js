function room(sessionId) {
  return `session:${sessionId}`;
}

function calcPoints(isCorrect, timeLeftSec, maxSec) {
  if (!isCorrect) return 0;
  const base = 500;
  const speedBonus = Math.round((timeLeftSec / maxSec) * 500);
  return base + speedBonus;
}

export function registerSocketHandlers(io, prisma) {
  io.on("connection", (socket) => {
    socket.on("join_session", async ({ sessionId, userId }) => {
      socket.join(room(sessionId));
      socket.data.sessionId = sessionId;
      socket.data.userId = userId;
      const participants = await prisma.sessionParticipant.count({ where: { sessionId } });
      io.to(room(sessionId)).emit("participant_count", { count: participants });
    });

    socket.on("start_session", async ({ sessionId }) => {
      await prisma.quizSession.update({
        where: { id: sessionId },
        data: { status: "ACTIVE", startedAt: new Date(), currentQuestionIdx: -1, isQuestionActive: false },
      });
      io.to(room(sessionId)).emit("session_started", { sessionId });
    });

    socket.on("show_question", async ({ sessionId, questionIndex }) => {
      const session = await prisma.quizSession.findUnique({
        where: { id: sessionId },
        include: { quiz: { include: { questions: { include: { options: true }, orderBy: { orderIndex: "asc" } } } } },
      });
      if (!session) return;
      const question = session.quiz.questions[questionIndex];
      if (!question) return;

      await prisma.quizSession.update({
        where: { id: sessionId },
        data: { currentQuestionIdx: questionIndex, isQuestionActive: true },
      });

      io.to(room(sessionId)).emit("question_shown", {
        questionIndex,
        question: {
          id: question.id,
          text: question.text,
          type: question.type,
          imageUrl: question.imageUrl,
          answerType: question.answerType,
          options: question.options.map((o) => ({ id: o.id, text: o.text })),
        },
        timeLimitSec: session.quiz.timePerQuestionSec,
      });
    });

    socket.on("submit_answer", async ({ sessionId, participantId, questionId, optionIds, timeLeftSec }) => {
      const session = await prisma.quizSession.findUnique({
        where: { id: sessionId },
        include: { quiz: true },
      });
      if (!session?.isQuestionActive) {
        return socket.emit("error_message", { message: "Ответы принимаются только во время демонстрации" });
      }

      const question = await prisma.question.findUnique({
        where: { id: questionId },
        include: { options: true },
      });
      const correctIds = question.options.filter((o) => o.isCorrect).map((o) => o.id).sort();
      const selected = [...optionIds].sort();
      const isCorrect =
        correctIds.length === selected.length && correctIds.every((id, i) => id === selected[i]);

      const points = calcPoints(isCorrect, timeLeftSec, session.quiz.timePerQuestionSec);

      await prisma.answer.upsert({
        where: { participantId_questionId: { participantId, questionId } },
        create: { sessionId, participantId, questionId, optionIds: JSON.stringify(optionIds), isCorrect, points },
        update: { optionIds: JSON.stringify(optionIds), isCorrect, points, answeredAt: new Date() },
      });

      await prisma.sessionParticipant.update({
        where: { id: participantId },
        data: { score: { increment: points } },
      });

      socket.emit("answer_accepted", { isCorrect, points });
    });

    socket.on("end_question", async ({ sessionId }) => {
      await prisma.quizSession.update({
        where: { id: sessionId },
        data: { isQuestionActive: false },
      });
      io.to(room(sessionId)).emit("question_ended", {});
    });

    socket.on("end_session", async ({ sessionId }) => {
      await prisma.quizSession.update({
        where: { id: sessionId },
        data: { status: "FINISHED", endedAt: new Date(), isQuestionActive: false },
      });
      const leaderboard = await prisma.sessionParticipant.findMany({
        where: { sessionId },
        include: { user: { select: { name: true } } },
        orderBy: { score: "desc" },
      });
      io.to(room(sessionId)).emit("session_ended", {
        leaderboard: leaderboard.map((r, i) => ({ place: i + 1, name: r.user.name, score: r.score })),
      });
    });
  });
}
