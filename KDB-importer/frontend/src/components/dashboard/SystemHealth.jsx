// frontend/src/components/dashboard/SystemHealth.jsx
export default function SystemHealth({ health }) {
  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
      case 'connected':
      case 'active':
        return 'text-green-600 bg-green-100';
      case 'warning':
        return 'text-yellow-600 bg-yellow-100';
      case 'error':
      case 'disconnected':
      case 'inactive':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
      case 'connected':
      case 'active':
        return '✅';
      case 'warning':
        return '⚠️';
      case 'error':
      case 'disconnected':
      case 'inactive':
        return '❌';
      default:
        return '❓';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">System Health</h3>
      <div className="space-y-3">
        {Object.entries(health).map(([key, status]) => (
          <div key={key} className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700 capitalize">
              {key.replace('_', ' ')}
            </span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(status)}`}>
              {getStatusIcon(status)} {status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
