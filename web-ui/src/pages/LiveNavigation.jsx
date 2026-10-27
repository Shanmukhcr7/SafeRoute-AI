import React, { useState, useEffect } from 'react';
import { 
  Compass, 
  CloudSun, 
  CloudRain, 
  CloudSnow, 
  CloudFog, 
  Sun, 
  Moon, 
  ShieldCheck, 
  ShieldAlert, 
  AlertTriangle,
  Route,
  Clock,
  Sparkles,
  ArrowRight,
  RefreshCw
} from 'lucide-react';
import LeafletSimulator from '../components/LeafletSimulator';
import { api } from '../services/api';

const DEFAULT_ROUTES = [
  {
    id: 'paris_lyon_A',
    name: 'paris_lyon_A',
    via: 'A6 Highway (Direct)',
    distance_km: 465.9,
    duration_minutes: 297.9,
    safety_score: 87.3,
    avg_risk: 15.3,
    critical_zones: 1,
    recommended: true,
  },
  {
    id: 'paris_lyon_B',
    name: 'paris_lyon_B',
    via: 'Dijon (Scenic)',
    distance_km: 511.1,
    duration_minutes: 337.1,
    safety_score: 72.0,
    avg_risk: 16.0,
    critical_zones: 4,
    recommended: false,
  },
  {
    id: 'paris_lyon_C',
    name: 'paris_lyon_C',
    via: 'Clermont-Ferrand (Western)',
    distance_km: 589.1,
    duration_minutes: 392.7,
    safety_score: 42.7,
    avg_risk: 14.5,
    critical_zones: 10,
    recommended: false,
  },
];

