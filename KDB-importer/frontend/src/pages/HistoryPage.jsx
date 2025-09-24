// frontend/src/pages/HistoryPage.jsx
import { useState, useEffect } from 'react';
import { getAvailableDates, getDocumentHistoryByDate, getDocumentSummaryByRange } from '../api/importer';
import { toast } from 'react-toastify';

export default function HistoryPage() {
  const [availableDates, setAvailableDates] = useState([]);
  const [selectedDate, setSelectedDate] = useState('');
  const [historyData, setHistoryData] = useState(null);
  const [rangeData, setRangeData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('single'); // 'single' or 'range'
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  useEffect(() => {
    loadAvailableDates();
  }, []);

  const loadAvailableDates = async () => {
    try {
      const response = await getAvailableDates();
      setAvailableDates(response.dates);
      if (response.dates.length > 0) {
        setSelectedDate(response.dates[0]);
        loadHistoryData(response.dates[0]);
      }
    } catch (error) {
      toast.error('Failed to load available dates');
    }
  };

  const loadHistoryData = async (date) => {
    if (!date) return;
    
    setLoading(true);
    try {
      const data = await getDocumentHistoryByDate(date);
      setHistoryData(data);
    } catch (error) {
      toast.error('Failed to load history data');
    } finally {
      setLoading(false);
    }
  };

  const loadRangeData = async () => {
    if (!startDate || !endDate) {
      toast.error('Please select both start and end dates');
      return;
    }
    
    setLoading(true);
    try {
      const data = await getDocumentSummaryByRange(startDate, endDate);
      setRangeData(data);
    } catch (error) {
      toast.error('Failed to load range data');
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getStatusIcon = (status) => {
    return status === 'success' ? '✅' : '❌';
  };

  const getEventTypeIcon = (type) => {
    const icons = {
      'import': '📄',
      'keyword_extraction': '🏷️',
      'paperless_upload': '📤',
      'search': '🔍'
    };
    return icons[type] || '📋';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Document History</h1>
          <p className="text-gray-600">View documents processed on specific dates</p>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('single')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'single'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Single Date
          </button>
          <button
            onClick={() => setActiveTab('range')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'range'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Date Range
          </button>
        </nav>
      </div>

      {/* Single Date Tab */}
      {activeTab === 'single' && (
        <div className="space-y-4">
          {/* Date Selector */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Date</h3>
            <div className="flex items-center space-x-4">
              <select
                value={selectedDate}
                onChange={(e) => {
                  setSelectedDate(e.target.value);
                  loadHistoryData(e.target.value);
                }}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select a date...</option>
                {availableDates.map((date) => (
                  <option key={date} value={date}>
                    {new Date(date).toLocaleDateString()}
                  </option>
                ))}
              </select>
              <button
                onClick={() => loadHistoryData(selectedDate)}
                disabled={!selectedDate || loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Loading...' : 'Refresh'}
              </button>
            </div>
          </div>

          {/* History Data */}
          {historyData && (
            <div className="space-y-6">
              {/* Daily Metrics */}
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Daily Summary - {new Date(historyData.date).toLocaleDateString()}
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {historyData.daily_metrics.papers_imported}
                    </div>
                    <div className="text-sm text-blue-800">Papers Imported</div>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {historyData.daily_metrics.papers_uploaded}
                    </div>
                    <div className="text-sm text-green-800">Papers Uploaded</div>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      {historyData.daily_metrics.keywords_extracted}
                    </div>
                    <div className="text-sm text-purple-800">Keywords Extracted</div>
                  </div>
                  <div className="bg-orange-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-orange-600">
                      {Math.round(historyData.daily_metrics.avg_confidence_score * 100)}%
                    </div>
                    <div className="text-sm text-orange-800">Avg Confidence</div>
                  </div>
                </div>
              </div>

              {/* Activities */}
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Activities</h3>
                {historyData.activities.length > 0 ? (
                  <div className="space-y-3">
                    {historyData.activities.map((activity, index) => (
                      <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                        <span className="text-lg">{getEventTypeIcon(activity.type)}</span>
                        <div className="flex-1">
                          <div className="font-medium text-gray-900">{activity.title}</div>
                          <div className="text-sm text-gray-500">
                            {formatTimestamp(activity.timestamp)}
                          </div>
                        </div>
                        <span className="text-lg">{getStatusIcon(activity.status)}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">No activities found for this date.</p>
                )}
              </div>

              {/* Keyword Extractions */}
              {historyData.keyword_extractions.length > 0 && (
                <div className="bg-white rounded-lg shadow-sm border p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Keyword Extractions</h3>
                  <div className="space-y-4">
                    {historyData.keyword_extractions.map((extraction, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-4">
                        <div className="font-medium text-gray-900 mb-2">{extraction.paper_title}</div>
                        <div className="text-sm text-gray-600 mb-2">
                          Confidence: {Math.round(extraction.confidence_score * 100)}% | 
                          Method: {extraction.extraction_method} | 
                          Time: {formatTimestamp(extraction.timestamp)}
                        </div>
                        {extraction.primary_keywords.length > 0 && (
                          <div className="mb-2">
                            <span className="text-sm font-medium text-gray-700">Primary Keywords:</span>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {extraction.primary_keywords.map((keyword, i) => (
                                <span key={i} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                                  {keyword}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Paperless Uploads */}
              {historyData.paperless_uploads.length > 0 && (
                <div className="bg-white rounded-lg shadow-sm border p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Paperless Uploads</h3>
                  <div className="space-y-3">
                    {historyData.paperless_uploads.map((upload, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <div className="font-medium text-gray-900">{upload.paper_title}</div>
                          <div className="text-sm text-gray-500">
                            Task ID: {upload.task_id} | {formatTimestamp(upload.timestamp)}
                          </div>
                        </div>
                        <span className="text-lg">{getStatusIcon(upload.status)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Date Range Tab */}
      {activeTab === 'range' && (
        <div className="space-y-4">
          {/* Date Range Selector */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Date Range</h3>
            <div className="flex items-center space-x-4">
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-gray-500">to</span>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={loadRangeData}
                disabled={!startDate || !endDate || loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Loading...' : 'Get Summary'}
              </button>
            </div>
          </div>

          {/* Range Data */}
          {rangeData && (
            <div className="space-y-6">
              {/* Summary */}
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Summary ({new Date(rangeData.date_range.start_date).toLocaleDateString()} - {new Date(rangeData.date_range.end_date).toLocaleDateString()})
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {rangeData.summary.total_imports}
                    </div>
                    <div className="text-sm text-blue-800">Total Imports</div>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {rangeData.summary.total_uploads}
                    </div>
                    <div className="text-sm text-green-800">Total Uploads</div>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      {rangeData.summary.total_keywords}
                    </div>
                    <div className="text-sm text-purple-800">Total Keywords</div>
                  </div>
                  <div className="bg-orange-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-orange-600">
                      {Math.round(rangeData.summary.avg_confidence * 100)}%
                    </div>
                    <div className="text-sm text-orange-800">Avg Confidence</div>
                  </div>
                </div>
              </div>

              {/* Unique Papers */}
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Unique Papers Processed</h3>
                {rangeData.unique_papers.length > 0 ? (
                  <div className="space-y-2">
                    {rangeData.unique_papers.map((paper, index) => (
                      <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <div className="font-medium text-gray-900">{paper.title}</div>
                        <div className="text-sm text-gray-500">
                          {formatTimestamp(paper.first_seen)}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">No papers found in this date range.</p>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
