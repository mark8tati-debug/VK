import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Layout from "../components/Layout";
import { quizzes, uploadImage } from "../api";

const DEFAULT_OPTIONS = ["Вариант A", "Вариант B", "Вариант C", "Вариант D"];

export default function QuizEdit() {
  const { id } = useParams();
  const nav = useNavigate();
  const [quiz, setQuiz] = useState(null);
  const [text, setText] = useState("");
  const [answerType, setAnswerType] = useState("SINGLE");
  const [options, setOptions] = useState(DEFAULT_OPTIONS);
  const [correct, setCorrect] = useState(new Set());
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState("");
  const [uploading, setUploading] = useState(false);
  const [title, setTitle] = useState("");
  const [savingTitle, setSavingTitle] = useState(false);

  useEffect(() => {
    quizzes.get(id).then((q) => {
      setQuiz(q);
      setTitle(q.title);
    });
  }, [id]);

  async function saveTitle() {
    if (!title.trim()) {
      alert("Введите название квиза");
      return;
    }
    try {
      setSavingTitle(true);
      const updated = await quizzes.update(id, { title: title.trim() });
      setQuiz(updated);
      setTitle(updated.title);
    } catch (ex) {
      alert(ex.message);
    } finally {
      setSavingTitle(false);
    }
  }

  function toggleCorrect(index) {
    setCorrect((prev) => {
      if (answerType === "SINGLE") return new Set([index]);
      const next = new Set(prev);
      if (next.has(index)) next.delete(index);
      else next.add(index);
      return next;
    });
  }

  function onAnswerTypeChange(value) {
    setAnswerType(value);
    if (value === "SINGLE" && correct.size > 1) {
      setCorrect(new Set([...correct][0]));
    }
  }

  function onImageSelect(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      alert("Выберите файл изображения");
      return;
    }
    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
  }

  function clearImage() {
    setImageFile(null);
    setImagePreview("");
  }

  function resetForm() {
    setText("");
    setOptions(DEFAULT_OPTIONS);
    setCorrect(new Set());
    clearImage();
  }

  async function addQuestion() {
    if (!text.trim()) {
      alert("Введите текст вопроса");
      return;
    }
    if (correct.size === 0) {
      alert("Отметьте хотя бы один правильный вариант");
      return;
    }

    try {
      setUploading(true);
      let imageUrl;
      if (imageFile) imageUrl = await uploadImage(imageFile);

      await quizzes.addQuestion(id, {
        text,
        type: imageUrl ? "IMAGE" : "TEXT",
        imageUrl,
        answerType,
        options: options.map((t, i) => ({ text: t, isCorrect: correct.has(i) })),
      });
      setQuiz(await quizzes.get(id));
      resetForm();
    } catch (ex) {
      alert(ex.message);
    } finally {
      setUploading(false);
    }
  }

  async function removeQuiz() {
    if (!quiz || !confirm(`Удалить квиз «${quiz.title}»? Все вопросы и сессии будут удалены.`)) return;
    try {
      await quizzes.remove(id);
      nav("/dashboard");
    } catch (ex) {
      alert(ex.message);
    }
  }

  if (!quiz) return null;

  return (
    <Layout
      title={`Редактор · ${quiz.title}`}
      action={<button className="btn btn-danger" onClick={removeQuiz}>Удалить квиз</button>}
    >
      <div className="card">
        <h3>Настройки квиза</h3>
        <div className="option-row">
          <div className="field">
            <label>Название квиза</label>
            <input value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>
          <button
            type="button"
            className="btn btn-primary"
            onClick={saveTitle}
            disabled={savingTitle || title.trim() === quiz.title}
          >
            {savingTitle ? "Сохранение…" : "Сохранить"}
          </button>
        </div>
      </div>
      <div className="card">
        <h3>Новый вопрос</h3>
        <div className="field">
          <label>Текст вопроса</label>
          <input value={text} onChange={(e) => setText(e.target.value)} />
        </div>
        <div className="field">
          <label>Изображение (необязательно)</label>
          <input type="file" accept="image/jpeg,image/png,image/gif,image/webp" onChange={onImageSelect} />
          <p style={{ fontSize: 12, color: "var(--muted)", marginTop: 6 }}>JPEG, PNG, GIF или WebP, до 5 МБ</p>
        </div>
        {imagePreview && (
          <div className="image-preview">
            <img src={imagePreview} alt="Превью" />
            <button type="button" className="btn btn-secondary" onClick={clearImage}>Убрать</button>
          </div>
        )}
        <div className="field">
          <label>Тип ответа</label>
          <select value={answerType} onChange={(e) => onAnswerTypeChange(e.target.value)}>
            <option value="SINGLE">Один ответ</option>
            <option value="MULTIPLE">Несколько</option>
          </select>
        </div>
        <p style={{ fontSize: 12, color: "var(--muted)", marginBottom: 12 }}>
          {answerType === "SINGLE"
            ? "Выберите один правильный вариант"
            : "Можно отметить несколько правильных вариантов"}
        </p>
        {options.map((o, i) => (
          <div className="option-row" key={i}>
            <div className="field">
              <label>Вариант {String.fromCharCode(65 + i)}</label>
              <input value={o} onChange={(e) => setOptions(options.map((x, j) => (j === i ? e.target.value : x)))} />
            </div>
            <button
              type="button"
              className={`btn btn-secondary correct-toggle ${correct.has(i) ? "active" : ""}`}
              onClick={() => toggleCorrect(i)}
            >
              {correct.has(i) ? "✓ Правильный" : "Правильный"}
            </button>
          </div>
        ))}
        <button className="btn btn-primary" onClick={addQuestion} disabled={uploading}>
          {uploading ? "Загрузка…" : "Добавить вопрос"}
        </button>
      </div>

      <h3>Вопросы ({quiz.questions.length})</h3>
      {quiz.questions.map((q, i) => (
        <div className="card" key={q.id}>
          <strong>{i + 1}. {q.text}</strong>
          <p style={{ color: "var(--muted)", fontSize: 13 }}>
            {q.type === "IMAGE" ? "С изображением · " : ""}
            {q.answerType === "SINGLE" ? "Один ответ" : "Несколько"} · {q.options.length} вариантов
          </p>
          {q.imageUrl && (
            <img src={q.imageUrl} alt="" className="question-thumb" />
          )}
          <ul style={{ margin: "8px 0 0", paddingLeft: 20, fontSize: 14 }}>
            {q.options.map((o) => (
              <li key={o.id} style={{ color: o.isCorrect ? "var(--success)" : "var(--text)" }}>
                {o.text}{o.isCorrect ? " ✓" : ""}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </Layout>
  );
}
