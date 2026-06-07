import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Layout from "../components/Layout";
import { quizzes } from "../api";

export default function QuizEdit() {
  const { id } = useParams();
  const [quiz, setQuiz] = useState(null);
  const [text, setText] = useState("");
  const [answerType, setAnswerType] = useState("SINGLE");
  const [options, setOptions] = useState(["Вариант A", "Вариант B", "Вариант C"]);

  useEffect(() => {
    quizzes.get(id).then(setQuiz);
  }, [id]);

  async function addQuestion() {
    await quizzes.addQuestion(id, {
      text,
      type: "TEXT",
      answerType,
      options: options.map((t, i) => ({ text: t, isCorrect: i === 1 })),
    });
    setQuiz(await quizzes.get(id));
    setText("");
  }

  if (!quiz) return null;

  return (
    <Layout title={`Редактор · ${quiz.title}`}>
      <div className="card">
        <h3>Новый вопрос</h3>
        <div className="field"><label>Текст вопроса</label><input value={text} onChange={(e) => setText(e.target.value)} /></div>
        <div className="field">
          <label>Тип ответа</label>
          <select value={answerType} onChange={(e) => setAnswerType(e.target.value)}>
            <option value="SINGLE">Один ответ</option>
            <option value="MULTIPLE">Несколько</option>
          </select>
        </div>
        {options.map((o, i) => (
          <div className="field" key={i}>
            <label>Вариант {String.fromCharCode(65 + i)}</label>
            <input value={o} onChange={(e) => setOptions(options.map((x, j) => (j === i ? e.target.value : x)))} />
          </div>
        ))}
        <button className="btn btn-primary" onClick={addQuestion}>Добавить вопрос</button>
      </div>
      <h3>Вопросы ({quiz.questions.length})</h3>
      {quiz.questions.map((q, i) => (
        <div className="card" key={q.id}>
          <strong>{i + 1}. {q.text}</strong>
          <p style={{ color: "var(--muted)", fontSize: 13 }}>{q.answerType} · {q.options.length} вариантов</p>
        </div>
      ))}
    </Layout>
  );
}
