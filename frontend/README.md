# Intelligent Prior Authorization - Frontend

Modern React dashboard for AI-powered healthcare automation system.

## Features

- 🏥 **End-to-End Workflow Dashboard** - Complete prescription processing pipeline
- ✅ **Benefit Verification** - Coverage lookup and eligibility checks
- 🔍 **Policy Search** - Vector semantic search for relevant policies
- 👨‍⚕️ **Clinical Qualification** - LLM-powered eligibility determination
- 📋 **PA Form Generation** - Automated clinical narrative generation
- 📊 **Real-time Results** - Beautiful visualization of workflow progress
- 📱 **Responsive Design** - Works on desktop and mobile devices

## Tech Stack

- **React 18** - UI library
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first styling
- **TanStack Query** - API state management
- **Axios** - HTTP client
- **React Hot Toast** - Notifications

## Quick Start

### Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev
# Visit http://localhost:3000
```

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Docker

```bash
# Build Docker image
docker build -t intelligent-prior-auth-frontend .

# Run container
docker run -p 3000:3000 intelligent-prior-auth-frontend
```

## Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   ├── client.js           # Axios HTTP client
│   │   └── hooks.js            # TanStack Query hooks
│   ├── components/
│   │   ├── shared/             # Reusable components
│   │   ├── phases/             # Phase-specific views
│   │   ├── Dashboard.jsx       # Main dashboard
│   │   ├── Navbar.jsx          # Navigation bar
│   │   └── OrchestratorView.jsx # End-to-end workflow
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css               # Tailwind styles
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

## API Integration

The frontend communicates with the backend via RESTful API:

- `POST /benefit-verification/check-coverage` - Check drug coverage
- `POST /policy-search/search` - Search policies
- `POST /clinical-qualification/check-eligibility` - Check clinical eligibility
- `POST /prior-authorization/generate-form` - Generate PA form
- `POST /orchestration/process-prescription` - End-to-end workflow

## Features Explained

### Dashboard Tabs

1. **End-to-End Workflow** - Complete prescription processing in one request
2. **Coverage Check** - Individual benefit verification
3. **Policy Search** - Find relevant insurance policies
4. **Eligibility Check** - LLM-based clinical qualification
5. **PA Form** - Generate clinical narratives and forms

### Workflow Timeline

Visual representation of workflow progress with status indicators for each phase.

### Results Panel

Detailed breakdown of results with expandable sections for:
- Summary
- Patient Information
- Coverage Details
- Eligibility Status
- PA Form Data
- Raw JSON

## Development

### Adding New Components

Components follow a standard structure:

```jsx
import Card from '../shared/Card'
import Button from '../shared/Button'

export default function NewComponent() {
  return (
    <Card title="Feature Title">
      {/* Component content */}
    </Card>
  )
}
```

### Styling

Uses Tailwind CSS utility classes. Custom theme colors defined in `tailwind.config.js`:

- Primary: Blue
- Success: Green
- Warning: Yellow
- Error: Red

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Contributing

1. Create feature branch
2. Make changes
3. Test locally
4. Submit pull request

## License

All rights reserved ©2025 Intelligent Prior Authorization
