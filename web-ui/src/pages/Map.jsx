import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Polyline, Polygon, Popup, useMap, Marker, useMapEvents } from 'react-leaflet';
import axios from 'axios';

function ChangeView({ bounds }) {
  const map = useMap();
  useEffect(() => {
    if (bounds) map.fitBounds(bounds, { padding: [50, 50] });
  }, [bounds, map]);
  return null;
}

function MapInteraction({ origin, setOrigin, dest, setDest }) {
  useMapEvents({
    click(e) {
      if (!origin) {
        setOrigin({ lat: e.latlng.lat, lon: e.latlng.lng });
      } else if (!dest) {
        setDest({ lat: e.latlng.lat, lon: e.latlng.lng });
      } else {
        // Reset and start over
        setOrigin({ lat: e.latlng.lat, lon: e.latlng.lng });
        setDest(null);
      }
    },
  });
  return null;
}

export default function MapPage() {
  const [route, setRoute] = useState(null);
  const [loading, setLoading] = useState(false);
  const [weather, setWeather] = useState('Clear');
  const [time, setTime] = useState('Day');

  // Interactive markers
  const [origin, setOrigin] = useState(null);
  const [dest, setDest] = useState(null);
  
  const PRESET_ROUTES = [
    { name: "Custom Route (Map Clicks)", origin: null, dest: null },
    { name: "Paris to Lyon", origin: { lat: 48.8566, lon: 2.3522 }, dest: { lat: 45.7640, lon: 4.8357 } },
    { name: "Marseille to Nice", origin: { lat: 43.2965, lon: 5.3698 }, dest: { lat: 43.7102, lon: 7.2620 } },
    { name: "Bordeaux to Toulouse", origin: { lat: 44.8378, lon: -0.5792 }, dest: { lat: 43.6047, lon: 1.4442 } },
    { name: "Lille to Paris", origin: { lat: 50.6292, lon: 3.0573 }, dest: { lat: 48.8566, lon: 2.3522 } }
  ];
  
  const handlePresetChange = (e) => {
    const idx = parseInt(e.target.value);
    const preset = PRESET_ROUTES[idx];
    setOrigin(preset.origin);
    setDest(preset.dest);
  };

  const analyzeRoute = async () => {
    if (!origin || !dest) return;
    setLoading(true);
    try {
      const res = await axios.post('http://localhost:8000/api/analyze-route', {
        origin_lat: origin.lat, origin_lon: origin.lon,
        dest_lat: dest.lat, dest_lon: dest.lon,
        weather, time_of_day: time
      });
      setRoute(res.data);
    } catch (e) {
      console.error(e);
      alert('Error fetching route. Is the backend running?');
    }
    setLoading(false);
  };

  const getBounds = () => {
    if (!route) return null;
    return [[origin.lat, origin.lon], [dest.lat, dest.lon]];
  };

  return (
    <div className="h-full flex flex-col gap-6">
      <header className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-extrabold text-gradient mb-2">Live Map Simulation</h1>
          <p className="text-gray-400">
            {!origin ? "📍 Click anywhere on the map to set the START point." : 
             !dest ? "📍 Click again to set the DESTINATION point." : 
             "✅ Route ready to scan!"}
          </p>
        </div>
        
        <div className="flex gap-4 bg-[#1a1d2d] p-4 rounded-xl border border-[#2d324d] flex-wrap">
          <div>
            <label className="block text-xs text-gray-400 mb-1">Preset Route</label>
            <select onChange={handlePresetChange} className="bg-[#0f111a] border border-[#2d324d] rounded p-2 text-white">
              {PRESET_ROUTES.map((route, i) => (
                <option key={i} value={i}>{route.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Weather</label>
            <select value={weather} onChange={e => setWeather(e.target.value)} className="bg-[#0f111a] border border-[#2d324d] rounded p-2 text-white">
              <option>Clear</option><option>Rain</option><option>Fog</option><option>Snow</option>
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Time of Day</label>
            <select value={time} onChange={e => setTime(e.target.value)} className="bg-[#0f111a] border border-[#2d324d] rounded p-2 text-white">
              <option>Day</option><option>Night</option>
            </select>
          </div>
          <button 
            onClick={analyzeRoute}
            disabled={loading || !origin || !dest}
            className="self-end bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-lg transition-colors disabled:opacity-50"
          >
            {loading ? 'Analyzing...' : 'Scan Route'}
          </button>
        </div>
      </header>

      <div className="flex-1 rounded-xl overflow-hidden border border-[#2d324d] shadow-2xl relative">
        <MapContainer center={[46.2276, 2.2137]} zoom={6} style={{ height: '100%', width: '100%' }} zoomControl={false}>
          <TileLayer
            attribution='&copy; CARTO'
            url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
          />
          
          <MapInteraction origin={origin} setOrigin={setOrigin} dest={dest} setDest={setDest} />
          
          {origin && <Marker position={[origin.lat, origin.lon]}><Popup>Start</Popup></Marker>}
          {dest && <Marker position={[dest.lat, dest.lon]}><Popup>Destination</Popup></Marker>}
          
          {route && <ChangeView bounds={getBounds()} />}
          
          {/* Route Line */}
          {route && (
            <Polyline 
              positions={route.geometry.map(p => [p[1], p[0]])} 
              color="#3B82F6" 
              weight={5} 
              opacity={0.7} 
            />
          )}

          {/* Risk Zones */}
          {route && route.analysis && Object.entries(route.analysis.dynamic_zones).map(([zoneId, zoneData]) => {
            if (!zoneData.polygon) return null;
            return (
              <Polygon 
                key={zoneId}
                positions={zoneData.polygon}
                pathOptions={{
                  fillColor: zoneData.color,
                  fillOpacity: 0.5,
                  color: zoneData.color,
                  weight: 2
                }}
              >
                <Popup>
                  <div className="font-sans">
                    <strong>{zoneData.level} RISK</strong><br/>
                    Score: {zoneData.score.toFixed(1)}
                  </div>
                </Popup>
              </Polygon>
            );
          })}
        </MapContainer>
        
        {/* Overlay Metrics & Legend */}
        {route && (
          <div className="absolute top-6 right-6 z-[1000] glass-card !p-4 min-w-[200px]">
            <h4 className="font-bold text-white mb-2">Trip Report</h4>
            <div className="flex justify-between mb-1 text-sm">
              <span className="text-gray-400">AI Safety Score</span>
              <span className={`font-bold ${route.analysis.safety_score > 80 ? 'text-green-400' : 'text-red-400'}`}>
                {route.analysis.safety_score} / 100
              </span>
            </div>
            <div className="flex justify-between mb-3 text-sm border-b border-gray-700 pb-2">
              <span className="text-gray-400">Critical Zones</span>
              <span className="font-bold text-white">{route.analysis.critical_zones}</span>
            </div>
            
            <h4 className="font-bold text-white mb-2 text-sm uppercase tracking-wide">Risk Legend</h4>
            <div className="flex items-center gap-2 mb-1 text-sm">
              <div className="w-4 h-4 rounded-full bg-[#FF0000] shadow-[0_0_10px_#FF0000]"></div>
              <span className="text-gray-300">FATAL</span>
            </div>
            <div className="flex items-center gap-2 mb-1 text-sm">
              <div className="w-4 h-4 rounded-full border border-gray-600 bg-[#000000] shadow-[0_0_8px_#000000]"></div>
              <span className="text-gray-300">CRITICAL</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <div className="w-4 h-4 rounded-full bg-[#FFFF00] shadow-[0_0_8px_#FFFF00]"></div>
              <span className="text-gray-300">HIGH</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
