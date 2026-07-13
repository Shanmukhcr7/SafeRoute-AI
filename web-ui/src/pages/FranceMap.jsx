import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Polygon, Popup } from 'react-leaflet';
import axios from 'axios';

export default function FranceMap() {
  const [zones, setZones] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('http://localhost:8000/api/france-risk-map')
      .then(res => {
        setZones(res.data.zones);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="h-full flex flex-col gap-6">
      <header className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-extrabold text-gradient mb-2">France Risk Map</h1>
          <p className="text-gray-400">Global Country-Wide Heatmap of the Top 300 Most Dangerous Intersections</p>
        </div>
      </header>

      <div className="flex-1 rounded-xl overflow-hidden border border-[#2d324d] shadow-2xl relative">
        {loading && (
          <div className="absolute inset-0 z-[2000] bg-[#0f111a]/80 flex items-center justify-center text-xl text-blue-400 font-bold backdrop-blur-sm">
            Loading Country Map...
          </div>
        )}
        
        <MapContainer center={[46.2276, 2.2137]} zoom={6} style={{ height: '100%', width: '100%' }} zoomControl={false}>
          <TileLayer
            attribution='&copy; CARTO'
            url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
          />
          
          {zones.map((zone) => (
            <Polygon 
              key={zone.zone_id}
              positions={zone.polygon}
              pathOptions={{
                fillColor: zone.color,
                fillOpacity: 0.7,
                color: zone.color,
                weight: 1
              }}
            >
              <Popup>
                <div className="font-sans">
                  <strong>{zone.level} RISK</strong><br/>
                  Score: {zone.score.toFixed(1)}
                </div>
              </Popup>
            </Polygon>
          ))}
        </MapContainer>
        
        {/* Overlay Metrics */}
        <div className="absolute bottom-6 right-6 z-[1000] glass-card !p-4 min-w-[200px]">
          <h4 className="font-bold text-white mb-2">Data Source</h4>
          <div className="flex justify-between mb-1 text-sm">
            <span className="text-gray-400">Total Records</span>
            <span className="font-bold text-blue-400">220,573</span>
          </div>
          <div className="flex justify-between mb-3 text-sm border-b border-gray-700 pb-2">
            <span className="text-gray-400">Displayed Hotspots</span>
            <span className="font-bold text-red-400">{zones.length}</span>
          </div>
          
          <h4 className="font-bold text-white mb-2 text-sm uppercase tracking-wide">Risk Legend</h4>
          <div className="flex items-center gap-2 mb-1 text-sm">
            <div className="w-4 h-4 rounded-full bg-[#FF0000] shadow-[0_0_10px_#FF0000]"></div>
            <span className="text-gray-300">FATAL (<span className="text-gray-500">{'>'}40 crashes</span>)</span>
          </div>
          <div className="flex items-center gap-2 mb-1 text-sm">
            <div className="w-4 h-4 rounded-full border border-gray-600 bg-[#000000] shadow-[0_0_8px_#000000]"></div>
            <span className="text-gray-300">CRITICAL (<span className="text-gray-500">20-40</span>)</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <div className="w-4 h-4 rounded-full bg-[#FFFF00] shadow-[0_0_8px_#FFFF00]"></div>
            <span className="text-gray-300">HIGH (<span className="text-gray-500">10-20</span>)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
