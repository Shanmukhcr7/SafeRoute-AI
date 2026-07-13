export default function Home() {
  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fade-in">
      <header className="mb-12">
        <h1 className="text-5xl font-extrabold text-gradient mb-4">AI Road Traffic Intelligence</h1>
        <p className="text-xl text-gray-400">Advanced Driver Assistance System (ADAS) Dashboard</p>
      </header>

      <section className="glass-card p-8">
        <h2 className="text-3xl font-bold mb-4 text-white">The Mission</h2>
        <p className="text-lg text-gray-300 leading-relaxed mb-4">
          This platform was engineered to proactively prevent road accidents by combining <b>authentic historical police data</b>, high-resolution <b>spatial grid systems</b>, and a powerful <b>Machine Learning risk engine</b>.
        </p>
        <p className="text-lg text-gray-300 leading-relaxed border-l-4 border-blue-500 pl-4 bg-blue-900/10 py-2">
          <b>Real-World Application:</b> By deploying this AI within a vehicle's GPS navigation system, we can warn drivers <i>miles in advance</i> that they are approaching an intersection known for fatal accidents specifically during their current weather conditions (e.g., Rain at Night).
        </p>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <section className="glass-card p-8">
          <h3 className="text-2xl font-bold mb-4 text-white">📊 The Dataset</h3>
          <p className="text-gray-300 mb-6 leading-relaxed">
            This AI was trained on a massive, authentic government dataset containing <b>over 15 years</b> of traffic accident history.
          </p>
          <ul className="space-y-4 text-gray-300">
            <li className="flex items-start gap-3">
              <span className="text-blue-400 font-bold">•</span>
              <span><strong className="text-blue-400">220,573</strong> unique accident records analyzed.</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-blue-400 font-bold">•</span>
              <span>Contains high-fidelity coordinates mapped across the entire country of France.</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-blue-400 font-bold">•</span>
              <span>Records detailed environmental variables including Lighting, Weather, Surface Conditions, and Time of Day.</span>
            </li>
          </ul>
        </section>

        <section className="glass-card p-8">
          <h3 className="text-2xl font-bold mb-4 text-white">🧠 The Architecture</h3>
          <p className="text-gray-300 mb-6 leading-relaxed">
            We process millions of data points into actionable real-time intelligence using cutting-edge technologies.
          </p>
          <ul className="space-y-4 text-gray-300">
            <li className="flex items-start gap-3">
              <span className="text-purple-400 font-bold">•</span>
              <span><b>Uber H3 Grid System:</b> Standardized, highly-efficient hexagonal zones to map historical blackspots.</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-purple-400 font-bold">•</span>
              <span><b>HistGradientBoosting AI:</b> Machine Learning classifier predicting the probability of a fatal crash in milliseconds.</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-purple-400 font-bold">•</span>
              <span><b>Dynamic Risk Multipliers:</b> Intersections are dynamically recalculated based on current weather and lighting.</span>
            </li>
          </ul>
        </section>
      </div>
    </div>
  );
}
