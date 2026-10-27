import React, { useState, useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { 
  MapPin, 
  ShieldAlert, 
  Filter, 
  Search, 
  Layers, 
  Database,
  Navigation
} from 'lucide-react';
import { api } from '../services/api';

export default function FranceRiskMap() {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const layerGroupRef = useRef(null);

  const [zones, setZones] = useState([]);
  const [selectedFilter, setSelectedFilter] = useState('ALL'); // ALL, FATAL, CRITICAL, HIGH
  const [loading, setLoading] = useState(true);

  // Metro Centers for quick jump
  const metros = [
    { name: 'France (All)', coords: [46.2276, 2.2137], zoom: 6 },
    { name: 'Paris', coords: [48.8566, 2.3522], zoom: 11 },
    { name: 'Lyon', coords: [45.7640, 4.8357], zoom: 12 },
    { name: 'Marseille', coords: [43.2965, 5.3698], zoom: 12 },
    { name: 'Bordeaux', coords: [44.8378, -0.5792], zoom: 12 },
    { name: 'Lille', coords: [50.6292, 3.0573], zoom: 12 },
  ];

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        zoomControl: true,
      }).setView([46.2276, 2.2137], 6);

      // OpenStreetMap basemap tiles (Free, zero API key)
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(map);

      mapInstanceRef.current = map;
      layerGroupRef.current = L.layerGroup().addTo(map);
    }

    // Fetch national zones
    setLoading(true);
    api.getNationalZones(2000)
      .then(res => {
        if (res?.zones) {
          setZones(res.zones);
        }
        setLoading(false);
      })
      .catch(() => setLoading(false));

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Filter and Draw Polygons
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !layerGroupRef.current) return;

    layerGroupRef.current.clearLayers();

    const filteredZones = zones.filter((z) => {
      const score = z.score || 0;
      if (selectedFilter === 'FATAL') return score >= 80;
      if (selectedFilter === 'CRITICAL') return score >= 45 && score < 80;
      if (selectedFilter === 'HIGH') return score < 45;
      return true;
    });

    filteredZones.forEach((z) => {
      const score = z.score || 0;
      let strokeColor, fillColor, fillOpacity, tierLabel;

      if (score >= 80) {
        strokeColor = '#b91c1c';
        fillColor = '#dc2626';
        fillOpacity = 0.75;
        tierLabel = '80+ SEVERE (RED)';
      } else if (score >= 45) {
        strokeColor = '#52525b';
        fillColor = '#000000';
        fillOpacity = 0.8;
        tierLabel = 'MEDIUM RISK (BLACK)';
      } else {
        strokeColor = '#c2410c';
        fillColor = '#f97316';
        fillOpacity = 0.65;
        tierLabel = 'LEAST RISK (ORANGE)';
      }

      const poly = L.polygon(z.polygon, {
        color: strokeColor,
        weight: 1.5,
        opacity: 0.95,
        fillColor: fillColor,
        fillOpacity: fillOpacity,
      });

      poly.bindTooltip(`
        <div style="font-family:sans-serif; font-size:12px; line-height:1.4;">
          <b style="color:${score >= 80 ? '#ef4444' : (score >= 45 ? '#e4e4e7' : '#fb923c')}">⚠️ ${tierLabel} HOTSPOT</b><br/>
          <b>H3 Cell ID:</b> <span style="font-family:monospace">${z.h3_index}</span><br/>
          <b>Historical Severity Score:</b> ${score.toFixed(1)} / 100<br/>
          <b>Location:</b> ${z.centroid[0].toFixed(4)}, ${z.centroid[1].toFixed(4)}
        </div>
      `, { className: 'custom-tooltip', sticky: true });

      layerGroupRef.current.addLayer(poly);
    });
  }, [zones, selectedFilter]);

  const jumpToMetro = (m) => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.setView(m.coords, m.zoom);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-indigo-950/40 border border-slate-800 shadow-xl">
        <div>
          <div className="flex items-center space-x-2 text-blue-400 text-xs font-bold uppercase tracking-wider mb-1">
            <MapPin className="w-4 h-4" />
            <span>89,726 Historical Crash Zones Indexed</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            National French Road Risk Map
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-xl">
            Exhaustive geospatial indexing of 11 years of French collision records across metropolitan and rural highway arteries.
          </p>
        </div>

        {/* Metro Fast Jump buttons */}
        <div className="flex flex-wrap items-center gap-1.5 bg-slate-950 p-1.5 rounded-xl border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 px-2">Jump To:</span>
          {metros.map((m) => (
            <button
              key={m.name}
              onClick={() => jumpToMetro(m)}
              className="px-2.5 py-1 rounded-lg text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800 transition-all"
            >
              {m.name}
            </button>
          ))}
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-blue-400" />
          <span className="text-xs font-semibold text-slate-300">Severity Tier Filter:</span>
          <div className="flex space-x-1.5">
            {[
              { id: 'ALL', label: 'All Loaded Tiers' },
              { id: 'FATAL', label: '🔴 80+ Severe (Red)' },
              { id: 'CRITICAL', label: '⬛ Medium (Black)' },
              { id: 'HIGH', label: '🟧 Least (Orange)' },
            ].map((f) => (
              <button
                key={f.id}
                onClick={() => setSelectedFilter(f.id)}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                  selectedFilter === f.id
                    ? 'bg-blue-600 text-white font-semibold shadow-sm'
                    : 'bg-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>

        <div className="text-xs text-slate-400">
          <span>Active Polygons: </span>
          <span className="font-bold text-white">{zones.length} Loaded</span>
        </div>
      </div>

      {/* Full-width Map Container */}
      <div className="relative w-full h-[650px] rounded-2xl overflow-hidden border border-slate-800 shadow-2xl bg-slate-950">
        <div ref={mapContainerRef} className="w-full h-full" />

        {loading && (
          <div className="absolute inset-0 bg-slate-950/70 backdrop-blur-sm z-[500] flex flex-col items-center justify-center space-y-3">
            <div className="w-8 h-8 border-3 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-sm font-semibold text-slate-200">Querying 89,726 H3 Zones from SQLite...</p>
          </div>
        )}
      </div>
    </div>
  );
}
