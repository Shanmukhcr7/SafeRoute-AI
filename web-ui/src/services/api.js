import axios from 'axios';

const API_BASE = '/api';

const client = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Status & KPIs
  getStatus: () => client.get('/status').then(r => r.data),
  getKpis: () => client.get('/kpis').then(r => r.data),
  getAlerts: (limit = 20) => client.get(`/alerts?limit=${limit}`).then(r => r.data),

  // Routes & Analysis
  getRoutes: () => client.get('/routes').then(r => r.data),
  analyzeRoute: (routeName, weather, timeOfDay) =>
    client.post('/routes/analyze', {
      route_name: routeName,
      weather: weather,
      time_of_day: timeOfDay,
    }).then(r => r.data),
  compareRoutes: (weather, timeOfDay) =>
    client.post('/routes/compare', {
      weather: weather,
      time_of_day: timeOfDay,
    }).then(r => r.data),

  // AI Model & Registry
  getModelEvaluation: () => client.get('/model/evaluation').then(r => r.data),
  predictLive: (lat, lon, weather, timeOfDay) =>
    client.post('/predict', {
      lat,
      lon,
      weather,
      time_of_day: timeOfDay,
    }).then(r => r.data),

  // National Zones
  getNationalZones: (limit = 1500) =>
    client.get(`/zones/national?limit=${limit}`).then(r => r.data),

  // Telemetry Playback
  getTelemetry: () => client.get('/simulation/telemetry').then(r => r.data),
};
