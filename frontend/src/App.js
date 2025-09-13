import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Components
const Header = ({ onSearch, searchQuery, setSearchQuery }) => (
  <header className="bg-gray-900 text-white p-4 shadow-lg">
    <div className="container mx-auto flex items-center justify-between">
      <h1 className="text-2xl font-bold text-red-500">DramaBox</h1>
      <div className="flex items-center space-x-4">
        <input
          type="text"
          placeholder="Cari drama..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="px-4 py-2 rounded-lg bg-gray-800 text-white border border-gray-600 focus:border-red-500 focus:outline-none"
          onKeyPress={(e) => e.key === 'Enter' && onSearch()}
        />
        <button
          onClick={onSearch}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
        >
          Cari
        </button>
      </div>
    </div>
  </header>
);

const DramaCard = ({ drama, onPlay }) => (
  <div className="bg-gray-800 rounded-lg overflow-hidden shadow-lg hover:shadow-xl transition-shadow">
    <div className="aspect-video bg-gray-700 flex items-center justify-center">
      {(drama.cover || drama.coverWap) ? (
        <img
          src={drama.cover || drama.coverWap}
          alt={drama.title || drama.bookName}
          className="w-full h-full object-cover"
        />
      ) : (
        <div className="text-gray-400">
          <svg className="w-12 h-12" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
          </svg>
        </div>
      )}
    </div>
    <div className="p-4">
      <h3 className="text-white font-semibold text-lg mb-2 line-clamp-2">
        {drama.title || drama.bookName || "Untitled"}
      </h3>
      <p className="text-gray-400 text-sm mb-3 line-clamp-3">
        {drama.description || drama.summary || drama.introduction || "No description available"}
      </p>
      <div className="flex items-center justify-between">
        <span className="text-gray-500 text-xs">
          {drama.chapterCount ? `${drama.chapterCount} Episodes` : ""}
        </span>
        <button
          onClick={() => onPlay(drama)}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm transition-colors"
        >
          Tonton
        </button>
      </div>
    </div>
  </div>
);

const VideoPlayer = ({ streamUrl, drama, onClose, onEpisodeChange, currentEpisode }) => (
  <div className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center">
    <div className="w-full max-w-6xl mx-4">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-white text-xl font-bold">
            {drama.title || drama.bookName} - Episode {currentEpisode}
          </h2>
        </div>
        <button
          onClick={onClose}
          className="text-white hover:text-red-500 text-2xl"
        >
          ×
        </button>
      </div>
      
      <div className="relative bg-black rounded-lg overflow-hidden">
        {streamUrl ? (
          <video
            controls
            autoPlay
            className="w-full h-auto max-h-[70vh]"
            src={streamUrl}
          >
            Your browser does not support the video tag.
          </video>
        ) : (
          <div className="aspect-video flex items-center justify-center text-white">
            Loading video...
          </div>
        )}
      </div>
      
      {/* Episode Controls */}
      <div className="mt-4 flex items-center justify-center space-x-4">
        <button
          onClick={() => onEpisodeChange(currentEpisode - 1)}
          disabled={currentEpisode <= 1}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>
        <span className="text-white">Episode {currentEpisode}</span>
        <button
          onClick={() => onEpisodeChange(currentEpisode + 1)}
          disabled={currentEpisode >= (drama.chapterCount || 999)}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next
        </button>
      </div>
    </div>
  </div>
);

const LoadingSpinner = () => (
  <div className="flex justify-center items-center py-12">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-500"></div>
  </div>
);

const App = () => {
  const [dramas, setDramas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearchMode, setIsSearchMode] = useState(false);
  const [selectedDrama, setSelectedDrama] = useState(null);
  const [streamUrl, setStreamUrl] = useState("");
  const [currentEpisode, setCurrentEpisode] = useState(1);
  const [error, setError] = useState("");

  // Load latest dramas on component mount
  useEffect(() => {
    loadLatestDramas();
  }, []);

  const loadLatestDramas = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.get(`${API}/dramas/latest`);
      if (response.data.success) {
        setDramas(response.data.data);
        setIsSearchMode(false);
      } else {
        setError("Failed to load dramas");
      }
    } catch (err) {
      console.error("Error loading latest dramas:", err);
      setError("Failed to load dramas");
    } finally {
      setLoading(false);
    }
  };

  const searchDramas = async () => {
    if (!searchQuery.trim()) {
      loadLatestDramas();
      return;
    }

    setLoading(true);
    setError("");
    try {
      const response = await axios.post(`${API}/dramas/search`, {
        keyword: searchQuery
      });
      if (response.data.success) {
        setDramas(response.data.data);
        setIsSearchMode(true);
      } else {
        setError("No results found");
        setDramas([]);
      }
    } catch (err) {
      console.error("Error searching dramas:", err);
      setError("Search failed");
      setDramas([]);
    } finally {
      setLoading(false);
    }
  };

  const playDrama = async (drama, episode = 1) => {
    setSelectedDrama(drama);
    setCurrentEpisode(episode);
    setStreamUrl(""); // Reset stream URL
    
    try {
      const response = await axios.post(`${API}/dramas/stream`, {
        book_id: drama.id || drama.bookId,
        episode: episode
      });
      
      if (response.data.success) {
        setStreamUrl(response.data.stream_url);
      } else {
        setError("Failed to load video stream");
      }
    } catch (err) {
      console.error("Error getting stream:", err);
      setError("Failed to load video stream");
    }
  };

  const handleEpisodeChange = (newEpisode) => {
    if (selectedDrama && newEpisode > 0) {
      playDrama(selectedDrama, newEpisode);
    }
  };

  const closePlayer = () => {
    setSelectedDrama(null);
    setStreamUrl("");
    setCurrentEpisode(1);
  };

  return (
    <div className="min-h-screen bg-gray-900">
      <Header
        onSearch={searchDramas}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
      />
      
      <main className="container mx-auto px-4 py-8">
        {/* Title Section */}
        <div className="mb-8">
          <h2 className="text-white text-2xl font-bold mb-2">
            {isSearchMode ? `Search Results for "${searchQuery}"` : "Latest Dramas"}
          </h2>
          {!isSearchMode && (
            <p className="text-gray-400">Discover the newest dramas available</p>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-600 text-white p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Loading Spinner */}
        {loading && <LoadingSpinner />}

        {/* Dramas Grid */}
        {!loading && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {dramas.map((drama, index) => (
              <DramaCard
                key={drama.id || drama.bookId || index}
                drama={drama}
                onPlay={playDrama}
              />
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && dramas.length === 0 && !error && (
          <div className="text-center py-12">
            <div className="text-gray-400 text-lg">
              {isSearchMode ? "No search results found" : "No dramas available"}
            </div>
          </div>
        )}
      </main>

      {/* Video Player Modal */}
      {selectedDrama && (
        <VideoPlayer
          streamUrl={streamUrl}
          drama={selectedDrama}
          onClose={closePlayer}
          onEpisodeChange={handleEpisodeChange}
          currentEpisode={currentEpisode}
        />
      )}
    </div>
  );
};

export default App;