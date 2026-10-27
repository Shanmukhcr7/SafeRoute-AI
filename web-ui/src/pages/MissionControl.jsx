import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Activity, 
  ShieldAlert, 
  AlertTriangle, 
  Navigation, 
  CloudRain, 
  Cpu, 
  CheckCircle,
  Clock,
  ArrowRight
} from 'lucide-react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  CartesianGrid
} from 'recharts';
import StatCard from '../components/StatCard';
import { api } from '../services/api';

export default function MissionControl() {
  const navigate = useNavigate();
  const [kpis, setKpis] = useState({
    active_vehicles: 4,
    avg_fleet_risk: 34.6,
    critical_alerts_24h: 12,
    current_weather: 'Rain',
    latency_ms: 4.8,
  });
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  // Sample fleet risk telemetry over time
  const telemetryTrend = [
    { time: '10:00', avgRisk: 28, maxRisk: 45, vehicles: 4 },
    { time: '10:15', avgRisk: 32, maxRisk: 58, vehicles: 4 },
    { time: '10:30', avgRisk: 48, maxRisk: 76, vehicles: 4 },
    { time: '10:45', avgRisk: 62, maxRisk: 91, vehicles: 4 },
    { time: '11:00', avgRisk: 41, maxRisk: 69, vehicles: 4 },
    { time: '11:15', avgRisk: 35, maxRisk: 52, vehicles: 4 },
    { time: '11:30', avgRisk: 34, maxRisk: 49, vehicles: 4 },
  ];

  const riskDistribution = [
    { level: 'Safe (0-20)', count: 75108, fill: '#10b981' },
    { level: 'Moderate (21-45)', count: 10732, fill: '#fbbf24' },
    { level: 'High (46-64)', count: 1978, fill: '#f97316' },
    { level: 'Critical (65-79)', count: 1092, fill: '#ef4444' },
    { level: 'Fatal (80-100)', count: 816, fill: '#dc2626' },
  ];

  useEffect(() => {
    Promise.all([
      api.getKpis().catch(() => null),
      api.getAlerts().catch(() => null),
    ]).then(([kpiData, alertData]) => {
      if (kpiData) setKpis(kpiData);
      if (alertData?.alerts) setAlerts(alertData.alerts);
      setLoading(false);
    });
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Hero Welcome & Quick Launch */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-blue-950/60 via-slate-900 to-indigo-950/40 border border-slate-800 shadow-xl">
        <div>
          <div className="flex items-center space-x-2 text-blue-400 text-xs font-bold uppercase tracking-wider mb-1">
            <Activity className="w-4 h-4 animate-pulse" />
            <span>Autonomous Transportation Command Center</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            SafeRoute-AI Mission Control
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-xl">
            Live telemetry monitoring, Uber H3 spatial hazard indexing, and real-time ADAS risk multipliers across France.
          </p>
        </div>

        <button
          onClick={() => navigate('/navigation')}
          className="inline-flex items-center justify-center space-x-2 px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm shadow-lg shadow-blue-600/30 transition-all hover:scale-105"
        >
          <span>Launch Live Navigation</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Active Digital Twins"
          value={kpis.active_vehicles}
          subtitle="Vehicles transmitting telemetry"
          icon={Navigation}
          color="blue"
          delta="Stable"
          deltaColor="blue"
        />
        <StatCard
          title="Fleet Dynamic Risk"
          value={`${kpis.avg_fleet_risk}/100`}
          subtitle="Real-time environmental risk"
          icon={ShieldAlert}
          color={kpis.avg_fleet_risk > 50 ? "red" : "amber"}
          delta={kpis.avg_fleet_risk > 50 ? "+High" : "Moderate"}
          deltaColor={kpis.avg_fleet_risk > 50 ? "red" : "amber"}
        />
        <StatCard
          title="Critical Alerts (24h)"
          value={kpis.critical_alerts_24h}
          subtitle="High lethality zones alerted"
          icon={AlertTriangle}
          color="red"
          delta="-14%"
          deltaColor="emerald"
        />
        <StatCard
          title="Inference Latency"
          value={`${kpis.latency_ms} ms`}
          subtitle="Scikit-Learn ML Model evaluation"
          icon={Cpu}
          color="emerald"
          delta="O(1) H3 Index"
          deltaColor="emerald"
        />
      </div>

      {/* Middle Section: Fleet Risk Trends & National Risk Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Telemetry Trend Chart */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-white">Fleet Dynamic Risk Trend</h2>
              <p className="text-xs text-slate-400">Weather-induced risk escalation across tracked routes</p>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
              Live Feed
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={telemetryTrend}>
                <defs>
                  <linearGradient id="riskGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0}/>
                  </linearGradient>
                  <linearGradient id="maxRiskGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="avgRisk" stroke="#3b82f6" strokeWidth={2.5} fillOpacity={1} fill="url(#riskGrad)" name="Average Fleet Risk" />
                <Area type="monotone" dataKey="maxRisk" stroke="#ef4444" strokeWidth={2} fillOpacity={1} fill="url(#maxRiskGrad)" name="Peak Zone Risk" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* National Risk Distribution Bar Chart */}
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-xl flex flex-col justify-between">
          <div>
            <h2 className="text-base font-bold text-white mb-1">National Risk Tiers</h2>
            <p className="text-xs text-slate-400 mb-4">89,726 H3 Zones in Database</p>

            <div className="space-y-3">
              {riskDistribution.map((item) => (
                <div key={item.level} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-300 font-medium">{item.level}</span>
                    <span className="text-white font-bold">{item.count.toLocaleString()}</span>
                  </div>
                  <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div 
                      className="h-full rounded-full"
                      style={{ 
                        width: `${Math.max(5, (item.count / 75108) * 100)}%`,
                        backgroundColor: item.fill 
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 pt-4 border-t border-slate-800/80 text-xs text-slate-400 flex items-center justify-between">
            <span>Spatial Model: Uber H3 Res 8</span>
            <span className="font-semibold text-emerald-400">Indexed & Ready</span>
          </div>
        </div>
      </div>

      {/* Bottom Section: Real-time Alerts Feed */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <ShieldAlert className="w-5 h-5 text-red-400" />
            <h2 className="text-base font-bold text-white">Live ADAS Hazard Alert Stream</h2>
          </div>
          <span className="text-xs text-slate-400">Auto-updating telemetry stream</span>
        </div>

        <div className="divide-y divide-slate-800/80 max-h-72 overflow-y-auto">
          {alerts.length === 0 ? (
            <div className="py-6 text-center text-sm text-slate-400">No active critical alerts. All corridors operating safely.</div>
          ) : (
            alerts.map((alt, idx) => {
              const isCrit = alt.type === 'CRITICAL' || alt.type === 'FATAL';
              const isHigh = alt.type === 'HIGH';
              return (
                <div key={idx} className="py-3.5 flex items-start justify-between gap-4 transition-colors hover:bg-slate-800/30 px-2 rounded-lg">
                  <div className="flex items-start space-x-3">
                    <span className={`px-2.5 py-1 rounded-md text-[10px] font-black uppercase mt-0.5 tracking-wider ${
                      isCrit 
                        ? 'bg-red-500/20 text-red-400 border border-red-500/30' 
                        : isHigh 
                        ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30'
                        : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                    }`}>
                      {alt.type || 'ALERT'}
                    </span>
                    <div>
                      <p className="text-sm font-semibold text-slate-200">
                        {alt.message}
                      </p>
                      <p className="text-xs text-slate-400 mt-0.5">
                        {alt.vehicle_id ? `Vehicle: ${alt.vehicle_id} • ` : ''}
                        Risk Severity Score: <span className="font-bold text-white">{alt.risk_score || 'N/A'}</span>
                      </p>
                    </div>
                  </div>
                  <span className="text-xs text-slate-400 whitespace-nowrap flex items-center space-x-1">
                    <Clock className="w-3 h-3 text-slate-400" />
                    <span>{alt.time || 'Recent'}</span>
                  </span>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
