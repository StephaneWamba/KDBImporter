// frontend/src/components/keywords/KeywordManager.jsx
import { useState, useEffect } from 'react';
import { extractKeywords, validateKeywords, getAvailableDomains } from '../../api/importer';
import { toast } from 'react-toastify';

export default function KeywordManager({ paperData, onKeywordsUpdate }) {
  const [extractedKeywords, setExtractedKeywords] = useState(null);
  const [userKeywords, setUserKeywords] = useState([]);
  const [validationResult, setValidationResult] = useState(null);
  const [availableDomains, setAvailableDomains] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
    loadAvailableDomains();
    if (paperData) {
      extractKeywordsFromPaper();
    }
  }, [paperData]);

  const loadAvailableDomains = async () => {
    try {
      const response = await getAvailableDomains();
      setAvailableDomains(response.domains);
    } catch (error) {
      console.error('Failed to load domains:', error);
    }
  };

  const extractKeywordsFromPaper = async () => {
    if (!paperData) return;
    
    setLoading(true);
    try {
      const result = await extractKeywords(paperData);
      setExtractedKeywords(result);
      
      // Auto-populate user keywords with primary keywords
      setUserKeywords(result.primary_keywords || []);
      
      toast.success(`Extracted ${result.primary_keywords?.length || 0} keywords with ${Math.round(result.confidence_score * 100)}% confidence`);
    } catch (error) {
      console.error('Keyword extraction failed:', error);
      toast.error('Failed to extract keywords');
    } finally {
      setLoading(false);
    }
  };

  const validateUserKeywords = async () => {
    if (userKeywords.length === 0) return;
    
    setLoading(true);
    try {
      const result = await validateKeywords(userKeywords);
      setValidationResult(result);
      
      const validCount = result.valid_keywords?.length || 0;
      const invalidCount = result.invalid_keywords?.length || 0;
      
      if (invalidCount > 0) {
        toast.warning(`${validCount} valid, ${invalidCount} invalid keywords`);
      } else {
        toast.success(`All ${validCount} keywords are valid`);
      }
    } catch (error) {
      console.error('Keyword validation failed:', error);
      toast.error('Failed to validate keywords');
    } finally {
      setLoading(false);
    }
  };

  const addKeyword = (keyword) => {
    if (keyword && !userKeywords.includes(keyword)) {
      setUserKeywords([...userKeywords, keyword]);
    }
  };

  const removeKeyword = (index) => {
    setUserKeywords(userKeywords.filter((_, i) => i !== index));
  };

  const applyKeywords = () => {
    if (onKeywordsUpdate) {
      onKeywordsUpdate(userKeywords);
    }
    toast.success('Keywords applied successfully');
  };

  const getConfidenceColor = (score) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceLabel = (score) => {
    if (score >= 0.8) return 'High';
    if (score >= 0.6) return 'Medium';
    return 'Low';
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Keyword Management</h3>
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          {showAdvanced ? 'Hide' : 'Show'} Advanced
        </button>
      </div>

      {/* Keyword Extraction Results */}
      {extractedKeywords && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <div className="flex justify-between items-center mb-3">
            <h4 className="font-medium text-gray-900">AI-Extracted Keywords</h4>
            <div className="flex items-center gap-2">
              <span className={`text-sm font-medium ${getConfidenceColor(extractedKeywords.confidence_score)}`}>
                {getConfidenceLabel(extractedKeywords.confidence_score)} Confidence
              </span>
              <span className="text-xs text-gray-500">
                ({Math.round(extractedKeywords.confidence_score * 100)}%)
              </span>
            </div>
          </div>

          {/* Primary Keywords */}
          <div className="mb-3">
            <label className="text-sm font-medium text-gray-700 mb-2 block">Primary Keywords</label>
            <div className="flex flex-wrap gap-2">
              {extractedKeywords.primary_keywords?.map((keyword, index) => (
                <button
                  key={index}
                  onClick={() => addKeyword(keyword)}
                  className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full hover:bg-blue-200 transition-colors"
                >
                  + {keyword}
                </button>
              ))}
            </div>
          </div>

          {/* Secondary Keywords */}
          {showAdvanced && extractedKeywords.secondary_keywords?.length > 0 && (
            <div className="mb-3">
              <label className="text-sm font-medium text-gray-700 mb-2 block">Secondary Keywords</label>
              <div className="flex flex-wrap gap-2">
                {extractedKeywords.secondary_keywords.map((keyword, index) => (
                  <button
                    key={index}
                    onClick={() => addKeyword(keyword)}
                    className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full hover:bg-gray-200 transition-colors"
                  >
                    + {keyword}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Technical Terms */}
          {showAdvanced && extractedKeywords.technical_terms?.length > 0 && (
            <div className="mb-3">
              <label className="text-sm font-medium text-gray-700 mb-2 block">Technical Terms</label>
              <div className="flex flex-wrap gap-2">
                {extractedKeywords.technical_terms.map((term, index) => (
                  <button
                    key={index}
                    onClick={() => addKeyword(term)}
                    className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full hover:bg-green-200 transition-colors"
                  >
                    + {term}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Domain Tags */}
          {showAdvanced && extractedKeywords.domain_tags?.length > 0 && (
            <div className="mb-3">
              <label className="text-sm font-medium text-gray-700 mb-2 block">Domain Tags</label>
              <div className="flex flex-wrap gap-2">
                {extractedKeywords.domain_tags.map((tag, index) => (
                  <button
                    key={index}
                    onClick={() => addKeyword(tag)}
                    className="px-3 py-1 bg-purple-100 text-purple-800 text-sm rounded-full hover:bg-purple-200 transition-colors"
                  >
                    + {tag}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* User Keywords Management */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-3">
          <h4 className="font-medium text-gray-900">Selected Keywords</h4>
          <div className="flex gap-2">
            <button
              onClick={validateUserKeywords}
              disabled={loading || userKeywords.length === 0}
              className="px-3 py-1 text-sm bg-yellow-100 text-yellow-800 rounded-md hover:bg-yellow-200 disabled:opacity-50"
            >
              Validate
            </button>
            <button
              onClick={extractKeywordsFromPaper}
              disabled={loading}
              className="px-3 py-1 text-sm bg-blue-100 text-blue-800 rounded-md hover:bg-blue-200 disabled:opacity-50"
            >
              {loading ? 'Extracting...' : 'Re-extract'}
            </button>
          </div>
        </div>

        {/* Keyword Input */}
        <div className="mb-3">
          <input
            type="text"
            placeholder="Add custom keyword..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                addKeyword(e.target.value.trim());
                e.target.value = '';
              }
            }}
          />
        </div>

        {/* Selected Keywords */}
        <div className="flex flex-wrap gap-2 mb-3">
          {userKeywords.map((keyword, index) => (
            <div
              key={index}
              className="flex items-center gap-1 px-3 py-1 bg-blue-600 text-white text-sm rounded-full"
            >
              <span>{keyword}</span>
              <button
                onClick={() => removeKeyword(index)}
                className="ml-1 hover:text-red-200"
              >
                ×
              </button>
            </div>
          ))}
        </div>

        {/* Validation Results */}
        {validationResult && (
          <div className="p-3 bg-gray-50 rounded-md">
            <h5 className="font-medium text-gray-900 mb-2">Validation Results</h5>
            
            {validationResult.valid_keywords?.length > 0 && (
              <div className="mb-2">
                <span className="text-sm text-green-600 font-medium">Valid: </span>
                <span className="text-sm text-gray-700">
                  {validationResult.valid_keywords.join(', ')}
                </span>
              </div>
            )}

            {validationResult.invalid_keywords?.length > 0 && (
              <div className="mb-2">
                <span className="text-sm text-red-600 font-medium">Invalid: </span>
                <span className="text-sm text-gray-700">
                  {validationResult.invalid_keywords.join(', ')}
                </span>
              </div>
            )}

            {validationResult.suggestions?.length > 0 && (
              <div>
                <span className="text-sm text-yellow-600 font-medium">Suggestions: </span>
                {validationResult.suggestions.map((suggestion, index) => (
                  <div key={index} className="text-sm text-gray-700 ml-2">
                    "{suggestion.original}" → {suggestion.suggestions.join(', ')}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex justify-end gap-3">
        <button
          onClick={() => setUserKeywords([])}
          className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
        >
          Clear All
        </button>
        <button
          onClick={applyKeywords}
          disabled={userKeywords.length === 0}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          Apply Keywords ({userKeywords.length})
        </button>
      </div>
    </div>
  );
}
