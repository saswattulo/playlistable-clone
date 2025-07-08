// src/App.jsx
import SongList from "./components/SongList";

function App() {
  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Music Annotator</h1>
        <SongList />
      </div>
    </div>
  );
}

export default App;
