import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import MissionControl from './pages/MissionControl';
import LiveNavigation from './pages/LiveNavigation';
import AIAnalytics from './pages/AIAnalytics';
import DigitalTwin from './pages/DigitalTwin';
import FranceRiskMap from './pages/FranceRiskMap';

export default function App() {
  return (
    <Router>
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
        <Navbar />

        <main className="flex-1">
          <Routes>
            <Route path="/" element={<MissionControl />} />
            <Route path="/navigation" element={<LiveNavigation />} />
            <Route path="/analytics" element={<AIAnalytics />} />
            <Route path="/digital-twin" element={<DigitalTwin />} />
            <Route path="/france-map" element={<FranceRiskMap />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>

        <footer className="border-t border-slate-800 bg-slate-900/50 py-6 text-xs text-slate-400">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center space-x-2">
              <span className="font-bold text-slate-300">SafeRoute-AI</span>
              <span>•</span>
              <span>Intelligent Transportation Systems (ITS) & ADAS Dynamic Risk Multiplier</span>
            </div>
            <div className="flex items-center space-x-4">
              <a 
                href="http://127.0.0.1:8000/docs" 
                target="_blank" 
                rel="noreferrer"
                className="hover:text-blue-400 transition-colors"
              >
                FastAPI Swagger Docs
              </a>
              <span>•</span>
              <span>Uber H3 Res 8 + HistGradientBoosting</span>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}
