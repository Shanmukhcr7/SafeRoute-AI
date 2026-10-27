import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { 
  ShieldAlert, 
  Compass, 
  Cpu, 
  Activity, 
  MapPin, 
  CheckCircle2, 
  AlertTriangle,
  Zap
} from 'lucide-react';
import { api } from '../services/api';

export default function Navbar() {
  const [apiOnline, setApiOnline] = useState(false);
  const [zoneCount, setZoneCount] = useState(89726);

  useEffect(() => {
    api.getStatus()
      .then(res => {
        setApiOnline(res.status === 'online');
        if (res.database?.indexed_h3_zones) {
          setZoneCount(res.database.indexed_h3_zones);
        }
      })
      .catch(() => setApiOnline(false));

    const interval = setInterval(() => {
      api.getStatus()
        .then(res => setApiOnline(res.status === 'online'))
        .catch(() => setApiOnline(false));
    }, 15000);

    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { to: '/', label: 'Mission Control', icon: Activity },
    { to: '/navigation', label: 'Live Navigation', icon: Compass },
    { to: '/analytics', label: 'AI Analytics', icon: Cpu },
    { to: '/digital-twin', label: 'Digital Twin', icon: Zap },
    { to: '/france-map', label: 'National Risk Map', icon: MapPin },
  ];

  return (
    <header className="sticky top-0 z-50 bg-slate-900/90 backdrop-blur-md border-b border-slate-800 text-slate-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/30">
              <ShieldAlert className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                  SafeRoute-AI
                </span>
                <span className="px-2 py-0.5 text-[10px] font-semibold bg-blue-500/20 text-blue-400 border border-blue-500/30 rounded-full">
                  ADAS v2.0
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">
                Autonomous Risk Assessment & Dynamic Guidance Engine
              </p>
            </div>
          </div>

          {/* Nav Links */}
          <nav className="hidden md:flex items-center space-x-1 lg:space-x-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
                      isActive
                        ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30 font-semibold'
                        : 'text-slate-300 hover:text-white hover:bg-slate-800/80'
                    }`
                  }
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>

          {/* Status Indicator */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-800/80 border border-slate-700/60 text-xs">
              <span className="relative flex h-2.5 w-2.5">
                {apiOnline && (
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                )}
                <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${apiOnline ? 'bg-emerald-500' : 'bg-amber-500'}`}></span>
              </span>
              <span className="font-medium text-slate-200">
                {apiOnline ? `FastAPI (${(zoneCount / 1000).toFixed(0)}k H3)` : 'Connecting...'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile nav */}
      <div className="md:hidden flex overflow-x-auto px-4 py-2 bg-slate-900 border-t border-slate-800 gap-1 scrollbar-none">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs whitespace-nowrap ${
                  isActive
                    ? 'bg-blue-600 text-white font-medium'
                    : 'text-slate-400 hover:bg-slate-800'
                }`
              }
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </div>
    </header>
  );
}
