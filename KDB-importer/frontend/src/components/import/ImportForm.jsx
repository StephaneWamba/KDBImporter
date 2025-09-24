import ImportByIdForm from './ImportByIdForm';
import SearchForm from '../search/SearchForm';

export default function ImportForm({ mode, onImportResults, onSearchResults }) {
  return (
    <div className="space-y-6">
      {mode === 'import' ? (
        <ImportByIdForm onImportResults={onImportResults} />
      ) : (
        <SearchForm onSearchResults={onSearchResults} />
      )}
    </div>
  );
}
