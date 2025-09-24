import { useState, useEffect } from 'react';
import { getDashboardStats, getDashboardAnalytics } from '../api/importer';
import StatsCard from '../components/dashboard/StatsCard';
import SystemHealth from '../components/dashboard/SystemHealth';
import RecentActivity from '../components/dashboard/RecentActivity';
import KeywordAnalytics from '../components/dashboard/KeywordAnalytics';

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [statsData, analyticsData] = await Promise.all([
        getDashboardStats(),
        getDashboardAnalytics()
      ]);
      setStats(statsData);
      setAnalytics(analyticsData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <span className="text-red-400">❌</span>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error loading dashboard</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
            <button
              onClick={loadDashboardData}
              className="mt-2 text-sm text-red-600 hover:text-red-500"
            >
              Try again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Overview of your KDB-importer system</p>
        </div>
        <button
          onClick={loadDashboardData}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          Refresh
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Papers Imported"
          value={stats?.total_papers_imported || 0}
          icon="📄"
          color="blue"
        />
        <StatsCard
          title="Uploaded to Paperless"
          value={stats?.papers_uploaded_to_paperless || 0}
          icon="📤"
          color="green"
        />
        <StatsCard
          title="Keywords Extracted"
          value={stats?.total_keywords_extracted || 0}
          icon="🏷️"
          color="purple"
        />
        <StatsCard
          title="Avg Confidence"
          value={`${Math.round((stats?.average_confidence_score || 0) * 100)}%`}
          icon="🎯"
          color="orange"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-6">
          <SystemHealth health={stats?.system_health || {}} />
          <RecentActivity activities={stats?.recent_activity || []} />
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          <KeywordAnalytics analytics={analytics?.keyword_analytics || {}} />
          
          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <a
                href="/"
                className="block w-full px-4 py-2 bg-blue-600 text-white text-center rounded-md hover:bg-blue-700 transition-colors"
              >
                📄 Import New Papers
              </a>
              <a
                href="/assistant"
                className="block w-full px-4 py-2 bg-purple-600 text-white text-center rounded-md hover:bg-purple-700 transition-colors"
              >
                🤖 Open Assistant
              </a>
              <a
                href="https://kdb.mohamedh.me"
                target="_blank"
                rel="noopener noreferrer"
                className="block w-full px-4 py-2 bg-green-600 text-white text-center rounded-md hover:bg-green-700 transition-colors"
              >
                📚 View Paperless-ngx
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Features Overview */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">System Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-3xl mb-2">🤖</div>
            <h4 className="font-medium text-gray-900">AI Keyword Extraction</h4>
            <p className="text-sm text-gray-600">GPT-4 powered keyword extraction with confidence scoring</p>
          </div>
          <div className="text-center">
            <div className="text-3xl mb-2">📤</div>
            <h4 className="font-medium text-gray-900">Paperless Integration</h4>
            <p className="text-sm text-gray-600">Seamless upload to Paperless-ngx with enhanced metadata</p>
          </div>
          <div className="text-center">
            <div className="text-3xl mb-2">🏷️</div>
            <h4 className="font-medium text-gray-900">Smart Validation</h4>
            <p className="text-sm text-gray-600">Intelligent keyword validation and suggestion system</p>
          </div>
        </div>
      </div>
    </div>
  );
}
