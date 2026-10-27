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
  RefreshCw,
  Gauge,
  MapPin,
  Play,
  Settings,
  Car,
  Navigation,
  CheckCircle2,
  Sliders,
  Zap,
  RotateCcw
} from 'lucide-react';
import LeafletSimulator from '../components/LeafletSimulator';
import { api } from '../services/api';

const DEFAULT_ROUTES = [
  {
    id: 'paris_lyon_A',
    name: 'paris_lyon_A',
    via: 'A6 Highway (Direct)',
    description: 'Autoroute du Soleil • Fastest freight & commuter route',
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
    via: 'Dijon (Scenic Corridor)',
    description: 'A5 / A31 via Burgundy • Secondary rural transitions',
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
    via: 'Clermont-Ferrand (Western Bypass)',
    description: 'A71 / A89 Central Massif • High elevation curves',
    distance_km: 589.1,
    duration_minutes: 392.7,
    safety_score: 42.7,
    avg_risk: 14.5,
    critical_zones: 10,
    recommended: false,
  },
];

const CITY_OPTIONS = [
  { id: 'Paris', name: 'Paris (Île-de-France)', lat: 48.8566, lon: 2.3522 },
  { id: 'Lyon', name: 'Lyon (Auvergne-Rhône-Alpes)', lat: 45.7640, lon: 4.8357 },
  { id: 'Marseille', name: 'Marseille (PACA)', lat: 43.2965, lon: 5.3698 },
  { id: 'Lille', name: 'Lille (Hauts-de-France)', lat: 50.6292, lon: 3.0573 },
  { id: 'Bordeaux', name: 'Bordeaux (Nouvelle-Aquitaine)', lat: 44.8378, lon: -0.5792 },
];

