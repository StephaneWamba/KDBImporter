// frontend/src/components/dashboard/KeywordAnalytics.jsx
export default function KeywordAnalytics({ analytics }) {
  const { most_used_keywords = [], domain_distribution = {}, confidence_trends = [] } = analytics;

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Keyword Analytics</h3>
      
      {/* Most Used Keywords */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Most Used Keywords</h4>
        {most_used_keywords.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {most_used_keywords.slice(0, 10).map((keyword, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
              >
                {keyword.keyword} ({keyword.count})
              </span>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No keywords extracted yet</p>
        )}
      </div>

      {/* Domain Distribution */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Domain Distribution</h4>
        {Object.keys(domain_distribution).length > 0 ? (
          <div className="space-y-2">
            {Object.entries(domain_distribution).slice(0, 5).map(([domain, count]) => (
              <div key={domain} className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{domain}</span>
                <div className="flex items-center space-x-2">
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-purple-500 h-2 rounded-full" 
                      style={{ width: `${(count / Math.max(...Object.values(domain_distribution))) * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium text-gray-900">{count}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No domain data available</p>
        )}
      </div>

      {/* Confidence Trends */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 mb-3">Confidence Trends</h4>
        {confidence_trends.length > 0 ? (
          <div className="text-sm text-gray-600">
            <p>Average Confidence: <span className="font-medium text-green-600">
              {confidence_trends.reduce((sum, trend) => sum + trend.confidence, 0) / confidence_trends.length * 100}%
            </span></p>
            <p>Total Extractions: <span className="font-medium">{confidence_trends.length}</span></p>
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No confidence data available</p>
        )}
      </div>
    </div>
  );
}
