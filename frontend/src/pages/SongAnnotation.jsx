import { useState } from "react";

// Sample predefined tags - in production you'd likely store these in a database
const MOOD_TAGS = [
  "Happy",
  "Sad",
  "Energetic",
  "Calm",
  "Nostalgic",
  "Angry",
  "Peaceful",
  "Melancholic",
  "Uplifting",
  "Bittersweet",
  "Dreamy",
  "Intense",
  "Romantic",
  "Anxious",
  "Confident",
];

const GENRE_TAGS = [
  "Pop",
  "Rock",
  "Hip-Hop",
  "R&B",
  "Electronic",
  "EDM",
  "Country",
  "Jazz",
  "Classical",
  "Metal",
  "Folk",
  "Reggae",
  "Latin",
  "K-Pop",
  "Indie",
  "Alternative",
  "House",
  "Techno",
  "Trap",
  "Punk",
];

const CONTEXT_TAGS = [
  "Workout",
  "Study",
  "Party",
  "Road Trip",
  "Relaxation",
  "Focus",
  "Morning",
  "Night",
  "Running",
  "Dinner",
  "Date Night",
  "Motivational",
  "Meditation",
  "Beach",
  "Gym",
  "Coding",
  "Gaming",
  "Commute",
];

export default function SongAnnotationTool() {
  // Song metadata state
  const [currentSong, setCurrentSong] = useState({
    id: "sample-001",
    title: "Sample Song",
    artist: "Sample Artist",
    album: "Sample Album",
    releaseYear: 2023,
    spotifyUrl: "https://open.spotify.com/track/sample",
    previewUrl: "https://p.scdn.co/mp3-preview/sample",
    imageUrl: "/api/placeholder/300/300", // Using placeholder image
  });

  // Annotation state
  const [selectedMoodTags, setSelectedMoodTags] = useState([]);
  const [selectedGenreTags, setSelectedGenreTags] = useState([]);
  const [selectedContextTags, setSelectedContextTags] = useState([]);

  // Strength indicators state
  const [strengthValues, setStrengthValues] = useState({
    tempo: 5,
    energy: 5,
    danceability: 5,
    instrumentalness: 5,
    positivity: 5,
  });

  // Toggle tag selection
  const toggleTag = (tag, category) => {
    switch (category) {
      case "mood":
        setSelectedMoodTags((prev) =>
          prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
        );
        break;
      case "genre":
        setSelectedGenreTags((prev) =>
          prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
        );
        break;
      case "context":
        setSelectedContextTags((prev) =>
          prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
        );
        break;
      default:
        break;
    }
  };

  // Update strength indicator
  const updateStrength = (name, value) => {
    setStrengthValues((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // Save annotations
  const saveAnnotations = () => {
    const annotations = {
      songId: currentSong.id,
      tags: {
        mood: selectedMoodTags,
        genre: selectedGenreTags,
        context: selectedContextTags,
        strength: strengthValues,
      },
      dateAnnotated: new Date().toISOString(),
      annotatedBy: "current-user", // In a real app, you'd use actual user ID
    };

    console.log("Saving annotations:", annotations);
    // Here you would send this data to your backend
    alert("Annotations saved successfully!");
  };

  // Load next song (would fetch from your database in a real implementation)
  const loadNextSong = () => {
    // Clear previous annotations
    setSelectedMoodTags([]);
    setSelectedGenreTags([]);
    setSelectedContextTags([]);
    setStrengthValues({
      tempo: 5,
      energy: 5,
      danceability: 5,
      instrumentalness: 5,
      positivity: 5,
    });

    // Mock loading next song
    const nextSongId = Math.floor(Math.random() * 1000);
    setCurrentSong({
      id: `song-${nextSongId}`,
      title: `Song Title ${nextSongId}`,
      artist: `Artist ${nextSongId % 20}`,
      album: `Album ${nextSongId % 50}`,
      releaseYear: 2010 + (nextSongId % 15),
      spotifyUrl: `https://open.spotify.com/track/sample${nextSongId}`,
      previewUrl: `https://p.scdn.co/mp3-preview/sample${nextSongId}`,
      imageUrl: "/api/placeholder/300/300",
    });
  };

  // Render tag buttons with selection state
  const renderTagButtons = (tags, selectedTags, category) => {
    return tags.map((tag) => (
      <button
        key={tag}
        onClick={() => toggleTag(tag, category)}
        className={`px-3 py-1 m-1 rounded-full text-sm font-medium 
          ${
            selectedTags.includes(tag)
              ? "bg-blue-500 text-white"
              : "bg-gray-200 text-gray-700 hover:bg-gray-300"
          }`}
      >
        {tag}
      </button>
    ));
  };

  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Song Annotation Tool</h1>

      {/* Song Information */}
      <div className="flex mb-6 bg-white p-4 rounded-lg shadow">
        <img
          src={currentSong.imageUrl}
          alt={`${currentSong.title} album cover`}
          className="w-32 h-32 object-cover rounded"
        />
        <div className="ml-4">
          <h2 className="text-xl font-semibold">{currentSong.title}</h2>
          <p className="text-gray-700">{currentSong.artist}</p>
          <p className="text-gray-500">
            {currentSong.album} ({currentSong.releaseYear})
          </p>
          <div className="mt-2">
            <a
              href={currentSong.spotifyUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-green-600 hover:underline"
            >
              Open in Spotify
            </a>
            {currentSong.previewUrl && (
              <audio controls className="mt-2 w-full max-w-xs">
                <source src={currentSong.previewUrl} type="audio/mpeg" />
                Your browser does not support the audio element.
              </audio>
            )}
          </div>
        </div>
      </div>

      {/* Annotation Sections */}
      <div className="bg-white p-6 rounded-lg shadow mb-6">
        {/* Mood Tags */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">Mood Tags</h3>
          <p className="text-sm text-gray-500 mb-2">Select all that apply</p>
          <div className="flex flex-wrap">
            {renderTagButtons(MOOD_TAGS, selectedMoodTags, "mood")}
          </div>
        </div>

        {/* Genre Tags */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">Genre Tags</h3>
          <p className="text-sm text-gray-500 mb-2">Select all that apply</p>
          <div className="flex flex-wrap">
            {renderTagButtons(GENRE_TAGS, selectedGenreTags, "genre")}
          </div>
        </div>

        {/* Context Tags */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">Context Tags</h3>
          <p className="text-sm text-gray-500 mb-2">Select all that apply</p>
          <div className="flex flex-wrap">
            {renderTagButtons(CONTEXT_TAGS, selectedContextTags, "context")}
          </div>
        </div>

        {/* Strength Indicators (Optional) */}
        <div>
          <h3 className="text-lg font-semibold mb-2">
            Strength Indicators{" "}
            <span className="text-sm font-normal text-gray-500">
              (Optional)
            </span>
          </h3>

          {/* Tempo */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tempo: {strengthValues.tempo}{" "}
              {strengthValues.tempo < 4
                ? "(Slow)"
                : strengthValues.tempo > 7
                ? "(Fast)"
                : "(Medium)"}
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={strengthValues.tempo}
              onChange={(e) =>
                updateStrength("tempo", parseInt(e.target.value))
              }
              className="w-full"
            />
          </div>

          {/* Energy */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Energy: {strengthValues.energy}{" "}
              {strengthValues.energy < 4
                ? "(Low)"
                : strengthValues.energy > 7
                ? "(High)"
                : "(Medium)"}
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={strengthValues.energy}
              onChange={(e) =>
                updateStrength("energy", parseInt(e.target.value))
              }
              className="w-full"
            />
          </div>

          {/* Danceability */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Danceability: {strengthValues.danceability}
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={strengthValues.danceability}
              onChange={(e) =>
                updateStrength("danceability", parseInt(e.target.value))
              }
              className="w-full"
            />
          </div>

          {/* Instrumentalness */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Instrumentalness: {strengthValues.instrumentalness}{" "}
              {strengthValues.instrumentalness < 4
                ? "(Vocal-focused)"
                : strengthValues.instrumentalness > 7
                ? "(Instrumental)"
                : "(Balanced)"}
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={strengthValues.instrumentalness}
              onChange={(e) =>
                updateStrength("instrumentalness", parseInt(e.target.value))
              }
              className="w-full"
            />
          </div>

          {/* Positivity */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Positivity: {strengthValues.positivity}{" "}
              {strengthValues.positivity < 4
                ? "(Negative)"
                : strengthValues.positivity > 7
                ? "(Positive)"
                : "(Neutral)"}
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={strengthValues.positivity}
              onChange={(e) =>
                updateStrength("positivity", parseInt(e.target.value))
              }
              className="w-full"
            />
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-between">
        <button
          onClick={saveAnnotations}
          className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded"
        >
          Save Annotations
        </button>
        <button
          onClick={loadNextSong}
          className="bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-6 rounded"
        >
          Next Song
        </button>
      </div>
    </div>
  );
}
