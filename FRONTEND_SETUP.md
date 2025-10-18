# Frontend Setup Guide

## Overview

The frontend is a modern React dashboard that connects to the FastAPI backend and provides a beautiful UI for interacting with all phases of the intelligent prior authorization system.

## 🚀 Quick Start

### Option 1: Docker Compose (Easiest)

```bash
# Build and start all services (backend + frontend + db + redis)
docker-compose up --build

# Frontend will be available at: http://localhost:3000
# Backend will be available at: http://localhost:8000
# Docs at: http://localhost:8000/docs
```

### Option 2: Manual Setup

#### Prerequisites
- Node.js 18+ and npm
- Python 3.10+ (for backend)
- PostgreSQL 16
- Redis 7

#### Steps

1. **Backend Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up environment
   cp .env.example .env
   # Edit .env and add your OPENROUTER_API_KEY
   
   # Generate and import mock data
   python scripts/generate_synthetic_data.py
   python scripts/import_data_to_db.py
   python scripts/build_vector_index.py
   
   # Start backend
   uvicorn app.main:app --reload
   ```

2. **Frontend Setup**
   ```bash
   # Navigate to frontend directory
   cd frontend
   
   # Install dependencies
   npm install
   
   # Create environment file
   cp .env.example .env
   
   # Start development server
   npm run dev
   ```

Visit http://localhost:3000 in your browser.

## 📋 Features & Tabs

### 1. **End-to-End Workflow** (Default Tab)
- Complete prescription processing in one click
- Visualize all phases executing sequentially
- See real-time progress and final recommendations

**Try it:**
```
Patient: P001
Drug: Ozempic
Provider: Dr. Smith
Click "Process Prescription"
```

### 2. **Coverage Check (Phase 2)**
- Verify if a drug is covered under a patient's plan
- View PA requirements
- See coverage criteria

**Try it:**
```
Patient ID: P001
Drug: Ozempic
Click "Check Coverage"
```

### 3. **Policy Search (Phase 3)**
- Search for relevant insurance policies using semantic search
- Vector embeddings find similar policies
- View policy documents and metadata

**Try it:**
```
Drug: Ozempic
Top Results: 3
Click "Search Policies"
```

### 4. **Clinical Eligibility (Phase 4)**
- LLM-powered eligibility determination
- RAG (Retrieval-Augmented Generation) with policy context
- Confidence scores and clinical justification

**Try it:**
```
Patient ID: P001
Drug: Ozempic
Policy Criteria: (auto-filled)
✓ Use RAG
Click "Check Eligibility"
```

### 5. **PA Form Generation (Phase 5)**
- Generate PA forms in JSON or Markdown
- LLM-generated clinical narratives
- Professional documentation format

**Try it:**
```
Patient ID: P001
Drug: Ozempic
Provider: Dr. Smith
NPI: 1234567890
Click "Generate JSON Form" or "Generate Markdown"
```

## 🏗️ Architecture

```
Frontend (React + Vite)
    ↓ HTTP/REST
Backend (FastAPI)
    ├─ Benefit Verification (Phase 2)
    ├─ Policy Search (Phase 3) → ChromaDB
    ├─ Clinical Qualification (Phase 4) → OpenRouter LLM
    ├─ PA Form Generation (Phase 5)
    └─ Orchestrator (Phase 6)
    ↓
PostgreSQL Database
```

## 🛠️ Development

### Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   ├── client.js       # Axios HTTP client
│   │   └── hooks.js        # React Query hooks for each endpoint
│   ├── components/
│   │   ├── shared/         # Reusable UI components
│   │   │   ├── Card.jsx
│   │   │   ├── Button.jsx
│   │   │   ├── LoadingSpinner.jsx
│   │   │   ├── WorkflowTimeline.jsx
│   │   │   └── ResultsPanel.jsx
│   │   ├── phases/         # Phase-specific views
│   │   │   ├── Phase2View.jsx
│   │   │   ├── Phase3View.jsx
│   │   │   ├── Phase4View.jsx
│   │   │   └── Phase5View.jsx
│   │   ├── Dashboard.jsx   # Tab navigation
│   │   ├── Navbar.jsx      # Top bar
│   │   └── OrchestratorView.jsx # End-to-end workflow
│   ├── App.jsx             # Root component
│   ├── main.jsx            # Entry point
│   └── index.css           # Tailwind styles
├── index.html              # HTML template
├── package.json
├── vite.config.js          # Vite configuration
├── tailwind.config.js      # Tailwind theme
└── postcss.config.js       # PostCSS config
```