export default function LiveNavigation() {
  const [selectedRouteId, setSelectedRouteId] = useState('paris_lyon_A');
  const [weather, setWeather] = useState('Clear');
  const [timeOfDay, setTimeOfDay] = useState('Day');

  const [routeAnalysis, setRouteAnalysis] = useState(null);
  const [comparisonRoutes, setComparisonRoutes] = useState(DEFAULT_ROUTES);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch corridor analysis for the selected route
  const fetchAnalysis = () => {
    setLoading(true);
    setError(null);
    api.analyzeRoute(selectedRouteId, weather, timeOfDay)
      .then((data) => {
        if (data && data.geometry) {
          setRouteAnalysis(data);
          setError(null);
        } else {
          setError('No geometry received for corridor.');
        }
      })
      .catch((err) => {
        console.error('Route analysis error:', err);
        setError('Failed to compute route corridor. Ensure backend is running.');
      })
      .finally(() => {
        setLoading(false);
      });
  };

  // Re-run corridor analysis whenever route, weather, or time of day changes
  useEffect(() => {
    fetchAnalysis();
  }, [selectedRouteId, weather, timeOfDay]);

  // Re-run comparison across all routes when weather or lighting changes
  useEffect(() => {
    api.compareRoutes(weather, timeOfDay)
      .then((compData) => {
        if (compData?.routes && compData.routes.length > 0) {
          setComparisonRoutes(compData.routes);
        }
      })
      .catch((err) => {
        console.warn('Routes comparison API fallback:', err);
      });
  }, [weather, timeOfDay]);

  const weatherOptions = [
    { label: 'Clear', icon: CloudSun, value: 'Clear' },
    { label: 'Rain', icon: CloudRain, value: 'Rain' },
    { label: 'Snow', icon: CloudSnow, value: 'Snow' },
    { label: 'Fog', icon: CloudFog, value: 'Fog' },
  ];

  const timeOptions = [
    { label: 'Day', icon: Sun, value: 'Day' },
    { label: 'Night', icon: Moon, value: 'Night' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Page Title & Environment Simulator Panel */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900/90 to-blue-950/40 border border-slate-800 shadow-xl">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div>
            <div className="flex items-center space-x-2 text-blue-400 text-xs font-bold uppercase tracking-wider mb-1">
              <Compass className="w-4 h-4" />
              <span>Real-Time ADAS Dynamic Risk Engine</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
              AI Navigation & Hotspot Simulator
            </h1>
            <p className="text-sm text-slate-400 mt-1 max-w-xl">
              Dynamically evaluates road stretches using Uber H3 indexing and adjusts risk using HistGradientBoosting based on weather and nocturnal conditions.
            </p>
          </div>

          {/* Environment Controls */}
          <div className="flex flex-wrap items-center gap-4 bg-slate-950/60 p-3 rounded-xl border border-slate-800">
            {/* Weather Selector */}
            <div>
              <span className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                Current Weather
              </span>
              <div className="flex bg-slate-900 p-1 rounded-lg border border-slate-800">
                {weatherOptions.map((w) => {
                  const Icon = w.icon;
                  const active = weather === w.value;
                  return (
                    <button
                      key={w.value}
                      onClick={() => setWeather(w.value)}
                      className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                        active 
                          ? 'bg-blue-600 text-white shadow-sm font-semibold' 
                          : 'text-slate-400 hover:text-white'
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                      <span>{w.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Time of Day */}
            <div>
              <span className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                Lighting Condition
              </span>
              <div className="flex bg-slate-900 p-1 rounded-lg border border-slate-800">
                {timeOptions.map((t) => {
                  const Icon = t.icon;
                  const active = timeOfDay === t.value;
                  return (
                    <button
                      key={t.value}
                      onClick={() => setTimeOfDay(t.value)}
                      className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                        active 
                          ? 'bg-indigo-600 text-white shadow-sm font-semibold' 
                          : 'text-slate-400 hover:text-white'
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                      <span>{t.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Alternative Route Comparison Cards */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-base font-bold text-white flex items-center space-x-2">
            <Route className="w-4 h-4 text-blue-400" />
            <span>Select Route Corridor (Paris → Lyon)</span>
          </h2>
          <span className="text-xs text-slate-400">
            ML Safety Scoring dynamically recalibrated
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {comparisonRoutes.map((r) => {
            const isSelected = selectedRouteId === r.id;
            const isRec = r.recommended;
            return (
              <div
                key={r.id}
                onClick={() => setSelectedRouteId(r.id)}
                className={`p-4 rounded-xl border cursor-pointer transition-all duration-200 relative ${
                  isSelected
                    ? 'bg-slate-900 border-blue-500 ring-2 ring-blue-500/30 shadow-lg shadow-blue-500/10'
                    : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900/80'
                }`}
              >
                {isRec && (
                  <span className="absolute top-3 right-3 px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center space-x-1">
                    <Sparkles className="w-3 h-3" />
                    <span>AI Recommended</span>
                  </span>
                )}

                <h3 className="font-bold text-white text-base pr-28">
                  {r.via}
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Distance: {r.distance_km} km • ETA: {r.duration_minutes ? (r.duration_minutes / 60).toFixed(1) : 4.5} hrs
                </p>

                <div className="grid grid-cols-3 gap-2 mt-4 pt-3 border-t border-slate-800/80 text-center">
                  <div>
                    <span className="block text-[10px] text-slate-400 uppercase font-medium">Safety Score</span>
                    <span className={`text-base font-black ${r.safety_score >= 80 ? 'text-emerald-400' : (r.safety_score >= 60 ? 'text-amber-400' : 'text-red-400')}`}>
                      {r.safety_score}/100
                    </span>
                  </div>
                  <div>
                    <span className="block text-[10px] text-slate-400 uppercase font-medium">Avg Risk</span>
                    <span className="text-base font-extrabold text-white">
                      {r.avg_risk}
                    </span>
                  </div>
                  <div>
                    <span className="block text-[10px] text-slate-400 uppercase font-medium">Critical Zones</span>
                    <span className="text-base font-extrabold text-red-400">
                      {r.critical_zones}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Interactive Map & ADAS Simulator */}
      {routeAnalysis ? (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 rounded-full bg-emerald-400 animate-ping"></span>
              <h2 className="text-lg font-bold text-white">
                Live Simulation: {routeAnalysis.via}
              </h2>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-xs px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-slate-300">
                Active Environment: <b>{weather}</b> during <b>{timeOfDay}</b>
              </span>
              <button
                onClick={fetchAnalysis}
                className="p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 transition-all border border-slate-700"
                title="Refresh corridor analysis"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>

          <LeafletSimulator
            geometry={routeAnalysis.geometry}
            hotspots={routeAnalysis.hotspots}
            environment={{ weather, time_of_day: timeOfDay }}
          />
        </div>
      ) : error ? (
        <div className="w-full h-96 rounded-2xl bg-slate-900 border border-red-900/40 flex flex-col items-center justify-center space-y-4 p-6 text-center">
          <AlertTriangle className="w-12 h-12 text-red-400 animate-pulse" />
          <div>
            <h3 className="text-lg font-bold text-white">Route Analysis Disconnected</h3>
            <p className="text-xs text-slate-400 mt-1 max-w-md">
              {error}
            </p>
          </div>
          <button
            onClick={fetchAnalysis}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold transition-all shadow-lg shadow-blue-500/20 flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Retry Route Computation</span>
          </button>
        </div>
      ) : (
        <div className="w-full h-[620px] rounded-2xl bg-slate-900 border border-slate-800 flex flex-col items-center justify-center space-y-4">
          <div className="relative">
            <div className="w-16 h-16 rounded-full border-4 border-blue-500/20 border-t-blue-500 animate-spin"></div>
            <Compass className="w-8 h-8 text-blue-400 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
          </div>
          <div className="text-center">
            <p className="text-base font-bold text-white">Synthesizing H3 Route Corridor</p>
            <p className="text-xs text-slate-400 mt-1">
              Calibrating dynamic weather risk multipliers and collision hotspots...
            </p>
          </div>
        </div>
      )}

      {/* Hotspots Breakdown Table */}
      {routeAnalysis?.hotspots && routeAnalysis.hotspots.length > 0 && (
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white flex items-center space-x-2">
                <ShieldAlert className="w-4 h-4 text-red-400" />
                <span>Detected Hazard Zones along this Corridor</span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Top accident clusters identified via Uber H3 spatial resolution 8 indexing
              </p>
            </div>
            <span className="text-xs font-semibold text-slate-300 bg-slate-800 px-3 py-1 rounded-lg border border-slate-700">
              {routeAnalysis.hotspots.length} Total Monitored Hotspots
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider text-[10px] border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3">Severity Level</th>
                  <th className="py-2.5 px-3">H3 Zone ID</th>
                  <th className="py-2.5 px-3">Centroid (Lat, Lon)</th>
                  <th className="py-2.5 px-3">Dynamic AI Risk</th>
                  <th className="py-2.5 px-3">Base Historical</th>
                  <th className="py-2.5 px-3">Weather Multiplier</th>
                  <th className="py-2.5 px-3">ADAS Advisory</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-200">
                {routeAnalysis.hotspots.slice(0, 8).map((h) => {
                  const isFatal = h.level === 'FATAL';
                  const isCrit = h.level === 'CRITICAL';
                  const isHigh = h.level === 'HIGH';
                  return (
                    <tr key={h.h3_index} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-2.5 px-3">
                        <span className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                          isFatal ? 'bg-red-950 text-red-400 border border-red-800' :
                          isCrit ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                          isHigh ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' :
                          'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                        }`}>
                          {h.level}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 font-mono text-[11px] text-slate-400">
                        {h.h3_index}
                      </td>
                      <td className="py-2.5 px-3 text-slate-300">
                        {h.centroid[0].toFixed(4)}, {h.centroid[1].toFixed(4)}
                      </td>
                      <td className="py-2.5 px-3 font-extrabold text-white">
                        {h.score.toFixed(1)} / 100
                      </td>
                      <td className="py-2.5 px-3 text-slate-300 font-semibold">
                        {h.base_score.toFixed(1)}
                      </td>
                      <td className="py-2.5 px-3 font-semibold text-blue-400">
                        {h.multiplier.toFixed(2)}x
                      </td>
                      <td className="py-2.5 px-3 text-slate-300">
                        {isFatal ? 'Reduce speed to 30 km/h (Fatal cluster)' :
                         isCrit ? 'Reduce speed to 50 km/h (High risk)' :
                         'Exercise caution'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}