import { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

export default function Analytics() {
  const [data, setData] = useState(null);

  useEffect(() => {
    axios.get('http://localhost:8000/api/analytics')
      .then(res => setData(res.data))
      .catch(err => console.error(err));
  }, []);

  if (!data) return <div className="p-8 text-xl animate-pulse">Loading AI Analytics...</div>;

  const { eval_data, meta_data } = data;

  // Format Feature Importance
  const featData = eval_data.feature_importance.map(f => ({
    name: f.feature,
    importance: f.importance * 100
  })).reverse();

  // Format ROC
  const rocData = eval_data.roc_fatal.fpr.map((f, i) => ({
    fpr: f,
    tpr: eval_data.roc_fatal.tpr[i]
  }));

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <header className="mb-8">
        <h1 className="text-4xl font-extrabold text-gradient mb-2">AI Analytics & Model Evaluation</h1>
        <p className="text-gray-400">Deep dive into the Machine Learning Engine's logic and performance metrics.</p>
      </header>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass-card p-6">
          <p className="text-sm text-gray-400 uppercase tracking-wider mb-1">Architecture</p>
          <p className="text-2xl font-bold text-white truncate">{meta_data.model_type}</p>
        </div>
        <div className="glass-card p-6">
          <p className="text-sm text-gray-400 uppercase tracking-wider mb-1">Training Records</p>
          <p className="text-2xl font-bold text-blue-400">{meta_data.dataset_size.toLocaleString()}</p>
        </div>
        <div className="glass-card p-6">
          <p className="text-sm text-gray-400 uppercase tracking-wider mb-1">Global Accuracy</p>
          <p className="text-2xl font-bold text-green-400">{(meta_data.accuracy * 100).toFixed(1)}%</p>
        </div>
        <div className="glass-card p-6">
          <p className="text-sm text-gray-400 uppercase tracking-wider mb-1">ROC-AUC Score</p>
          <p className="text-2xl font-bold text-purple-400">{eval_data.roc_fatal.auc.toFixed(3)}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Feature Importance */}
        <div className="glass-card p-6 flex flex-col">
          <h3 className="text-xl font-bold text-white mb-2">🔍 Global Feature Importance</h3>
          <p className="text-sm text-gray-400 mb-6">
            This graph reveals the inner workings of the AI's decision-making process. The longer the bar, the heavier the AI relies on that specific environmental factor (like Lighting or Road Surface) to predict a fatal crash. 
          </p>
          <div className="h-80 flex-1 min-h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={featData} layout="vertical" margin={{ left: 50 }}>
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" stroke="#94a3b8" />
                <Tooltip cursor={{fill: 'rgba(255,255,255,0.05)'}} contentStyle={{backgroundColor: '#1e2235', border: 'none', borderRadius: '8px'}} />
                <Bar dataKey="importance" fill="#8B5CF6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* ROC Curve */}
        <div className="glass-card p-6 flex flex-col">
          <h3 className="text-xl font-bold text-white mb-2">📈 ROC Curve (Fatal Prediction)</h3>
          <p className="text-sm text-gray-400 mb-6">
            The ROC (Receiver Operating Characteristic) curve measures the AI's ability to distinguish between Minor and Fatal accidents. An AUC (Area Under Curve) score of 1.0 is perfect. Anything above 0.8 is considered excellent for complex real-world data.
          </p>
          <div className="h-80 flex-1 min-h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={rocData} margin={{ left: -20, bottom: 0 }}>
                <XAxis dataKey="fpr" stroke="#94a3b8" tickFormatter={v => v.toFixed(2)} />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{backgroundColor: '#1e2235', border: 'none', borderRadius: '8px'}} />
                <Area type="monotone" dataKey="tpr" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.3} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
