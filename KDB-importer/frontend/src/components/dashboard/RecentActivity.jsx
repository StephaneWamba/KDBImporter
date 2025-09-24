// frontend/src/components/dashboard/RecentActivity.jsx
export default function RecentActivity({ activities = [] }) {
  const getActivityIcon = (type) => {
    switch (type) {
      case 'import':
        return '📄';
      case 'keyword':
        return '🏷️';
      case 'upload':
        return '📤';
      case 'search':
        return '🔍';
      default:
        return '📋';
    }
  };

  const getActivityColor = (type) => {
    switch (type) {
      case 'import':
        return 'text-blue-600';
      case 'keyword':
        return 'text-purple-600';
      case 'upload':
        return 'text-green-600';
      case 'search':
        return 'text-orange-600';
      default:
        return 'text-gray-600';
    }
  };

  if (activities.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="text-center py-8">
          <p className="text-gray-500">No recent activity</p>
          <p className="text-sm text-gray-400 mt-2">Start importing papers to see activity here</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
      <div className="space-y-3">
        {activities.map((activity, index) => (
          <div key={index} className="flex items-center space-x-3">
            <span className="text-lg">{getActivityIcon(activity.type)}</span>
            <div className="flex-1 min-w-0">
              <p className={`text-sm font-medium ${getActivityColor(activity.type)}`}>
                {activity.title}
              </p>
              <p className="text-xs text-gray-500">{activity.timestamp}</p>
            </div>
            {activity.status && (
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                activity.status === 'success' 
                  ? 'text-green-600 bg-green-100' 
                  : 'text-red-600 bg-red-100'
              }`}>
                {activity.status}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