### Adding a New Feature

1. **Create a new hook in `api/hooks.js`:**
   ```javascript
   export const useMyNewFeature = () => {
     return useMutation({
       mutationFn: async (payload) => {
         const { data } = await client.post('/endpoint', payload)
         return data
       },
     })
   }
   ```

2. **Create a new component in `components/`:**
   ```jsx
   import { useMyNewFeature } from '../api/hooks'
   import Card from './shared/Card'
   import Button from './shared/Button'

   export default function MyNewComponent() {
     const mutation = useMyNewFeature()
     // Component logic...
     return <Card title="My Feature">{/* JSX */}</Card>
   }
   ```

3. **Add to Dashboard tabs:**
   ```jsx
   const tabs = [
     // ... existing tabs
     { id: 'myfeature', label: 'My Feature', icon: '🎯' },
   ]
   ```

## 🎨 Styling

The project uses **Tailwind CSS** with a custom color scheme:

- **Primary**: Sky Blue (`#0ea5e9`)
- **Success**: Green (`#10b981`)
- **Warning**: Amber (`#f59e0b`)
- **Error**: Red (`#ef4444`)

### Using Colors

```jsx
// Background
<div className="bg-primary-50">Light background</div>
<div className="bg-primary-600">Dark button</div>

// Text
<p className="text-primary-700">Blue text</p>
<span className="text-success">Green success</span>
<span className="text-error">Red error</span>

// Borders
<div className="border-2 border-primary-300">Blue border</div>
```

## 🔌 API Integration

### Base URL
- Development: `http://localhost:8000`
- Production: Set via `VITE_API_URL` env var

### Endpoints Used

```
POST /benefit-verification/check-coverage
Body: { patient_id, drug }

POST /policy-search/search
Body: { drug, top_k }

POST /clinical-qualification/check-eligibility
Body: { patient_id, drug, policy_criteria, use_rag }

POST /prior-authorization/generate-form
Body: { patient_id, drug, provider_name, npi }

POST /prior-authorization/generate-form-markdown
Body: { patient_id, drug, provider_name, npi }

POST /orchestration/process-prescription
Body: { patient_id, drug, provider_name, npi }

GET /health
```

## 🧪 Testing

### Manual Testing Checklist

- [ ] All tabs load without errors
- [ ] End-to-end workflow completes successfully
- [ ] Individual phases work correctly
- [ ] Error handling shows appropriate messages
- [ ] Loading states display correctly
- [ ] Results display properly formatted
- [ ] Responsive design works on mobile

### Sample Test Data

```
Patients: P001, P002, P003
Drugs: Ozempic, Trulicity, Metformin, Victoza, Januvia
Insurance Plans: Aetna Gold, BlueCross Silver, etc.
```

## 📊 Performance

- First Load: ~2-3s (includes Vite + React initialization)
- API Responses: 1-10s (depends on LLM processing)
- UI Interactions: <200ms

### Optimization Tips

1. Use React DevTools to check for unnecessary re-renders
2. Implement code splitting for large views
3. Cache API responses with TanStack Query
4. Use Lighthouse for performance audits

## 🐛 Troubleshooting

### Frontend won't connect to backend

```bash
# Check if backend is running
curl http://localhost:8000/health

# If not, start backend in separate terminal
cd /path/to/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Port already in use

```bash
# Find and kill process on port 3000
lsof -i :3000
kill -9 <PID>

# Or use a different port
npm run dev -- --port 3001
```

### CORS errors

Make sure backend has CORS configured:
```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📱 Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## 📚 Further Reading

- [React Docs](https://react.dev)
- [Vite Docs](https://vitejs.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [TanStack Query](https://tanstack.com/query/latest)

## 🚀 Deployment

### Build for Production

```bash
npm run build  # Creates optimized dist/ folder
```

### Deploy to Vercel

```bash
npm install -g vercel
vercel --prod
```

### Deploy to Netlify

```bash
npm run build
netlify deploy --prod --dir=dist
```

## 📝 Environment Variables

Create `frontend/.env`:

```env
# API Configuration
VITE_API_URL=http://localhost:8000

# App Configuration
VITE_APP_NAME=Intelligent Prior Authorization
VITE_APP_VERSION=1.0.0
```

## 📞 Support

For issues or questions:
1. Check the documentation
2. Review backend logs for API errors
3. Check browser console for frontend errors
4. Open an issue on GitHub

---

**Happy building! 🎉**
