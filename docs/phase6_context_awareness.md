# Phase 6: Context Awareness Engine

## Architectural Vision
Instead of statically pushing weather data into the AI, Phase 6 introduces a fully decoupled **Context Awareness Engine**. This treats the system like a real autonomous or driver-assistance vehicle that is continuously sensing its environment.

## The Context Object
All live inputs (Weather API, GPS coordinates, local time, vehicle telemetry, road topography) are ingested via dedicated modules (`weather.py`, `gps.py`, `time_context.py`, `road_context.py`). These modules evaluate the raw metrics and generate scientifically grounded Risk Modifiers and explanations.

Example Context Pipeline:
1. `raw_data["rain"] = True`
2. `weather.py` evaluates: `modifier += 15.0`, explanation: `"Rain (-30% Visibility, -20% Road Grip)"`
3. All modules output to `context_engine.py` which builds a unified `Context Object`.

## The Dynamic Risk Formula
The master `DynamicRiskEngine` combines the past (historical), the future (AI), and the present (Context):

```text
Final Dynamic Risk = 
    (Historical Risk * AI Severity Multiplier) 
    + Weather Modifier 
    + Time Modifier 
    + Road Modifier 
    + Speed Modifier
```

## Advanced Capabilities
1. **Zone Status Escalation**: Hexagons are no longer just colors. They now have an Escalation Status: `SAFE -> WATCH -> WARNING -> DANGER -> CRITICAL`.
2. **5-Minute Forecast**: Computes a lookahead risk (`forecast_5min`) anticipating compounding environmental decay (e.g., night + rain).
3. **Emergency Recommendation Engine**: Automatically generates actionable advice (e.g., *Reduce Speed by 20 km/h, Turn On Fog Lights, Avoid Sudden Braking*) based on the active modifiers inside the Context Object.
4. **Notification Queue (`alerts` table)**: Every time a zone hits `WARNING` or above, it is silently logged to the `alerts` SQLite table, establishing a permanent ledger of risks ready for Phase 8 (Driver Alert UI) and Phase 9 (Traffic Dashboard).
