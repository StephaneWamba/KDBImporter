import { useState } from 'react';
import { uploadToPaperless } from '../../api/importer';
import KeywordManager from '../keywords/KeywordManager';
import { toast } from 'react-toastify';

export default function ImportResultList({ results }) {
  const [uploading, setUploading] = useState({});
  const [uploaded, setUploaded] = useState({});
  const [showKeywordManager, setShowKeywordManager] = useState({});
  const [selectedKeywords, setSelectedKeywords] = useState({});

  if (!results || results.length === 0) return null;

  const handleUploadToPaperless = async (result, index) => {
    if (!result.success || !result.data?.paper) {
      toast.error('Cannot upload failed import to Paperless');
      return;
    }

    setUploading(prev => ({ ...prev, [index]: true }));
    
    try {
      const taskId = await uploadToPaperless(result.data.paper, result.data.metadata);
      if (taskId) {
        setUploaded(prev => ({ ...prev, [index]: true }));
        toast.success(`Paper queued for upload to Paperless (Task: ${taskId.substring(0, 8)}...)`);
      }
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(`Failed to upload to Paperless: ${error.message}`);
    } finally {
      setUploading(prev => ({ ...prev, [index]: false }));
    }
  };

  const handleKeywordsUpdate = (index, keywords) => {
    setSelectedKeywords(prev => ({ ...prev, [index]: keywords }));
  };

  const toggleKeywordManager = (index) => {
    setShowKeywordManager(prev => ({ ...prev, [index]: !prev[index] }));
  };

  return (
    <div className="mt-6">
      <h2 className="text-lg font-bold mb-2">Import Results</h2>
      {results.map((r, i) => (
        <div key={i} className="border p-4 mb-3 rounded-lg bg-white shadow-sm">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <p className="font-medium text-gray-900">
                <strong>Input:</strong> {r.input}
              </p>
              <p className="text-sm">
                <strong>Status:</strong>{' '}
                <span className={r.success ? 'text-green-600' : 'text-red-600'}>
                  {r.success ? '✅ Success' : `❌ Failed (${r.reason || 'Unknown'})`}
                </span>
              </p>
              {r.success && r.data?.paper?.title && (
                <div className="mt-2">
                  <p className="text-sm text-gray-700 font-medium">{r.data.paper.title}</p>
                  <p className="text-xs text-gray-500">
                    Authors: {r.data.paper.authors?.join(', ') || 'Unknown'}
                  </p>
                  {r.data.paper.summary && (
                    <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                      {r.data.paper.summary.substring(0, 150)}...
                    </p>
                  )}
                </div>
              )}
            </div>
            
            {r.success && r.data?.paper && (
              <div className="ml-4 flex flex-col gap-2">
                {uploaded[i] ? (
                  <div className="flex items-center text-green-600 text-sm">
                    <span className="mr-1">✅</span>
                    Uploaded to Paperless
                  </div>
                ) : (
                  <button
                    onClick={() => handleUploadToPaperless(r, i)}
                    disabled={uploading[i]}
                    className={`px-3 py-1 text-xs rounded-md font-medium transition-colors ${
                      uploading[i]
                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                  >
                    {uploading[i] ? (
                      <span className="flex items-center">
                        <svg className="animate-spin -ml-1 mr-1 h-3 w-3 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Uploading...
                      </span>
                    ) : (
                      '📄 Send to Paperless'
                    )}
                  </button>
                )}
                
                {r.data?.paper?.pdf_url && (
                  <a
                    href={r.data.paper.pdf_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3 py-1 text-xs rounded-md font-medium bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors"
                  >
                    📖 View PDF
                  </a>
                )}
                
                <button
                  onClick={() => toggleKeywordManager(i)}
                  className="px-3 py-1 text-xs rounded-md font-medium bg-purple-100 text-purple-700 hover:bg-purple-200 transition-colors"
                >
                  🏷️ Keywords
                </button>
              </div>
            )}
          </div>
          
          {/* Keyword Manager */}
          {showKeywordManager[i] && r.success && r.data?.paper && (
            <div className="mt-4 border-t pt-4">
              <KeywordManager
                paperData={r.data.paper}
                onKeywordsUpdate={(keywords) => handleKeywordsUpdate(i, keywords)}
              />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
