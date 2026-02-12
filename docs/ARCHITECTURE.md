# Architecture Guide

## System Overview

RescueRoute AI is a distributed system designed for autonomous disaster response coordination. The architecture separates concerns into four primary layers: simulation, backend API, AI decision-making, and frontend visualization.

## Core Components

### 1. Simulation Layer
**Developer**: Mihiran

The simulation engine models disaster scenarios with autonomous robots navigating hazardous environments.

**Key Features**:
- Multi-robot fleet simulation with independent agent behavior
- Dynamic obstacle generation (debris, fire hazards, water hazards)
- Victim placement and rescue mechanics
- Real-time state broadcasting via HTTP endpoints

**Technology**: Python with custom physics and pathfinding algorithms

**Endpoints**:
- `GET /simulation/state` - Current simulation state snapshot
- `POST /simulation/command` - Execute AI-generated commands

### 2. Backend API Layer
**Developer**: Daniyal Asif

FastAPI-based server that orchestrates communication between simulation, AI, and frontend.

**Key Features**:
- Server-Sent Events (SSE) for real-time data streaming
- AI command processing and validation
- State aggregation and transformation
- CORS-enabled for cross-origin requests

**Technology**: FastAPI, Uvicorn, Pydantic

**Endpoints**:
- `GET /` - Health check
- `GET /stream` - SSE stream of simulation updates
- `POST /ai-command` - Trigger AI decision-making
- `GET /simulation-state` - Proxy to simulation state

### 3. AI Decision Layer
**Developer**: Daniyal Asif

Gemini AI integration that analyzes disaster scenarios and generates strategic commands.

**Key Features**:
- Context-aware decision making based on robot positions, victims, and hazards
- Structured JSON command generation
- Multi-robot coordination strategies
- Real-time situation assessment

**Technology**: Google Gemini AI (gemini-2.0-flash-exp)

**Decision Process**:
1. Receive current simulation state
2. Analyze robot capabilities and positions
3. Identify priority targets (victims, hazards)
4. Generate coordinated movement commands
5. Return structured JSON response

### 4. Frontend Dashboard
**Developer**: Daniyal Asif (Development), Albert (UX/UI Design)

Modern web interface for real-time fleet monitoring and AI interaction.

**Key Features**:
- Live map visualization with robot tracking
- AI command interface with streaming responses
- Real-time metrics dashboard
- Responsive design with dark mode support

**Technology**: Next.js 16, React 19, TypeScript, Tailwind CSS

**Components**:
- `MapVisualizer` - Grid-based simulation rendering
- `AICommander` - AI interaction interface
- `MetricsPanel` - Fleet statistics display

## Data Flow

```
┌──────────────┐
│  Simulation  │ Generates state every tick
└──────┬───────┘
       │
       │ HTTP polling (1s intervals)
       ▼
┌──────────────┐
│  Backend API │ Aggregates & transforms data
└──────┬───────┘
       │
       ├─────────► SSE Stream ────────┐
       │                              │
       │ User triggers AI             │
       ▼                              ▼
┌──────────────┐              ┌──────────────┐
│  Gemini AI   │ Analyzes     │   Frontend   │
│              │ & decides    │   Dashboard  │
└──────┬───────┘              └──────────────┘
       │
       │ Returns commands
       ▼
┌──────────────┐
│  Simulation  │ Executes commands
└──────────────┘
```

## API Endpoints

### Backend API (Port 8000)

#### `GET /`
Health check endpoint.

**Response**: `{ "status": "ok" }`

#### `GET /stream`
Server-Sent Events stream providing real-time simulation updates.

**Response**: SSE stream with JSON payloads containing robot positions, victims, obstacles, and metrics.

#### `POST /ai-command`
Triggers AI analysis of current simulation state.

**Request Body**: None (uses current simulation state)

**Response**: Streamed AI decision-making process and final commands

#### `GET /simulation-state`
Proxies current simulation state from simulation service.

**Response**: Complete simulation state JSON

### Simulation API (Port 8001)

#### `GET /simulation/state`
Returns current simulation snapshot.

**Response**:
```json
{
  "robots": [{ "id": 1, "x": 10, "y": 15, "battery": 85, ... }],
  "victims": [{ "id": 1, "x": 20, "y": 25, "rescued": false }],
  "obstacles": [{ "type": "debris", "x": 5, "y": 10 }],
  "metrics": { "rescued": 3, "active_robots": 5 }
}
```

#### `POST /simulation/command`
Executes AI-generated commands in simulation.

**Request Body**:
```json
{
  "commands": [
    { "robot_id": 1, "action": "move", "target": { "x": 20, "y": 25 } }
  ]
}
```

## Technology Decisions

### Why FastAPI?
- Native async/await support for SSE streaming
- Automatic API documentation (OpenAPI/Swagger)
- High performance with minimal overhead
- Excellent Python ecosystem integration

### Why Next.js?
- Server-side rendering for optimal performance
- Built-in TypeScript support
- Modern React features (Server Components, Suspense)
- Excellent developer experience

### Why Gemini AI?
- Advanced reasoning capabilities for complex scenarios
- Structured output support (JSON mode)
- Fast response times for real-time decisions
- Cost-effective for hackathon development

### Why SSE over WebSockets?
- Simpler implementation for unidirectional data flow
- Native browser support without additional libraries
- Automatic reconnection handling
- Lower overhead for read-heavy applications

## Development Workflow

1. **Simulation** runs independently, generating disaster scenarios
2. **Backend** polls simulation and streams data to connected clients
3. **Frontend** subscribes to SSE stream and renders real-time updates
4. **User** triggers AI analysis via dashboard
5. **AI** analyzes state and generates commands
6. **Backend** forwards commands to simulation
7. **Simulation** executes commands and updates state

## Deployment

The system uses Docker Compose for orchestrated deployment:

```yaml
services:
  simulation:
    build: ./simulation
    ports: ["8001:8001"]
  
  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [simulation]
  
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    depends_on: [backend]
```

## Future Enhancements

- WebSocket support for bidirectional communication
- Database persistence for simulation history
- Multi-scenario support with scenario selection
- Advanced AI strategies (reinforcement learning)
- Mobile app for field monitoring

---

*Architecture designed for scalability, maintainability, and real-time performance*
