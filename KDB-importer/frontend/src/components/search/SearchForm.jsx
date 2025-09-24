import { useState } from 'react';
import { searchArxiv } from '../../api/importer';
import { toast } from 'react-toastify';

export default function SearchForm({ onSearchResults }) {
  const [query, setQuery] = useState('');
  const [importance, setImportance] = useState('medium');
  const [tag, setTag] = useState('');
  const [sortBy, setSortBy] = useState('relevance');
  const [maxResults, setMaxResults] = useState(5);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const trimmedQuery = query.trim();
    if (!trimmedQuery) {
      toast.warning('Please enter a search query.');
      return;
    }

    try {
      setIsLoading(true);

      const metadata = {
        ...(importance && { importance }),
        ...(tag.trim() && { tag: tag.trim() }),
      };

      const payload = {
        query: trimmedQuery,
        sort_by: sortBy,
        max_results: Number(maxResults) || 5,
        metadata: Object.keys(metadata).length > 0 ? metadata : undefined,
      };

      console.log("Sending search payload:", payload);

      const results = await searchArxiv(payload);
      toast.success('Search complete');
      onSearchResults(results);
    } catch (err) {
      console.error(err);
      toast.error('Search failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <input
        className="w-full border p-2 rounded"
        placeholder="Search query (e.g. transformer vision)"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <div className="flex flex-wrap gap-4">
        <div className="flex-1 min-w-[150px]">
          <label className="block text-sm mb-1">Sort by</label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="w-full border p-2 rounded"
          >
            <option value="relevance">Relevance</option>
            <option value="submittedDate">Date</option>
          </select>
        </div>

        <div className="flex-1 min-w-[100px]">
          <label className="block text-sm mb-1">Max results</label>
          <input
            type="number"
            value={maxResults}
            onChange={(e) => setMaxResults(e.target.value)}
            min={1}
            max={50}
            className="w-full border p-2 rounded"
          />
        </div>

        <div className="flex-1 min-w-[120px]">
          <label className="block text-sm mb-1">Importance</label>
          <select
            value={importance}
            onChange={(e) => setImportance(e.target.value)}
            className="w-full border p-2 rounded"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        <div className="flex-1 min-w-[150px]">
          <label className="block text-sm mb-1">Tag</label>
          <input
            type="text"
            value={tag}
            onChange={(e) => setTag(e.target.value)}
            placeholder="Tag"
            className="w-full border p-2 rounded"
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
      >
        {isLoading ? 'Searching…' : 'Search'}
      </button>
    </form>
  );
}
