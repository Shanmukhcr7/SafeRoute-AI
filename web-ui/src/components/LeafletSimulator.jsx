import React, { useEffect, useRef, useState } from 'react';
import * as turf from '@turf/turf';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  Eye, 
  Crosshair, 
  AlertTriangle, 
  Gauge, 
  ShieldAlert,
  Settings
} from 'lucide-react';

export default function LeafletSimulator({ 
  geometry = [], 
  hotspots = [], 
  environment = { weather: 'Clear', time_of_day: 'Day' },
  initialSpeed = 130,
  autoStart = true,
  onAlert = null,
  onReconfigure = null
}) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const carMarkerRef = useRef(null);
  const pathLayerRef = useRef(null);
  const zonesLayerGroupRef = useRef(null);

  const [isPlaying, setIsPlaying] = useState(autoStart);
  const [speedKmh, setSpeedKmh] = useState(initialSpeed);
  const [progressKm, setProgressKm] = useState(0);
  const [totalKm, setTotalKm] = useState(0);
  const [followCar, setFollowCar] = useState(false);
  const [activeAlert, setActiveAlert] = useState(null);
  const [tierFilter, setTierFilter] = useState('ALL'); // 'ALL' | 'RED' | 'BLACK' | 'ORANGE'

  // Sync external speed changes
  useEffect(() => {
    if (initialSpeed) {
      setSpeedKmh(initialSpeed);
      speedRef.current = initialSpeed;
      currentLiveSpeedRef.current = initialSpeed;
    }
  }, [initialSpeed]);

  // References for animation loop to avoid re-renders
  const animFrameRef = useRef(null);
  const lastTimeRef = useRef(null);
  const currentDistRef = useRef(0);
  const isPlayingRef = useRef(isPlaying);
  const speedRef = useRef(speedKmh);
  const currentLiveSpeedRef = useRef(speedKmh);
  const followCarRef = useRef(followCar);
  const activeAlertIdRef = useRef(null);
  const lastProgressUpdateRef = useRef(0);

  isPlayingRef.current = isPlaying;
  speedRef.current = speedKmh;
  followCarRef.current = followCar;

  // Single consolidated Map & Simulation Lifecycle
  useEffect(() => {
    if (!mapContainerRef.current) return;
    if (!geometry || geometry.length < 2) return;

    // Reset distance & alert
    currentDistRef.current = 0;
    setProgressKm(0);
    setActiveAlert(null);
    activeAlertIdRef.current = null;

    // 1. Initialize Leaflet Map safely (guards against React StrictMode re-initialization)
    let map = mapInstanceRef.current;
    if (!map) {
      if (mapContainerRef.current._leaflet_id) {
        delete mapContainerRef.current._leaflet_id;
      }

      const defaultCenter = [geometry[0][1], geometry[0][0]];
      map = L.map(mapContainerRef.current, {
        zoomControl: true,
        attributionControl: true,
      }).setView(defaultCenter, 10);

      // Free, open OpenStreetMap tiles (no API keys, no watermarks)
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(map);

      mapInstanceRef.current = map;
      zonesLayerGroupRef.current = L.layerGroup().addTo(map);
    }

    // Force map to compute dimensions accurately
    setTimeout(() => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.invalidateSize();
      }
    }, 150);

    // 2. Draw Route Polyline
    if (pathLayerRef.current && map.hasLayer(pathLayerRef.current)) {
      map.removeLayer(pathLayerRef.current);
    }

    const latlngs = geometry.map(p => [p[1], p[0]]);
    const path = L.polyline(latlngs, {
      color: '#00aaff',
      weight: 4.5,
      opacity: 0.85,
    }).addTo(map);
    pathLayerRef.current = path;

    // Calculate total route distance with turf
    const routeLine = turf.lineString(geometry);
    const totalDist = turf.length(routeLine, { units: 'kilometers' });
    setTotalKm(totalDist);

    // Fit map to full route corridor initially
    map.fitBounds(path.getBounds().pad(0.08));

    // 3. Draw Hotspots Layer
    if (zonesLayerGroupRef.current) {
      zonesLayerGroupRef.current.clearLayers();
    }

    const processedTurfZones = [];

    hotspots.forEach((zone) => {
      const score = zone.score || 0;
      let strokeColor, fillColor, fillOpacity, badgeClass, tierLabel, badgeIconSymbol;

      // Color logic: Red for 80+, Black for medium (45-79), Orange for least (<45)
      if (score >= 80) {
        strokeColor = '#b91c1c';
        fillColor = '#dc2626';
        fillOpacity = 0.8;
        badgeClass = 'score-red';
        tierLabel = '80+ SEVERE (RED)';
        badgeIconSymbol = '⚠️';
      } else if (score >= 45) {
        strokeColor = '#52525b';
        fillColor = '#000000';
        fillOpacity = 0.85;
        badgeClass = 'score-black';
        tierLabel = 'MEDIUM RISK (BLACK)';
        badgeIconSymbol = '⬛';
      } else {
        strokeColor = '#ea580c';
        fillColor = '#f97316';
        fillOpacity = 0.75;
        badgeClass = 'score-orange';
        tierLabel = 'LEAST RISK (ORANGE)';
        badgeIconSymbol = '🟧';
      }

      // Filter layer based on active tierFilter selection
      const isVisible = tierFilter === 'ALL' ||
        (tierFilter === 'RED' && score >= 80) ||
        (tierFilter === 'BLACK' && score >= 45 && score < 80) ||
        (tierFilter === 'ORANGE' && score < 45);

      if (isVisible && zone.polygon && zone.polygon.length >= 3) {
        const poly = L.polygon(zone.polygon, {
          color: strokeColor,
          weight: score < 45 ? 3.5 : 2.5,
          opacity: 0.95,
          fillColor: fillColor,
          fillOpacity: fillOpacity,
        });

        const tooltipContent = `
          <div style="font-family:sans-serif; font-size:12px; line-height:1.4;">
            <b style="color:${score >= 80 ? '#ef4444' : (score >= 45 ? '#e4e4e7' : '#fb923c')}">${badgeIconSymbol} ${tierLabel} HOTSPOT</b><br/>
            <b>Dynamic AI Risk:</b> ${score.toFixed(1)} / 100<br/>
            <b>Base Historical Risk:</b> ${(zone.base_score || score).toFixed(1)}<br/>
            <b>Weather Multiplier:</b> ${(zone.multiplier || 1.0).toFixed(2)}x<br/>
            <b>Status:</b> ${score >= 80 ? 'Severe Lethality Zone' : (score >= 45 ? 'Medium Risk Cluster' : 'Least Risk Highway Stretch')}
          </div>
        `;
        poly.bindTooltip(tooltipContent, { className: 'custom-tooltip', sticky: true });
        zonesLayerGroupRef.current.addLayer(poly);

        // Centroid Badge
        if (zone.centroid) {
          const badgeIcon = L.divIcon({
            html: `<div class="hotspot-badge ${badgeClass}" title="${tierLabel} Hotspot (${score.toFixed(1)})">${badgeIconSymbol}</div>`,
            className: '',
            iconSize: [24, 24],
            iconAnchor: [12, 12],
          });
          const marker = L.marker(zone.centroid, { icon: badgeIcon });
          marker.bindTooltip(tooltipContent, { className: 'custom-tooltip' });
          zonesLayerGroupRef.current.addLayer(marker);
        }
      }

      // Prepare turf polygon for collision detection (all zones)
      try {
        const ring = zone.polygon.map(p => [p[1], p[0]]); // [lon, lat]
        ring.push([ring[0][0], ring[0][1]]); // close ring
        if (ring.length >= 4) {
          processedTurfZones.push({
            turfPoly: turf.polygon([ring]),
            data: zone,
          });
        }
      } catch (e) {
        // ignore invalid ring
      }
    });

    // 4. Vehicle Marker Setup with Live Speed HUD & Attached Alert Popup
    if (carMarkerRef.current && map.hasLayer(carMarkerRef.current)) {
      map.removeLayer(carMarkerRef.current);
    }

    const carIconHtml = `
      <div class="car-marker-hud-wrapper" style="width: 260px; height: 95px; margin-left: -130px; margin-top: -68px;">
        <!-- Alert Popup Bubble (Anchored right above the car!) -->
        <div id="car-alert-bubble" class="car-alert-bubble hidden">
          <span>⚠️</span>
          <span id="car-alert-text">ALERT 500m AHEAD</span>
        </div>

        <!-- Live Speed Badge (Directly on the car!) -->
        <div id="car-speed-badge" class="car-speed-pill">
          <span>⚡</span>
          <span id="car-speed-val">${Math.round(currentLiveSpeedRef.current)}</span>
          <span style="font-size: 8px; opacity: 0.85;">km/h</span>
        </div>

        <!-- Vehicle Body with Heading Rotation & Hazard Halo -->
        <div id="car-inner" style="transition: transform 0.1s linear; position: relative;">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M7 6L9 2H15L17 6V18L15 22H9L7 18V6Z" fill="#ef4444" stroke="#ffffff" stroke-width="2"/>
            <path d="M8 8H16V12H8V8Z" fill="#1e293b"/>
            <circle cx="10" cy="4" r="1.2" fill="#38bdf8"/>
            <circle cx="14" cy="4" r="1.2" fill="#38bdf8"/>
          </svg>
          <div id="car-hazard-halo" class="car-hazard-halo hidden"></div>
        </div>
      </div>
    `;

    const carIcon = L.divIcon({
      html: carIconHtml,
      className: '',
      iconSize: [0, 0],
      iconAnchor: [0, 0],
    });

    const startCoord = [geometry[0][1], geometry[0][0]];
    const carMarker = L.marker(startCoord, { icon: carIcon, zIndexOffset: 1000 }).addTo(map);
    carMarkerRef.current = carMarker;

    // Auto-engage tracking after 2.5 seconds of corridor overview
    const autoFollowTimeout = setTimeout(() => {
      setFollowCar(true);
    }, 2500);

    // 5. Animation Loop
    lastTimeRef.current = null;

    function animate(timestamp) {
      if (!lastTimeRef.current) lastTimeRef.current = timestamp;
      const deltaTime = (timestamp - lastTimeRef.current) / 1000;
      lastTimeRef.current = timestamp;

      if (isPlayingRef.current) {
        try {
          const safeDist = Math.max(0, Math.min(currentDistRef.current, Math.max(0.001, totalDist - 0.001)));
          const currentPt = turf.along(routeLine, safeDist, { units: 'kilometers' }).geometry.coordinates;
          const lat = currentPt[1];
          const lon = currentPt[0];

          // 500m Lookahead Collision Detection
          const checkDistance = Math.min(currentDistRef.current + 0.5, totalDist);
          const lookaheadPt = turf.along(routeLine, checkDistance, { units: 'kilometers' }).geometry.coordinates;
          const lookaheadPoint = turf.point(lookaheadPt);

          // Fast Bounding Box pre-check before expensive Turf polygon test
          let hit = null;
          for (let i = 0; i < processedTurfZones.length; i++) {
            const z = processedTurfZones[i].data;
            if (z.centroid) {
              const dLat = Math.abs(z.centroid[0] - lookaheadPt[1]);
              const dLon = Math.abs(z.centroid[1] - lookaheadPt[0]);
              if (dLat > 0.015 || dLon > 0.02) {
                continue; // Skip polygon check if further than ~1.5km
              }
            }

            if (turf.booleanPointInPolygon(lookaheadPoint, processedTurfZones[i].turfPoly)) {
              hit = z;
              break;
            }
          }

          // ADAS Target Speed: Automatically decelerate when hazard approaches
          let targetSpeed = speedRef.current;
          if (hit) {
            if (hit.level === 'FATAL') targetSpeed = 35;
            else if (hit.level === 'CRITICAL') targetSpeed = 50;
            else if (hit.level === 'HIGH') targetSpeed = 75;
            else targetSpeed = 95;
            targetSpeed = Math.min(targetSpeed, speedRef.current);
          }

          // Smooth realistic emergency deceleration & re-acceleration
          if (currentLiveSpeedRef.current > targetSpeed) {
            currentLiveSpeedRef.current = Math.max(targetSpeed, currentLiveSpeedRef.current - 75 * deltaTime);
          } else if (currentLiveSpeedRef.current < targetSpeed) {
            currentLiveSpeedRef.current = Math.min(targetSpeed, currentLiveSpeedRef.current + 45 * deltaTime);
          }

          // Advance distance using dynamic live speed
          currentDistRef.current += (currentLiveSpeedRef.current / 3600) * deltaTime;

          if (currentDistRef.current >= totalDist) {
            currentDistRef.current = totalDist;
            setIsPlaying(false);
            setProgressKm(totalDist);
          } else {
            // Throttle progress state updates to ~8fps to eliminate React re-render churn
            if (!lastProgressUpdateRef.current || (timestamp - lastProgressUpdateRef.current) > 120) {
              lastProgressUpdateRef.current = timestamp;
              setProgressKm(currentDistRef.current);
            }
          }

          // 1. Update Live Speed Display directly on the car marker
          const speedValElem = document.getElementById('car-speed-val');
          if (speedValElem) {
            speedValElem.innerText = Math.round(currentLiveSpeedRef.current);
          }

          // 2. Update Alert Pop-up directly on the car marker
          const alertBubble = document.getElementById('car-alert-bubble');
          const alertText = document.getElementById('car-alert-text');
          const hazardHalo = document.getElementById('car-hazard-halo');
          const speedPill = document.getElementById('car-speed-badge');

          if (hit) {
            const hScore = hit.score || 0;
            const hitClass = hScore >= 80 ? 'score-80-red' : (hScore >= 45 ? 'score-medium-black' : 'score-least-orange');
            const tierTitle = hScore >= 80 ? '80+ SEVERE' : (hScore >= 45 ? 'MEDIUM RISK' : 'LEAST RISK');
            if (alertBubble) {
              alertBubble.className = `car-alert-bubble ${hitClass}`;
              alertBubble.classList.remove('hidden');
            }
            if (alertText) {
              alertText.innerText = `⚠️ ${tierTitle}: ${Math.round(currentLiveSpeedRef.current)} km/h`;
            }
            if (hazardHalo) hazardHalo.classList.remove('hidden');
            if (speedPill) speedPill.classList.add('alert-active');
          } else {
            if (alertBubble) alertBubble.classList.add('hidden');
            if (hazardHalo) hazardHalo.classList.add('hidden');
            if (speedPill) speedPill.classList.remove('alert-active');
          }

          // Rotate car heading
          if (currentDistRef.current + 0.08 < totalDist) {
            const nextPt = turf.along(routeLine, currentDistRef.current + 0.08, { units: 'kilometers' }).geometry.coordinates;
            const bearing = turf.bearing(turf.point(currentPt), turf.point(nextPt));
            const carElem = document.getElementById('car-inner');
            if (carElem) {
              carElem.style.transform = `rotate(${bearing}deg)`;
            }
          }

          carMarker.setLatLng([lat, lon]);

          if (followCarRef.current) {
            map.panTo([lat, lon], { animate: false });
          }

          // State update ONLY if alert state changed (avoids 60fps re-render freeze!)
          if (hit) {
            if (activeAlertIdRef.current !== hit.h3_index) {
              activeAlertIdRef.current = hit.h3_index;
              setActiveAlert(hit);
              if (onAlert) onAlert(hit);
            }
          } else {
            if (activeAlertIdRef.current !== null) {
              activeAlertIdRef.current = null;
              setActiveAlert(null);
            }
          }
        } catch (e) {
          // ignore interpolation safe catch
        }
      }

      animFrameRef.current = requestAnimationFrame(animate);
    }

    animFrameRef.current = requestAnimationFrame(animate);

    return () => {
      clearTimeout(autoFollowTimeout);
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    };
  }, [geometry, hotspots, tierFilter]);

  // Clean-up on unmount
  useEffect(() => {
    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
      if (mapContainerRef.current) {
        delete mapContainerRef.current._leaflet_id;
      }
    };
  }, []);

  const handleFitFullRoute = () => {
    setFollowCar(false);
    if (mapInstanceRef.current && pathLayerRef.current) {
      mapInstanceRef.current.fitBounds(pathLayerRef.current.getBounds().pad(0.08));
    }
  };

  const handleFollowCar = () => {
    setFollowCar(true);
    if (mapInstanceRef.current && carMarkerRef.current) {
      mapInstanceRef.current.setView(carMarkerRef.current.getLatLng(), 13);
    }
  };

  const handleReset = () => {
    currentDistRef.current = 0;
    setProgressKm(0);
    setIsPlaying(true);
    currentLiveSpeedRef.current = speedRef.current;
    activeAlertIdRef.current = null;
    setActiveAlert(null);
    const alertBubble = document.getElementById('car-alert-bubble');
    if (alertBubble) alertBubble.classList.add('hidden');
    const hazardHalo = document.getElementById('car-hazard-halo');
    if (hazardHalo) hazardHalo.classList.add('hidden');
    const speedPill = document.getElementById('car-speed-badge');
    if (speedPill) speedPill.classList.remove('alert-active');
    if (carMarkerRef.current && geometry.length > 0) {
      carMarkerRef.current.setLatLng([geometry[0][1], geometry[0][0]]);
    }
    handleFitFullRoute();
  };

  return (
    <div className="relative w-full h-[620px] rounded-2xl overflow-hidden border border-slate-800 shadow-2xl bg-slate-950">
      {/* Map Canvas */}
      <div ref={mapContainerRef} className="w-full h-full" />

      {/* Floating Top-Right HUD: Hotspot Counts & Legend */}
      <div className="absolute top-4 right-4 z-[400] bg-slate-900/90 backdrop-blur-md p-4 rounded-xl border border-slate-700/70 shadow-2xl text-xs max-w-xs">
        <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <ShieldAlert className="w-4 h-4 text-red-400" />
            <span className="font-bold text-white text-sm">AI Accident Hotspots</span>
          </div>
          <span className="px-2 py-0.5 rounded-full font-bold text-[11px] bg-red-500/20 text-red-400 border border-red-500/30">
            {hotspots.length} Detected
          </span>
        </div>

        <div className="space-y-1.5 text-slate-300">
          <button
            type="button"
            onClick={() => setTierFilter(tierFilter === 'RED' ? 'ALL' : 'RED')}
            className={`w-full flex items-center justify-between p-1.5 rounded-lg transition-all text-left cursor-pointer ${
              tierFilter === 'RED' ? 'bg-red-950/80 border border-red-500 shadow-md' : 'hover:bg-slate-800/60'
            }`}
            title="Click to isolate 80+ Red zones"
          >
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 rounded-full bg-red-600 ring-2 ring-red-600/40 shadow-sm"></span>
              <span className="font-semibold text-white">80+ Scored (Red)</span>
            </div>
            <span className="font-bold text-red-400 bg-red-950/60 px-2 py-0.5 rounded border border-red-800 text-[11px]">
              {hotspots.filter(h => (h.score || 0) >= 80).length}
            </span>
          </button>

          <button
            type="button"
            onClick={() => setTierFilter(tierFilter === 'BLACK' ? 'ALL' : 'BLACK')}
            className={`w-full flex items-center justify-between p-1.5 rounded-lg transition-all text-left cursor-pointer ${
              tierFilter === 'BLACK' ? 'bg-slate-800 border border-slate-500 shadow-md' : 'hover:bg-slate-800/60'
            }`}
            title="Click to isolate Medium Black zones"
          >
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 rounded-full bg-black border-2 border-slate-500 ring-2 ring-slate-800 shadow-sm"></span>
              <span className="font-semibold text-white">Medium Scored (Black)</span>
            </div>
            <span className="font-bold text-slate-200 bg-slate-950 px-2 py-0.5 rounded border border-slate-700 text-[11px]">
              {hotspots.filter(h => (h.score || 0) >= 45 && (h.score || 0) < 80).length}
            </span>
          </button>

          <button
            type="button"
            onClick={() => {
              const newFilter = tierFilter === 'ORANGE' ? 'ALL' : 'ORANGE';
              setTierFilter(newFilter);
              if (newFilter === 'ORANGE') {
                const firstOrange = hotspots.find(h => (h.score || 0) < 45);
                if (firstOrange?.centroid && mapInstanceRef.current) {
                  mapInstanceRef.current.setView(firstOrange.centroid, 11);
                }
              }
            }}
            className={`w-full flex items-center justify-between p-1.5 rounded-lg transition-all text-left cursor-pointer ${
              tierFilter === 'ORANGE' ? 'bg-orange-950/90 border border-orange-500 ring-1 ring-orange-500 shadow-md' : 'hover:bg-slate-800/60'
            }`}
            title="Click to view & focus Orange Least Risk spots"
          >
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 rounded-full bg-orange-500 ring-2 ring-orange-500/50 shadow-sm"></span>
              <span className="font-semibold text-white">Least Scored (Orange)</span>
            </div>
            <span className="font-bold text-orange-400 bg-orange-950/80 px-2 py-0.5 rounded border border-orange-700 text-[11px]">
              {hotspots.filter(h => (h.score || 0) < 45).length}
            </span>
          </button>
        </div>

        {tierFilter !== 'ALL' && (
          <div className="mt-2 pt-1 border-t border-slate-800 text-center">
            <button
              onClick={() => {
                setTierFilter('ALL');
                handleFitFullRoute();
              }}
              className="text-[11px] text-blue-400 hover:text-blue-300 font-bold cursor-pointer"
            >
              ← Reset to Show All Tiers
            </button>
          </div>
        )}

        <div className="mt-3 pt-2.5 border-t border-slate-800 flex gap-2">
          <button
            onClick={handleFitFullRoute}
            className={`flex-1 py-1.5 px-2 rounded-lg text-[11px] font-medium flex items-center justify-center space-x-1 transition-all ${
              !followCar ? 'bg-blue-600 text-white shadow-md' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            <Eye className="w-3.5 h-3.5" />
            <span>Full Route</span>
          </button>
          <button
            onClick={handleFollowCar}
            className={`flex-1 py-1.5 px-2 rounded-lg text-[11px] font-medium flex items-center justify-center space-x-1 transition-all ${
              followCar ? 'bg-blue-600 text-white shadow-md' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            <Crosshair className="w-3.5 h-3.5" />
            <span>Follow Car</span>
          </button>
        </div>
      </div>

      {/* Real-time ADAS Lookahead Warning Banner */}
      {activeAlert && (
        <div className="absolute top-4 left-1/2 -translate-x-1/2 z-[400] animate-bounce">
          <div className={`px-5 py-3 rounded-2xl shadow-2xl border flex items-center space-x-3 text-white ${
            activeAlert.level === 'FATAL' || activeAlert.level === 'CRITICAL'
              ? 'bg-red-600/95 border-red-400 shadow-red-500/40'
              : 'bg-orange-600/95 border-orange-400 shadow-orange-500/40'
          }`}>
            <AlertTriangle className="w-6 h-6 animate-pulse" />
            <div>
              <div className="text-xs font-black uppercase tracking-wider">
                ⚠️ ADAS Hazard Alert: 500m Ahead
              </div>
              <div className="text-sm font-extrabold">
                {activeAlert.level} Collision Hotspot — Risk Score: {(activeAlert.score || 0).toFixed(1)}/100
              </div>
              <div className="text-[11px] text-white/90">
                AI Advisory: Decelerate immediately to {activeAlert.level === 'FATAL' ? '30' : (activeAlert.level === 'CRITICAL' ? '50' : '70')} km/h
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Floating Bottom Navigation Controller */}
      <div className="absolute bottom-4 left-4 right-4 z-[400] bg-slate-900/90 backdrop-blur-md px-6 py-4 rounded-2xl border border-slate-800 shadow-2xl flex flex-wrap items-center justify-between gap-4">
        {/* Play / Pause / Reset */}
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center shadow-lg shadow-blue-600/30 hover:bg-blue-500 transition-all"
            title={isPlaying ? "Pause Simulation" : "Resume Simulation"}
          >
            {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-0.5" />}
          </button>
          <button
            onClick={handleReset}
            className="w-10 h-10 rounded-xl bg-slate-800 text-slate-300 flex items-center justify-center hover:bg-slate-700 hover:text-white transition-all border border-slate-700/60"
            title="Restart Journey"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          <div>
            <div className="text-xs font-semibold text-slate-400">Simulation Status</div>
            <div className="text-sm font-bold text-white flex items-center space-x-2">
              <span className={`w-2 h-2 rounded-full ${isPlaying ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`}></span>
              <span>{isPlaying ? 'Cruising (Live Tracking)' : 'Paused'}</span>
            </div>
          </div>
        </div>

        {/* Progress Timeline */}
        <div className="flex-1 min-w-[200px] max-w-md">
          <div className="flex justify-between text-xs text-slate-400 font-medium mb-1">
            <span>Trip Progress</span>
            <span className="text-white font-bold">{progressKm.toFixed(1)} / {totalKm.toFixed(1)} km</span>
          </div>
          <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden border border-slate-700/50">
            <div 
              className="bg-gradient-to-r from-blue-500 via-indigo-500 to-cyan-400 h-full rounded-full transition-all duration-100"
              style={{ width: `${totalKm > 0 ? (progressKm / totalKm) * 100 : 0}%` }}
            />
          </div>
        </div>

        {/* Speed Slider & Reconfigure */}
        <div className="flex items-center space-x-4 text-xs">
          <div className="flex items-center space-x-2">
            <Gauge className="w-4 h-4 text-blue-400" />
            <span className="text-slate-400 font-medium">Speed:</span>
            <span className="font-extrabold text-white text-sm min-w-[50px]">{speedKmh} km/h</span>
            <input
              type="range"
              min="30"
              max="300"
              step="10"
              value={speedKmh}
              onChange={(e) => setSpeedKmh(Number(e.target.value))}
              className="w-24 accent-blue-500 cursor-pointer"
            />
          </div>

          {onReconfigure && (
            <button
              onClick={onReconfigure}
              className="py-1.5 px-3 rounded-xl bg-slate-800 text-slate-200 hover:text-white hover:bg-slate-700 font-bold flex items-center space-x-1.5 border border-slate-700 transition-all shadow-sm"
              title="Return to Mission Configuration"
            >
              <Settings className="w-3.5 h-3.5 text-blue-400" />
              <span>Modify Setup</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
