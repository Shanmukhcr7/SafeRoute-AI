import React from 'react';

export default function StatCard({ title, value, subtitle, icon: Icon, color = 'blue', delta, deltaColor = 'emerald' }) {
  const colorMap = {
    blue: 'border-blue-500/20 bg-gradient-to-br from-blue-950/30 to-slate-900/60 text-blue-400',
    red: 'border-red-500/20 bg-gradient-to-br from-red-950/30 to-slate-900/60 text-red-400',
    amber: 'border-amber-500/20 bg-gradient-to-br from-amber-950/30 to-slate-900/60 text-amber-400',
    emerald: 'border-emerald-500/20 bg-gradient-to-br from-emerald-950/30 to-slate-900/60 text-emerald-400',
    purple: 'border-purple-500/20 bg-gradient-to-br from-purple-950/30 to-slate-900/60 text-purple-400',
  };

  const deltaColorMap = {
    emerald: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    red: 'text-red-400 bg-red-500/10 border-red-500/20',
    amber: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
    blue: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
  };

  return (
    <div className={`p-5 rounded-2xl border backdrop-blur-md shadow-lg transition-all duration-200 hover:scale-[1.01] ${colorMap[color] || colorMap.blue}`}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          {title}
        </span>
        {Icon && (
          <div className="p-2 rounded-xl bg-slate-800/80 border border-slate-700/50">
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      <div className="flex items-baseline justify-between">
        <div className="text-3xl font-extrabold text-white tracking-tight">
          {value}
        </div>
        {delta && (
          <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${deltaColorMap[deltaColor] || deltaColorMap.emerald}`}>
            {delta}
          </span>
        )}
      </div>

      {subtitle && (
        <p className="mt-2 text-xs text-slate-400 font-medium">
          {subtitle}
        </p>
      )}
    </div>
  );
}
