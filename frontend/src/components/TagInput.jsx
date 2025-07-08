// src/components/TagInput.jsx
import { useState } from "react";

export default function TagInput({ value, onChange }) {
  const [inputValue, setInputValue] = useState("");

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && inputValue.trim()) {
      e.preventDefault();
      const newTags = [...value, inputValue.trim()];
      onChange(newTags);
      setInputValue("");
    }
  };

  const removeTag = (index) => {
    const newTags = value.filter((_, i) => i !== index);
    onChange(newTags);
  };

  return (
    <div className="border rounded p-2 min-h-[40px]">
      {value.map((tag, idx) => (
        <span
          key={idx}
          className="inline-block bg-blue-100 text-blue-700 px-2 py-1 mr-1 mb-1 rounded"
        >
          {tag}
          <button onClick={() => removeTag(idx)} className="ml-1 font-bold">
            ×
          </button>
        </span>
      ))}
      <input
        type="text"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Add tag + press Enter"
        className="outline-none w-full"
      />
    </div>
  );
}
