// src/components/SongCard.jsx
import { Link } from "react-router-dom";

export default function SongCard({ song }) {
  return (
    <div className="border rounded shadow p-4 hover:shadow-md transition-shadow">
      <h3 className="text-lg font-bold">{song.title}</h3>
      <p className="text-sm text-gray-600">
        {song.artist} - {song.album}
      </p>
      <Link
        to={`/songs/${song.id}`}
        className="text-blue-500 underline mt-2 inline-block"
      >
        View Details
      </Link>
    </div>
  );
}
