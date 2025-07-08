// src/components/AnnotationForm.jsx
import { useState } from "react";
import api from "../services/api";
import TagInput from "./TagInput";

export default function AnnotationForm({ songId, onAnnotated }) {
  const [note, setNote] = useState("");
  const [rating, setRating] = useState(3);
  const [tags, setTags] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      user_id: 1, // TODO: replace with real user ID
      song_id: songId,
      note,
      rating,
      tag_names: tags,
    };

    try {
      await api.post("/songs/annotations/", payload);
      onAnnotated();
    } catch (err) {
      console.error("Failed to save annotation:", err);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="mb-4">
        <label className="block mb-1">Rating</label>
        <select
          value={rating}
          onChange={(e) => setRating(Number(e.target.value))}
          className="border rounded p-2 w-full"
        >
          {[1, 2, 3, 4, 5].map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>
      </div>
      <div className="mb-4">
        <label className="block mb-1">Note</label>
        <textarea
          className="w-full border rounded p-2"
          value={note}
          onChange={(e) => setNote(e.target.value)}
        />
      </div>
      <div className="mb-4">
        <label className="block mb-1">Tags</label>
        <TagInput value={tags} onChange={setTags} />
      </div>
      <button
        type="submit"
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      >
        Save Annotation
      </button>
    </form>
  );
}
