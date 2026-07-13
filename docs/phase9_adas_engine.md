# Phase 9: Advanced Driver Assistance System (ADAS) Engine

## Automotive Industry Architecture
Moving away from a simple "Alert Popup" system, Phase 9 re-architects the Driver Alert mechanism to mimic modern ADAS platforms (like Mobileye or Tesla Autopilot).

The system doesn't trigger blindly based on distance. It calculates the physical **Time To Enter (TTE)** based on the digital twin's current speed and exact distance to the boundary of a critical H3 hexagon.

## Core Modules (`adas/`)
1. **`zone_monitor.py`**: Computes TTE. If a vehicle is doing 120km/h toward a Critical Zone, the TTE shrinks rapidly, triggering alerts much earlier than a vehicle moving at 30km/h.
2. **`alert_engine.py`**: A 5-Level Priority System.
   - 🟢 Level 1 (Information)
   - 🟡 Level 2 (Caution)
   - 🟠 Level 3 (Warning)
   - 🔴 Level 4 (Critical)
   - ⚫ Level 5 (Emergency)
3. **`notification_manager.py`**: Implements a Priority Min-Max Queue (`heapq`). If five alerts trigger simultaneously (e.g., Rain + High Speed + Critical Zone), the queue squashes lower-priority noise and *only* presents the highest priority emergency to the driver.
4. **`driver_scorer.py`**: Dynamically adjusts a Driver Safety Score from 100 based on their responsiveness to alerts and contextual speeding (e.g., speeding in heavy rain deducts more points than speeding on a sunny day).
5. **`recommendation_engine.py`**: Translates AI insights into actionable Human Machine Interface (HMI) commands ("Reduce Speed", "Turn On Fog Lights").
6. **`voice_assistant.py`**: Simulated `pyttsx3` voice prompts to audibly warn the driver without forcing them to look at the screen.

## Streamlit HMI
A dedicated Streamlit page (`6_ADAS_Display.py`) acts as the in-car console, fetching live telemetry and presenting the prioritized, contextualized warnings and AI recommendations.

---

## IEEE Research Paper Assets (Mermaid Diagrams)

### 1. System Architecture (Component Diagram)
```mermaid
graph TD
    A[Historical SQLite Dataset] --> B(Risk Intelligence Engine)
    C[Live Weather & Time API] --> D(Context Awareness Engine)
    E[Digital Twin Vehicle] --> D
    B --> F(AI Severity Predictor)
    D --> F
    F --> G(Dynamic Risk Engine)
    G --> H(ADAS Notification Queue)
    H --> I[Human Machine Interface - Streamlit]
```

### 2. Vehicle State Machine
```mermaid
stateDiagram-v2
    [*] --> IDLE
    IDLE --> MOVING : Speed > 0
    MOVING --> WARNING : TTE < 30s (Warning Zone)
    WARNING --> CRITICAL : TTE < 10s (Critical Zone)
    CRITICAL --> MOVING : Exited Zone
    CRITICAL --> STOPPED : Speed = 0
    MOVING --> STOPPED : Speed = 0
    STOPPED --> [*]
```

### 3. ADAS Alert Priority Logic (Activity Diagram)
```mermaid
flowchart TD
    Start([Receive GPS & Zone Data]) --> CalcTTE{Calculate Time To Enter}
    CalcTTE --> |TTE < 10s| L5[Level 5: Emergency Alert]
    CalcTTE --> |TTE < 30s| L3[Level 3: Warning Alert]
    L5 --> Q[Priority Queue]
    L3 --> Q
    Q --> Check{Is Priority > Current?}
    Check --> |Yes| HMI[Trigger Visual & Voice UI]
    Check --> |No| Drop[Drop/Log Silently]
```
