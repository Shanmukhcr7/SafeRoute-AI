# Phase 7: Digital Twin Simulation Engine

## The Digital Twin Concept
Phase 7 upgrades the project from an analytical platform to a full **Intelligent Transportation System (ITS)** simulation. Instead of "moving a marker," the system spawns **Digital Twins**—virtual vehicles that possess state, behavior, and telemetry.

## Component Breakdown

1. **Digital Vehicle Model (`vehicle_model.py`)**:
   - Every vehicle is instantiated with a Driver Profile: `SAFE`, `NORMAL`, or `AGGRESSIVE`.
   - Aggressive drivers naturally sustain higher speeds, which the `Context Engine` interprets as higher risk, resulting in more rapid `WARNING` state escalations.
   - Includes a State Machine (`IDLE -> MOVING -> WARNING -> DANGER -> STOPPED`).

2. **Route Interpolation Engine (`route_engine.py`)**:
   - Vehicles do not "jump" between coordinates. The engine uses mathematical linear interpolation based on Haversine distance and real-time speed.
   - Smooth, continuous GPS coordinates are generated every second.

3. **Telemetry Logger (`telemetry_logger.py`)**:
   - The absolute foundation for the upcoming Mission Control Playback.
   - Every tick (second), every vehicle's exact state (GPS, speed, Risk Score, H3 Zone, State) is written permanently to the SQLite `vehicle_telemetry` table.

4. **Simulation Manager (`simulation_manager.py`)**:
   - Capable of managing 100+ vehicles simultaneously.
   - It acts as the bridge: It takes the GPS from the Route Engine, injects simulated Weather from the environment, and feeds the combined package into the **Context Engine** (built in Phase 6).
   - The resulting Risk and Alerts instantly update the Digital Twin's internal state.

## Preparing for Phase 8
By building this Simulation Engine *now*, the upcoming **Streamlit Traffic Dashboard** (Phase 8) will immediately have rich, dynamic, multi-vehicle telemetry to visualize, complete with a Mission Control Playback slider.
