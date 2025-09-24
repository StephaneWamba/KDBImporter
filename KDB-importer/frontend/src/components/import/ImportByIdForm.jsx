import { useState } from 'react';
import { importArxiv } from '../../api/importer';
import { toast } from 'react-toastify';

export default function ImportByIdForm({ onImportResults }) {
  const [inputText, setInputText] = useState('');
  const [importance, setImportance] = useState('medium');
  const [tag, setTag] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const inputs = inputText
      .split('\n')
      .map(s => s.trim())
      .filter(Boolean);

    if (inputs.length === 0) {
      toast.warning('Please enter at least one ID or URL.');
      return;
    }

    const metadata = inputs.map(() => ({
      importance: importance.toLowerCase(),
      ...(tag.trim() && { tag: tag.trim() }),
    }));

    try {
      setIsLoading(true);
      const results = await importArxiv(inputs, metadata);
      toast.success('Import complete');
      onImportResults(results);
    } catch (err) {
      console.error(err);
      toast.error('Import failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm mb-1 font-medium">arXiv IDs or URLs</label>
        <textarea
          className="w-full border p-2 rounded"
          rows="6"
          required
          placeholder="Paste arXiv IDs or URLs (one per line)..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
        />
      </div>

      <div className="flex flex-wrap gap-4">
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
          <label className="block text-sm mb-1">Tag (optional)</label>
          <input
            type="text"
            value={tag}
            onChange={(e) => setTag(e.target.value)}
            placeholder="Enter tag"
            className="w-full border p-2 rounded"
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading || !inputText.trim()}
        className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
      >
        {isLoading ? 'Importing…' : 'Import'}
      </button>
    </form>
  );
}
