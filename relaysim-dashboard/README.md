# Relaysim Dashboard

Interactive web dashboard for the Relaysim Automated Firmware Test Harness.

## Overview

The Relaysim Dashboard is a React + TypeScript application that provides a browser-based interface for running and visualizing firmware test scenarios. It communicates with the Relaysim backend API to execute tests and display results in real-time.

## Features

- **Scenario Browser**: Visual card-based layout of available test scenarios
- **One-Click Execution**: Run scenarios with a single button click
- **Real-Time Status**: Live updates during scenario execution
- **State Visualization**: Animated state machine diagram showing IDLE → ACTIVE → FAULT transitions
- **Detailed Logging**: Timestamped execution logs with step-by-step details
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Clean Animations**: Smooth transitions and visual feedback

## Technology Stack

- **React 18.2**: UI framework
- **TypeScript 5.2**: Type-safe development
- **Vite**: Fast build tool and dev server
- **CSS3**: Custom styling with animations
- **Fetch API**: REST API communication

## Project Structure

```
relaysim-dashboard/
├── src/
│   ├── components/           # React components
│   │   ├── ScenarioList.tsx         # Scenario browser
│   │   ├── ScenarioList.css
│   │   ├── RunStatusPanel.tsx       # Status indicator
│   │   ├── RunStatusPanel.css
│   │   ├── DeviceStateVisualizer.tsx # State diagram
│   │   ├── DeviceStateVisualizer.css
│   │   ├── LogViewer.tsx            # Log display
│   │   └── LogViewer.css
│   ├── pages/
│   │   ├── HomePage.tsx             # Main page
│   │   └── HomePage.css
│   ├── api/
│   │   └── client.ts                # API wrapper
│   ├── types.ts                     # TypeScript types
│   ├── App.tsx
│   ├── App.css
│   └── main.tsx
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## Setup

### Prerequisites

- Node.js 16+ and npm
- Relaysim backend running on `http://localhost:8000`

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

   The dashboard will be available at `http://localhost:5173`

3. **Build for production:**
   ```bash
   npm run build
   ```

   Production files will be in the `dist/` directory.

4. **Preview production build:**
   ```bash
   npm run preview
   ```

## Development

### Running with Backend

Ensure the Relaysim backend is running before starting the dashboard:

```bash
# Terminal 1: Start backend
cd ../relaysim
python -m uvicorn api.main:app --reload

# Terminal 2: Start frontend
cd ../relaysim-dashboard
npm run dev
```

### API Configuration

The dashboard connects to the backend API at `http://localhost:8000`. This is configured in `src/api/client.ts`:

```typescript
const API_BASE_URL = 'http://localhost:8000';
```

For production deployment, update this to your backend URL.

### Proxy Configuration

The Vite dev server includes a proxy configuration in `vite.config.ts` to handle CORS during development:

```typescript
server: {
  port: 5173,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

## Components

### ScenarioList

Displays available scenarios in a grid of cards. Each card shows:
- Scenario name
- Description
- Filename
- Run button

**Props:**
- `scenarios: ScenarioInfo[]` - List of scenarios
- `onRunScenario: (name: string) => void` - Callback for running a scenario
- `isRunning: boolean` - Whether a scenario is currently running

### RunStatusPanel

Shows the current run status with visual indicators:
- Status badge (IDLE, RUNNING, PASSED, FAILED, ERROR)
- Scenario details (name, duration, steps)
- Step-by-step summary
- Error messages (if any)

**Props:**
- `runResult: RunResult | null` - Current run result
- `isRunning: boolean` - Running state

### DeviceStateVisualizer

Visualizes the device state machine with:
- Three-box diagram (IDLE, ACTIVE, FAULT)
- Animated transitions
- Current state highlighting
- Timeline of state changes

**Props:**
- `runResult: RunResult | null` - Current run result
- `isRunning: boolean` - Running state

### LogViewer

Displays detailed execution logs:
- Timestamped entries
- Log levels (INFO, WARN, ERROR)
- Step details and durations
- Scrollable container
- Syntax highlighting for errors

**Props:**
- `runResult: RunResult | null` - Current run result

## Styling

The dashboard uses custom CSS with:
- **Color Schemes**: Gradient backgrounds for visual appeal
- **Animations**: Smooth transitions, pulses, fades
- **Responsive Design**: Grid layouts that adapt to screen size
- **Visual Feedback**: Hover effects, active states, loading indicators

### Key Color Palette

- **Primary**: Purple gradient (#667eea → #764ba2)
- **Success**: Green gradient (#11998e → #38ef7d)
- **Error**: Red gradient (#eb3349 → #f45c43)
- **Warning**: Orange gradient (#ff6b6b → #ffa500)
- **Background**: Light blue-gray gradient (#f5f7fa → #c3cfe2)

## Type Safety

All API responses and component props are fully typed using TypeScript interfaces defined in `types.ts`:

```typescript
interface ScenarioInfo {
  name: string;
  description: string;
  filename: string;
}

interface RunResult {
  run_id: string;
  scenario_name: string;
  overall_status: 'running' | 'passed' | 'failed' | 'error';
  // ... more fields
}
```

## Error Handling

The dashboard includes comprehensive error handling:
- **API Errors**: Displayed in an error banner at the top
- **Network Failures**: Clear error messages
- **Loading States**: Spinner during data fetching
- **User Feedback**: Disabled buttons during execution

## Performance

Optimizations include:
- **Component Memoization**: Prevents unnecessary re-renders
- **Lazy Loading**: Components load only when needed
- **Efficient Updates**: State updates are batched
- **CSS Animations**: GPU-accelerated transforms

## Browser Support

Tested and working on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Troubleshooting

### Dashboard won't start

**Check Node version:**
```bash
node --version  # Should be 16+
```

**Clear node_modules and reinstall:**
```bash
rm -rf node_modules package-lock.json
npm install
```

### Can't connect to backend

**Verify backend is running:**
```bash
curl http://localhost:8000/api/scenarios
```

**Check CORS settings** in backend (`api/main.py`):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Scenarios not loading

**Check backend logs** for errors:
```bash
# Backend should show:
INFO: Relaysim API started
INFO: Available at http://localhost:8000
```

**Verify YAML files** exist in `relaysim/config/examples/`

## Contributing

This is a demonstration project. For production use, consider:
- Adding unit tests (Jest, React Testing Library)
- Implementing E2E tests (Playwright, Cypress)
- Adding accessibility features (ARIA labels, keyboard navigation)
- Implementing dark mode
- Adding internationalization (i18n)

## License

Part of the Relaysim project - demonstration purposes only.
