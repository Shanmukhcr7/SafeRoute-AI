import React, { useState, useEffect } from 'react';
import { 
  Zap, 
  Play, 
  Pause, 
  RotateCcw, 
  Car, 
  ShieldAlert, 
  Activity, 
  Sliders,
  Clock,
  Gauge
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  CartesianGrid 
} from 'recharts';
import StatCard from '../components/StatCard';
import { api } from '../services/api';

export default function DigitalTwin() {
  const [telemetry, setTelemetry] = useState([]);
  const [timeIndex, setTimeIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    api.getTelemetry()
      .then(res => {
        if (res?.telemetry?.length > 0) {
          setTelemetry(res.telemetry);
        } else {
          // Realistic fallback telemetry simulation data
          const mock = [];
          for (let i = 0; i < 30; i++) {
            const min = String(i).padStart(2, '0');
            mock.push(
              { id: i*2, vehicle_id: 'VEH-01 (Highway ADAS)', timestamp: `10:${min}:00`, lat: 48.85 + i*0.01, lon: 2.35 + i*0.02, speed: 90 + Math.sin(i)*15, risk: 30 + (i > 15 ? 45 : 10), status: i > 15 ? 'CRITICAL' : 'NORMAL' },
              { id: i*2+1, vehicle_id: 'VEH-02 (Freight Convoy)', timestamp: `10:${min}:00`, lat: 45.76 + i*0.008, lon: 4.83 + i*0.015, speed: 75 + Math.cos(i)*10, risk: 25 + Math.random()*20, status: 'NORMAL' }
            );
          }
          setTelemetry(mock);
        }
      })
      .catch(() => {});
  }, []);

  // Distinct timestamps
  const timestamps = Array.from(new Set(telemetry.map(t => t.timestamp)));

  // Auto-playback loop
  useEffect(() => {
    let timer = null;
    if (isPlaying && timestamps.length > 0) {
      timer = setInterval(() => {
        setTimeIndex((prev) => {
          if (prev >= timestamps.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 800);
    }
    return () => clearInterval(timer);
  }, [isPlaying, timestamps.length]);

  const currentTimestamp = timestamps[timeIndex] || '10:00:00';
  const currentVehicles = telemetry.filter(t => t.timestamp === currentTimestamp);

  // Chart data formatted for timeline
  const chartData = timestamps.slice(0, timeIndex + 1).map((ts) => {
    const v1 = telemetry.find(t => t.timestamp === ts && t.vehicle_id.includes('VEH-01'));
    const v2 = telemetry.find(t => t.timestamp === ts && t.vehicle_id.includes('VEH-02'));
    return {
      timestamp: ts,
      v1Risk: v1 ? v1.risk : 0,
      v2Risk: v2 ? v2.risk : 0,
    };
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800 shadow-xl">
        <div className="flex items-center space-x-2 text-indigo-400 text-xs font-bold uppercase tracking-wider mb-1">
          <Zap className="w-4 h-4" />
          <span>Multi-Agent Fleet Telemetry Simulation</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
          Digital Twin Playback Engine
        </h1>
        <p className="text-sm text-slate-400 mt-1 max-w-xl">
          Synchronized temporal playback of vehicular speed profiles, GPS coordinates, and real-time hazard triggers as vehicles encounter H3 hotspots.
        </p>
      </div>

      {/* Playback Controls & Timeline Scrubber */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-xl space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="w-11 h-11 rounded-xl bg-blue-600 hover:bg-blue-500 text-white flex items-center justify-center shadow-lg shadow-blue-600/30 transition-all"
            >
              {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-0.5" />}
            </button>
            <button
              onClick={() => { setTimeIndex(0); setIsPlaying(false); }}
              className="w-11 h-11 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white flex items-center justify-center border border-slate-700 transition-all"
            >
              <RotateCcw className="w-5 h-5" />
            </button>
            <div>
              <div className="text-xs font-semibold text-slate-400">Current Mission Timestamp</div>
              <div className="text-base font-extrabold text-white flex items-center space-x-1.5">
                <Clock className="w-4 h-4 text-blue-400" />
                <span>{currentTimestamp}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2 text-xs text-slate-400">
            <span>Frame: </span>
            <span className="font-extrabold text-white">{timeIndex + 1} / {timestamps.length}</span>
          </div>
        </div>

        {/* Timeline Slider */}
        <div className="space-y-1">
          <input
            type="range"
            min="0"
            max={Math.max(0, timestamps.length - 1)}
            value={timeIndex}
            onChange={(e) => setTimeIndex(Number(e.target.value))}
            className="w-full accent-blue-500 cursor-pointer h-2 bg-slate-800 rounded-lg"
          />
          <div className="flex justify-between text-[11px] text-slate-400">
            <span>Start: {timestamps[0] || '10:00:00'}</span>
            <span>End: {timestamps[timestamps.length - 1] || '10:30:00'}</span>
          </div>
        </div>
      </div>

      {/* Real-Time Vehicle Status Cards */}
      <div className="space-y-3">
        <h2 className="text-base font-bold text-white flex items-center space-x-2">
          <Car className="w-4 h-4 text-blue-400" />
          <span>Active Connected Telemetry Nodes ({currentVehicles.length})</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {currentVehicles.map((v, idx) => {
            const isDanger = v.status === 'CRITICAL' || v.status === 'DANGER' || v.risk > 70;
            return (
              <div
                key={idx}
                className={`p-5 rounded-2xl border backdrop-blur-md shadow-xl transition-all ${
                  isDanger 
                    ? 'bg-red-950/30 border-red-500/40' 
                    : 'bg-slate-900/60 border-slate-800'
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${isDanger ? 'bg-red-500/20 text-red-400' : 'bg-blue-500/20 text-blue-400'}`}>
                      <Car className="w-4 h-4" />
                    </div>
                    <div>
                      <h3 className="font-bold text-white text-sm">{v.vehicle_id}</h3>
                      <p className="text-[11px] text-slate-400">GPS: {v.lat.toFixed(4)}, {v.lon.toFixed(4)}</p>
                    </div>
                  </div>
                  <span className={`px-2.5 py-1 rounded-full text-[10px] font-black uppercase ${
                    isDanger ? 'bg-red-500/20 text-red-400 border border-red-500/30 animate-pulse' : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  }`}>
                    {isDanger ? '⚠️ HAZARD ALERT' : 'NORMAL'}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3 pt-3 border-t border-slate-800/80">
                  <div>
                    <span className="block text-[10px] text-slate-400 font-medium uppercase">Velocity</span>
                    <span className="text-lg font-black text-white">{Math.round(v.speed)} km/h</span>
                  </div>
                  <div>
                    <span className="block text-[10px] text-slate-400 font-medium uppercase">Active Risk Index</span>
                    <span className={`text-lg font-black ${v.risk > 60 ? 'text-red-400' : 'text-emerald-400'}`}>
                      {v.risk.toFixed(1)} / 100
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Dynamic Risk Evolution Chart */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-xl space-y-3">
        <h2 className="text-base font-bold text-white">Dynamic Risk Progression Across Playback</h2>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="timestamp" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} domain={[0, 100]} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
              />
              <Line type="monotone" dataKey="v1Risk" stroke="#ef4444" strokeWidth={2.5} dot={false} name="VEH-01 (Highway ADAS)" />
              <Line type="monotone" dataKey="v2Risk" stroke="#3b82f6" strokeWidth={2} dot={false} name="VEH-02 (Freight Convoy)" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
