import { useState } from 'react';
import ImportForm from '../components/import/ImportForm';
import ImportResultList from '../components/import/ImportResultList';
import SearchResultList from '../components/search/SearchResultList';
import { importArxiv } from '../api/importer';
import { toast } from 'react-toastify';

export default function ImportPage() {
  const [mode, setMode] = useState('import'); // 'import' or 'search'
  const [importResults, setImportResults] = useState([]);
  const [searchResults, setSearchResults] = useState([]);

  const switchMode = (newMode) => {
    setMode(newMode);
    setImportResults([]);
    setSearchResults([]);
  };

  const handleImportResults = (results) => {
    setMode('import');
    setImportResults(results);
    setSearchResults([]);
  };

  const handleSearchResults = (results) => {
    setMode('search');
    setSearchResults(results);
    setImportResults([]);
  };

  const handleImportSelected = async (selectedItems) => {
    try {
      const inputs = selectedItems.map((r) => r.paper.id);
      const metadata = selectedItems.map((r) => r.metadata || {});
      const imported = await importArxiv(inputs, metadata);
      setImportResults(imported);
      toast.success(`Imported ${imported.length} items`);
      setMode('import'); // switch to import view
    } catch (err) {
      console.error(err);
      toast.error('Import failed');
    }
  };

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">arXiv Importer</h1>

      {/* Mode Tabs */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={() => switchMode('import')}
          className={`px-4 py-2 rounded ${
            mode === 'import'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700'
          }`}
        >
          Import by ID/URL
        </button>
        <button
          onClick={() => switchMode('search')}
          className={`px-4 py-2 rounded ${
            mode === 'search'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700'
          }`}
        >
          Search by Query
        </button>
      </div>

      {/* Form (shared) */}
      <ImportForm
        mode={mode}
        onImportResults={handleImportResults}
        onSearchResults={handleSearchResults}
      />

      {/* Results */}
      {mode === 'import' && importResults.length > 0 && (
        <ImportResultList results={importResults} />
      )}

      {mode === 'search' && searchResults.length > 0 && (
        <SearchResultList
          results={searchResults}
          onImport={handleImportSelected}
        />
      )}
    </div>
  );
}
