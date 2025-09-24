import { useState, useEffect } from 'react';

export default function SearchResultList({ results, onImport }) {
  const [selected, setSelected] = useState({});

  useEffect(() => {
    // Initialize all as relevant (true) by default when new results come in
    const initialState = {};
    results?.forEach((_, i) => {
      initialState[i] = true;
    });
    setSelected(initialState);
  }, [results]);

  const toggleSelection = (index) => {
    setSelected(prev => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  const handleImport = () => {
    const relevantResults = results.filter((_, i) => selected[i]);
    if (onImport) {
      onImport(relevantResults);
    }
  };

  const anySelected = Object.values(selected).some(Boolean);

  if (!results || results.length === 0) return null;

  return (
    <div className="mt-6">
      <h2 className="text-lg font-bold mb-4">Search Results</h2>

      {results.map((r, i) => (
        <div key={i} className="border p-3 mb-3 rounded shadow-sm bg-white">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-base font-medium text-gray-800">{r.paper.title}</p>
              <p className="text-sm text-gray-500">
                Authors: {r.paper.authors?.join(', ') || 'Unknown'}
              </p>
              <p className="text-xs mt-1 text-gray-400">
                Importance: {r.metadata.importance || 'N/A'} | Tag: {r.metadata.tag || '—'}
              </p>
            </div>
            <div className="flex items-center ml-4">
              <label className="text-sm mr-2 text-gray-700">Relevant</label>
              <input
                type="checkbox"
                checked={!!selected[i]}
                onChange={() => toggleSelection(i)}
                className="w-4 h-4"
              />
            </div>
          </div>
        </div>
      ))}

      <button
        onClick={handleImport}
        disabled={!anySelected}
        className={`mt-4 px-4 py-2 rounded ${
          anySelected ? 'bg-green-600 text-white hover:bg-green-700' : 'bg-gray-300 text-gray-500 cursor-not-allowed'
        }`}
      >
        Import Selected
      </button>
    </div>
  );
}
