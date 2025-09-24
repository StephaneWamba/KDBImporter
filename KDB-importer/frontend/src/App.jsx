import { Routes, Route } from 'react-router-dom';
import Sidebar from './components/shared/Sidebar';
import ImportPage from './pages/ImportPage';
import DashboardPage from './pages/DashboardPage';
import AssistantPage from './pages/AssistantPage';
import HistoryPage from './pages/HistoryPage';
import 'react-toastify/dist/ReactToastify.css';
import { ToastContainer } from 'react-toastify';

function App() {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6 bg-white">
        <Routes>
          <Route path="/" element={<ImportPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/assistant" element={<AssistantPage />} />
          <Route path="/history" element={<HistoryPage />} />
        </Routes>
        <ToastContainer />
      </main>
    </div>
  );
}

export default App;