export default function LiveNavigation() {
  // Navigation & Origin/Destination State
  const [origin, setOrigin] = useState('Paris');
  const [destination, setDestination] = useState('Lyon');
  const [selectedRouteId, setSelectedRouteId] = useState('paris_lyon_A');

  // Atmospheric & Vehicle Actions
  const [weather, setWeather] = useState('Rain');
  const [timeOfDay, setTimeOfDay] = useState('Night');
  const [speedKmh, setSpeedKmh] = useState(130);

  // Simulation execution state - FALSE by default so it does NOT auto-run
  const [isSimulationRunning, setIsSimulationRunning] = useState(false);

  // Corridor Analysis & Comparison Data
  const [routeAnalysis, setRouteAnalysis] = useState(null);
  const [comparisonRoutes, setComparisonRoutes] = useState(DEFAULT_ROUTES);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch corridor analysis
  const fetchAnalysis = async (autoLaunch = false) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.analyzeRoute(selectedRouteId, weather, timeOfDay);
      if (data && data.geometry) {
        setRouteAnalysis(data);
        setError(null);
        if (autoLaunch) {
          setIsSimulationRunning(true);
        }
      } else {
        setError('No geometry received for corridor.');
      }
    } catch (err) {
      console.error('Route analysis error:', err);
      setError('Failed to compute route corridor. Ensure backend is running.');
    } finally {
      setLoading(false);
    }
  };

  // Re-run comparison across routes when weather or lighting changes
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

  // Handle user clicking "Run Simulation"
  const handleRunSimulation = async () => {
    // If corridor is not yet loaded for these actions, fetch it and launch
    if (!routeAnalysis || routeAnalysis.route_id !== selectedRouteId || routeAnalysis.environment?.weather !== weather || routeAnalysis.environment?.time_of_day !== timeOfDay) {
      await fetchAnalysis(true);
    } else {
      setIsSimulationRunning(true);
    }
  };

  // Weather configuration options
  const weatherOptions = [
    { 
      label: 'Rain', 
      icon: CloudRain, 
      value: 'Rain', 
      color: 'text-blue-400', 
      multiplier: '+35%', 
      desc: 'Wet asphalt & hydroplaning' 
    },
    { 
      label: 'Clear', 
      icon: CloudSun, 
      value: 'Clear', 
      color: 'text-amber-400', 
      multiplier: '1.00x', 
      desc: 'Optimal dry grip conditions' 
    },
    { 
      label: 'Snow', 
      icon: CloudSnow, 
      value: 'Snow', 
      color: 'text-cyan-300', 
      multiplier: '+60%', 
      desc: 'Sub-zero low friction' 
    },
    { 
      label: 'Fog', 
      icon: CloudFog, 
      value: 'Fog', 
      color: 'text-slate-300', 
      multiplier: '+45%', 
      desc: 'Optical range < 50 meters' 
    },
  ];

  // Lighting options
  const timeOptions = [
    { 
      label: 'Night', 
      icon: Moon, 
      value: 'Night', 
      color: 'text-indigo-400', 
      desc: 'Headlight constraints & nocturnal fatigue' 
    },
    { 
      label: 'Day', 
      icon: Sun, 
      value: 'Day', 
      color: 'text-amber-400', 
      desc: 'Standard daylight visibility' 
    },
  ];

  // Speed presets
  const speedPresets = [
    { label: 'City / Wet', speed: 60 },
    { label: 'Eco Highway', speed: 90 },
    { label: 'Autoroute 130', speed: 130 },
    { label: 'Fast Demo', speed: 200 },
  ];

  const currentRoute = comparisonRoutes.find(r => r.id === selectedRouteId) || comparisonRoutes[0];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Page Title & Control State Banner */}
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
            <p className="text-sm text-slate-400 mt-1 max-w-2xl">
              Choose your origin, destination, corridor, atmospheric hazards, and vehicle cruise speed. 
              Once configured, run the simulation to monitor dynamic ML risk multipliers and real-time ADAS collision alerts.
            </p>
          </div>

          {/* Quick Status / Toggle */}
          <div className="flex items-center space-x-3">
            {isSimulationRunning ? (
              <button
                onClick={() => setIsSimulationRunning(false)}
                className="px-4 py-2 rounded-xl bg-slate-800 text-slate-200 hover:text-white hover:bg-slate-700 font-bold text-xs flex items-center space-x-2 border border-slate-700 transition-all shadow-md"
              >
                <Settings className="w-4 h-4 text-blue-400" />
                <span>Modify Actions / Setup</span>
              </button>
            ) : (
              <span className="px-3 py-1.5 rounded-xl bg-blue-950/60 border border-blue-800/60 text-blue-400 text-xs font-semibold flex items-center space-x-2">
                <span className="w-2 h-2 rounded-full bg-blue-400"></span>
                <span>Configuring Mission Parameters</span>
              </span>
            )}
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* VIEW 1: MISSION CONFIGURATION PANEL (Displayed when !isSimulationRunning) */}
      {/* ========================================================================= */}
      {!isSimulationRunning ? (
        <div className="space-y-8 animate-fadeIn">
          {/* Section 1: Origin & Destination Selector */}
          <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 shadow-xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
              <div className="flex items-center space-x-2">
                <MapPin className="w-4 h-4 text-emerald-400" />
                <h2 className="text-base font-bold text-white uppercase tracking-wider text-xs">
                  Step 1: Journey Endpoints (From → To)
                </h2>
              </div>
              <span className="text-[11px] font-semibold text-slate-400 bg-slate-800/80 px-2.5 py-0.5 rounded-md border border-slate-700">
                France National Arteries
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
              {/* Origin */}
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                  Origin (Departure City)
                </label>
                <div className="relative">
                  <select
                    value={origin}
                    onChange={(e) => setOrigin(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl py-3 px-4 text-sm font-semibold text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all cursor-pointer appearance-none"
                  >
                    {CITY_OPTIONS.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name}
                      </option>
                    ))}
                  </select>
                  <MapPin className="w-4 h-4 text-emerald-400 absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none" />
                </div>
              </div>

              {/* Destination */}
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                  Destination (Arrival City)
                </label>
                <div className="relative">
                  <select
                    value={destination}
                    onChange={(e) => setDestination(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl py-3 px-4 text-sm font-semibold text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all cursor-pointer appearance-none"
                  >
                    {CITY_OPTIONS.filter(c => c.id !== origin).map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name}
                      </option>
                    ))}
                  </select>
                  <Navigation className="w-4 h-4 text-blue-400 absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none" />
                </div>
              </div>
            </div>
          </div>

          {/* Section 2: Route Corridor Selection */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Route className="w-4 h-4 text-blue-400" />
                <h2 className="text-base font-bold text-white uppercase tracking-wider text-xs">
                  Step 2: Select Route Corridor ({origin} → {destination})
                </h2>
              </div>
              <span className="text-xs text-slate-400">
                Click a corridor card to select your transit line
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
                    className={`p-5 rounded-2xl border cursor-pointer transition-all duration-200 relative ${
                      isSelected
                        ? 'bg-slate-900 border-blue-500 ring-2 ring-blue-500/40 shadow-xl shadow-blue-500/10'
                        : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900/80'
                    }`}
                  >
                    {isRec && (
                      <span className="absolute top-3 right-3 px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center space-x-1">
                        <Sparkles className="w-3 h-3" />
                        <span>AI Recommended</span>
                      </span>
                    )}

                    <div className="flex items-center space-x-2 mb-1">
                      <div className={`w-3 h-3 rounded-full border-2 ${isSelected ? 'border-blue-400 bg-blue-500' : 'border-slate-600'}`}></div>
                      <h3 className="font-bold text-white text-base">
                        {r.via}
                      </h3>
                    </div>

                    <p className="text-xs text-slate-400 mt-1">
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

          {/* Section 3: Atmospheric Hazards & Lighting Actions */}
          <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 shadow-xl space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
              <div className="flex items-center space-x-2">
                <Sliders className="w-4 h-4 text-cyan-400" />
                <h2 className="text-base font-bold text-white uppercase tracking-wider text-xs">
                  Step 3: Atmospheric Actions & Visibility
                </h2>
              </div>
              <span className="text-xs text-slate-400">
                Directly impacts HistGradientBoosting ML risk multipliers
              </span>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Weather Selection */}
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2.5">
                  Precipitation & Weather Action
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                  {weatherOptions.map((w) => {
                    const Icon = w.icon;
                    const active = weather === w.value;
                    return (
                      <button
                        key={w.value}
                        type="button"
                        onClick={() => setWeather(w.value)}
                        className={`p-3 rounded-xl border flex flex-col items-center justify-center text-center transition-all ${
                          active
                            ? 'bg-blue-600/20 border-blue-500 ring-2 ring-blue-500/30 text-white shadow-lg'
                            : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:text-white hover:border-slate-700'
                        }`}
                      >
                        <Icon className={`w-5 h-5 mb-1.5 ${active ? 'text-blue-400' : w.color}`} />
                        <span className="text-xs font-bold">{w.label}</span>
                        <span className="text-[10px] text-slate-400 mt-0.5">{w.multiplier}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Lighting / Time of Day */}
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2.5">
                  Lighting & Nocturnal Conditions
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {timeOptions.map((t) => {
                    const Icon = t.icon;
                    const active = timeOfDay === t.value;
                    return (
                      <button
                        key={t.value}
                        type="button"
                        onClick={() => setTimeOfDay(t.value)}
                        className={`p-3.5 rounded-xl border flex items-center space-x-3 transition-all ${
                          active
                            ? 'bg-indigo-600/20 border-indigo-500 ring-2 ring-indigo-500/30 text-white shadow-lg'
                            : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:text-white hover:border-slate-700'
                        }`}
                      >
                        <div className={`p-2 rounded-lg ${active ? 'bg-indigo-600 text-white' : 'bg-slate-900 text-slate-400'}`}>
                          <Icon className="w-5 h-5" />
                        </div>
                        <div className="text-left">
                          <span className="block text-xs font-bold">{t.label} Time</span>
                          <span className="text-[10px] text-slate-400">{t.desc.split('&')[0]}</span>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* Section 4: Vehicle Cruising Speed */}
          <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 shadow-xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
              <div className="flex items-center space-x-2">
                <Gauge className="w-4 h-4 text-blue-400" />
                <h2 className="text-base font-bold text-white uppercase tracking-wider text-xs">
                  Step 4: Vehicle Speed & Cruising Telemetry
                </h2>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-xs text-slate-400">Cruising Speed:</span>
                <span className="text-lg font-black text-blue-400">{speedKmh} km/h</span>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <span className="text-xs font-semibold text-slate-400 min-w-[50px]">30 km/h</span>
                <input
                  type="range"
                  min="30"
                  max="250"
                  step="5"
                  value={speedKmh}
                  onChange={(e) => setSpeedKmh(Number(e.target.value))}
                  className="w-full accent-blue-500 h-2 bg-slate-950 rounded-lg cursor-pointer"
                />
                <span className="text-xs font-semibold text-slate-400 min-w-[50px] text-right">250 km/h</span>
              </div>

              {/* Quick Presets */}
              <div className="flex flex-wrap items-center gap-3 pt-2">
                <span className="text-xs font-semibold text-slate-400">Quick Presets:</span>
                {speedPresets.map((p) => (
                  <button
                    key={p.speed}
                    type="button"
                    onClick={() => setSpeedKmh(p.speed)}
                    className={`px-3 py-1 rounded-lg text-xs font-bold border transition-all ${
                      speedKmh === p.speed
                        ? 'bg-blue-600 text-white border-blue-500 shadow-sm'
                        : 'bg-slate-950 text-slate-300 border-slate-800 hover:border-slate-700 hover:text-white'
                    }`}
                  >
                    {p.label} ({p.speed} km/h)
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Section 5: Mission Launch Summary & Action Button */}
          <div className="p-6 rounded-2xl bg-gradient-to-r from-blue-950/60 via-slate-900 to-indigo-950/60 border border-blue-800/50 shadow-2xl flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="space-y-1">
              <div className="flex items-center space-x-2 text-xs font-bold text-blue-400 uppercase tracking-wider">
                <Zap className="w-4 h-4" />
                <span>Simulation Configuration Ready</span>
              </div>
              <h3 className="text-lg font-black text-white">
                {origin} → {destination} via {currentRoute.via}
              </h3>
              <p className="text-xs text-slate-300 flex items-center space-x-2">
                <span>Conditions: <b>{weather}</b> • <b>{timeOfDay}</b></span>
                <span>•</span>
                <span>Target Speed: <b>{speedKmh} km/h</b></span>
                <span>•</span>
                <span>Corridor Distance: <b>{currentRoute.distance_km} km</b></span>
              </p>
            </div>

            <button
              onClick={handleRunSimulation}
              disabled={loading}
              className="w-full md:w-auto px-8 py-4 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-black text-base uppercase tracking-wider shadow-xl shadow-blue-500/25 flex items-center justify-center space-x-3 transition-all transform active:scale-95 cursor-pointer disabled:opacity-50"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  <span>Synthesizing Corridor...</span>
                </>
              ) : (
                <>
                  <Play className="w-5 h-5 fill-current" />
                  <span>Run Simulation</span>
                </>
              )}
            </button>
          </div>
        </div>
      ) : (
        /* ========================================================================= */
        /* VIEW 2: ACTIVE SIMULATION MODE (Shown when user hits "Run Simulation")    */
        /* ========================================================================= */
        <div className="space-y-6 animate-fadeIn">
          {/* Active Navigation Header with Reconfigure Button */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-md">
            <div className="flex items-center space-x-3">
              <span className="w-3 h-3 rounded-full bg-emerald-400 animate-ping"></span>
              <div>
                <h2 className="text-base font-bold text-white flex items-center space-x-2">
                  <span>Live Simulation:</span>
                  <span className="text-blue-400">{origin} → {destination}</span>
                  <span className="text-xs text-slate-400 font-normal">({routeAnalysis?.via || currentRoute.via})</span>
                </h2>
                <div className="flex items-center space-x-3 text-xs text-slate-400 mt-0.5">
                  <span>Weather: <b className="text-slate-200">{weather}</b></span>
                  <span>•</span>
                  <span>Lighting: <b className="text-slate-200">{timeOfDay}</b></span>
                  <span>•</span>
                  <span>Cruising: <b className="text-blue-400">{speedKmh} km/h</b></span>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <button
                onClick={() => setIsSimulationRunning(false)}
                className="px-4 py-2 rounded-xl bg-slate-800 text-slate-200 hover:text-white hover:bg-slate-700 text-xs font-bold flex items-center space-x-2 border border-slate-700 transition-all shadow-sm"
                title="Change weather, speed, corridor or endpoints"
              >
                <Settings className="w-3.5 h-3.5 text-blue-400" />
                <span>Reconfigure Parameters</span>
              </button>
            </div>
          </div>

          {/* Interactive Simulator Component */}
          {routeAnalysis ? (
            <LeafletSimulator
              geometry={routeAnalysis.geometry}
              hotspots={routeAnalysis.hotspots}
              environment={{ weather, time_of_day: timeOfDay }}
              initialSpeed={speedKmh}
              autoStart={true}
              onReconfigure={() => setIsSimulationRunning(false)}
            />
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
                onClick={() => fetchAnalysis(true)}
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
                      const score = h.score || 0;
                      const isRed = score >= 80;
                      const isBlack = score >= 45 && score < 80;
                      const isOrange = score < 45;
                      return (
                        <tr key={h.h3_index} className="hover:bg-slate-800/40 transition-colors">
                          <td className="py-2.5 px-3">
                            <span className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                              isRed ? 'bg-red-950 text-red-400 border border-red-800' :
                              isBlack ? 'bg-black text-slate-100 border border-slate-600' :
                              'bg-orange-500/20 text-orange-400 border border-orange-500/30'
                            }`}>
                              {isRed ? '80+ SEVERE (RED)' : (isBlack ? 'MEDIUM (BLACK)' : 'LEAST (ORANGE)')}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 font-mono text-[11px] text-slate-400">
                            {h.h3_index}
                          </td>
                          <td className="py-2.5 px-3 text-slate-300">
                            {h.centroid[0].toFixed(4)}, {h.centroid[1].toFixed(4)}
                          </td>
                          <td className="py-2.5 px-3 font-extrabold text-white">
                            {score.toFixed(1)} / 100
                          </td>
                          <td className="py-2.5 px-3 text-slate-300 font-semibold">
                            {(h.base_score || score).toFixed(1)}
                          </td>
                          <td className="py-2.5 px-3 font-semibold text-blue-400">
                            {(h.multiplier || 1.0).toFixed(2)}x
                          </td>
                          <td className="py-2.5 px-3 text-slate-300">
                            {isRed ? 'Reduce speed to 35 km/h (Severe zone)' :
                             isBlack ? 'Reduce speed to 65 km/h (Medium risk)' :
                             'Exercise normal caution'}
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
      )}
    </div>
  );
}