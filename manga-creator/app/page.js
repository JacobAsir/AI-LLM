'use client';

import { useState } from 'react';

export default function Home() {
  const [prompt, setPrompt] = useState('');
  const [image, setImage] = useState(null);

  const handleGenerate = async () => {
    // Call your backend API to generate the manga story or image
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt }),
    });
    const data = await response.json();
    setImage(data.imageUrl); // Assuming the API returns an image URL
  };

  return (
    <main className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-4xl font-bold text-center text-gray-800">Manga Creator</h1>

        <div className="mt-8 space-y-4">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Enter your manga idea..."
            className="w-full p-4 border border-gray-300 rounded"
          ></textarea>

          <button
            onClick={handleGenerate}
            className="w-full px-4 py-2 text-white bg-blue-500 rounded hover:bg-blue-600"
          >
            Generate Manga
          </button>

          {image && (
            <div className="mt-4">
              <h2 className="text-lg font-semibold">Generated Manga:</h2>
              <img src={image} alt="Generated Manga" className="w-full rounded" />
            </div>
          )}
        </div>
      </div>
    </main>
  );
}