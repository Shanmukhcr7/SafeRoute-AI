import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { Home, Map as MapIcon, BarChart3, Globe } from 'lucide-react';
import HomePage from './pages/Home';
import MapPage from './pages/Map';
import FranceMap from './pages/FranceMap';
import AnalyticsPage from './pages/Analytics';

function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen bg-[#0f111a] text-[#E2E8F0]">
        {/* Sidebar */}
        <aside className="w-64 bg-[#1a1d2d] border-r border-[#2d324d] flex flex-col">
          <div className="p-6 border-b border-[#2d324d]">
            <h1 className="text-xl font-bold text-gradient flex items-center gap-2">
              <MapIcon className="text-blue-500" />
              Road Risk AI
            </h1>
          </div>
          <nav className="flex-1 p-4 space-y-2">
            <NavLink to="/" className={({ isActive }) => `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400' : 'hover:bg-white/5'}`}>
              <Home size={20} />
              <span>Project Overview</span>
            </NavLink>
            <NavLink to="/france" className={({ isActive }) => `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400' : 'hover:bg-white/5'}`}>
              <Globe size={20} />
              <span>France Risk Map</span>
            </NavLink>
            <NavLink to="/map" className={({ isActive }) => `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400' : 'hover:bg-white/5'}`}>
              <MapIcon size={20} />
              <span>Live Map Simulation</span>
            </NavLink>
            <NavLink to="/analytics" className={({ isActive }) => `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${isActive ? 'bg-blue-600/20 text-blue-400' : 'hover:bg-white/5'}`}>
              <BarChart3 size={20} />
              <span>AI Analytics</span>
            </NavLink>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-auto p-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/france" element={<FranceMap />} />
            <Route path="/map" element={<MapPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
