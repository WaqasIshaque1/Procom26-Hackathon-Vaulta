# Vaulta Voice Agent - Frontend

A modern Next.js 14 frontend for the Vaulta Voice AI Agent with Vapi.ai integration. This project provides a professional banking interface for real-time voice conversations with an AI-powered banking assistant.

## 🎯 Overview
,
This frontend application enables users to interact with the Vaulta banking assistant through voice. It features:

- **Real-time voice communication** via Vapi.ai SDK
- **Live transcript display** with user and assistant messages
- **Agent state tracking** (verification, flow, escalation status)
- **Tool call visualization** showing which banking operations are being performed
- **Professional banking UI** with status indicators and metrics
- **Error handling** with user-friendly error messages
- **Responsive design** that works on desktop and mobile devices

## 📋 Prerequisites

- **Node.js**: Version 18 or higher
- **npm** or **yarn**: Package manager
- **Vapi.ai account**: With API keys and assistant configuration
- **Backend API**: FastAPI backend running on Render or local environment

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
# or
yarn install
```

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.local.example .env.local
```

Edit `.env.local` and add your credentials:

```env
# Vapi Configuration - Get these from your Vapi.ai dashboard
NEXT_PUBLIC_VAPI_PUBLIC_KEY=your_vapi_public_key_here
NEXT_PUBLIC_VAPI_ASSISTANT_ID=your_vapi_assistant_id_here

# Backend API URL
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# Optional: Google Analytics
NEXT_PUBLIC_GA_ID=

# Access Gate (assessment review)
# NOTE: Share this code separately with reviewers; the app is gated by IntroGate.
ACCESS_CODE=your_access_code_here
```

### 3. Run Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### 4. Build for Production

```bash
npm run build
npm start
```

## 📁 Project Structure

```
vaulta-voice-agent/
├── app/
│   ├── layout.tsx                 # Root layout
│   ├── page.tsx                   # Main page
│   ├── not-found.tsx              # 404 page
│   └── globals.css                # Global styles
├── components/
│   ├── VoiceAgentInterface.tsx     # Main voice interface
│   └── ui/                        # shadcn/ui components
│       ├── button.tsx
│       ├── card.tsx
│       ├── badge.tsx
│       └── scroll-area.tsx
├── hooks/
│   └── useVapiClient.ts           # Vapi integration hook
├── lib/
│   └── utils.ts                   # Utility functions
├── types/
│   ├── vapi.ts                    # Vapi TypeScript types
│   └── index.ts                   # Type exports
├── .env.local.example             # Environment template
├── next.config.js                 # Next.js configuration
├── tailwind.config.ts             # Tailwind CSS configuration
├── tsconfig.json                  # TypeScript configuration
├── package.json                   # Dependencies and scripts
├── vercel.json                    # Vercel deployment config
└── README.md                      # This file
```

## 🔧 Technology Stack

| Technology | Purpose | Version |
|-----------|---------|---------|
| **Next.js** | React framework | 14.1.0 |
| **React** | UI library | 18.2.0 |
| **TypeScript** | Type safety | 5.3.3 |
| **Tailwind CSS** | Styling | 3.4.0 |
| **shadcn/ui** | UI components | Latest |
| **Vapi.ai SDK** | Voice integration | 2.5.2 |
| **Lucide React** | Icons | 0.294.0 |
| **date-fns** | Date formatting | 3.0.0 |

## 🎤 Features

### Voice Integration
- **Start/Stop Calls**: Simple button controls to initiate and end voice conversations
- **Real-time Transcripts**: Live display of user and assistant messages
- **Automatic Scrolling**: Transcript area auto-scrolls to show latest messages
- **Connection Status**: Visual indicators for call status (inactive, loading, active, ended, error)

### Agent State Management
- **Identity Verification**: Badge showing verification status
- **Flow Tracking**: Displays current banking flow (card issues, account servicing, etc.)
- **Escalation Alerts**: Shows when escalation to human agent is needed
- **Message Count**: Tracks number of messages in current session

### UI/UX
- **Professional Banking Theme**: Blue gradient header with banking-appropriate styling
- **Status Badges**: Color-coded badges for different states
- **Error Messages**: Clear error display with actionable feedback
- **Demo Information**: Session info panel for debugging and assessment
- **Testing Instructions**: Built-in guide for test scenarios

## 🧪 Testing

### Test Credentials
- **Customer ID**: `1234`
- **PIN**: `5678`

### Test Scenarios

1. **Lost Card Flow** (Deep Flow)
   ```
   User: "My card was stolen"
   Expected: Agent initiates card replacement flow
   ```

2. **Balance Check** (Deep Flow)
   ```
   User: "What's my account balance?"
   Expected: Agent retrieves and displays balance
   ```

3. **Login Issue** (Stub Flow)
   ```
   User: "I can't log into the mobile app"
   Expected: Agent provides troubleshooting or escalates
   ```

4. **Account Closure** (Stub Flow)
   ```
   User: "I want to close my account"
   Expected: Agent routes to appropriate handler
   ```

## 📝 Environment Configuration

### Local Development (`.env.local`)
```env
NEXT_PUBLIC_VAPI_PUBLIC_KEY=your_dev_key
NEXT_PUBLIC_VAPI_ASSISTANT_ID=your_dev_assistant_id
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### Production (Set in Vercel Dashboard)
```env
NEXT_PUBLIC_VAPI_PUBLIC_KEY=your_prod_key
NEXT_PUBLIC_VAPI_ASSISTANT_ID=your_prod_assistant_id
NEXT_PUBLIC_BACKEND_URL=https://your-backend.onrender.com
```

## 🚀 Deployment to Vercel

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Initial frontend commit"
git push origin main
```

### Step 2: Import in Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Select your GitHub repository
4. Click "Import"

### Step 3: Configure Environment Variables
In the Vercel dashboard, add these environment variables:
- `NEXT_PUBLIC_VAPI_PUBLIC_KEY`
- `NEXT_PUBLIC_VAPI_ASSISTANT_ID`
- `NEXT_PUBLIC_BACKEND_URL`

### Step 4: Deploy
Vercel will automatically build and deploy your project. Your site will be available at `https://your-project.vercel.app`

## 🔌 API Integration

### Vapi.ai Integration
The `useVapiClient` hook handles all Vapi.ai communication:

```typescript
const {
  callStatus,        // 'inactive' | 'loading' | 'active' | 'ended' | 'error'
  messages,          // Array of TranscriptMessage
  agentState,        // Agent state (verified, flow, escalation)
  metrics,           // Call metrics (duration, message count)
  error,             // Error message if any
  startCall,         // Function to start a call
  stopCall,          // Function to end a call
  isCallActive,      // Boolean: is call currently active
  isCallLoading,     // Boolean: is call initializing
} = useVapiClient()
```

### Backend Communication
The frontend communicates with the FastAPI backend through:
- **Vapi.ai** handles voice STT/TTS
- **Backend API** processes banking operations
- **Frontend** displays results and manages UI state

## 🐛 Troubleshooting

### Microphone Not Working
- Ensure HTTPS is enabled (required for microphone access)
- Check browser permissions for microphone access
- Verify Vapi.ai credentials are correct
- Check browser console for errors

### No Audio Playback
- Check browser audio permissions
- Verify TTS provider is configured in Vapi
- Ensure speakers/headphones are connected
- Check browser console for errors

### Backend Connection Errors
- Verify `NEXT_PUBLIC_BACKEND_URL` is correct
- Ensure backend is deployed and running
- Check CORS configuration on backend
- Verify network connectivity

### TypeScript Errors
```bash
# Check TypeScript compilation
npm run lint

# Fix any issues and rebuild
npm run build
```

### Build Errors
```bash
# Clear cache and reinstall
rm -rf node_modules .next
npm install
npm run build
```

## 📚 Component Documentation

### VoiceAgentInterface
Main component that orchestrates the voice interface. Uses the `useVapiClient` hook to manage Vapi state and provides UI for:
- Call controls (Start/Stop buttons)
- Transcript display
- Status indicators
- Error handling

### useVapiClient Hook
Custom React hook that manages:
- Vapi client initialization
- Event listeners for call lifecycle
- Message state management
- Agent state tracking
- Error handling

### UI Components
- **Button**: Customizable button with variants (default, destructive, outline, secondary, ghost, link)
- **Card**: Container component with header, content, and footer
- **Badge**: Status indicator with variants
- **ScrollArea**: Scrollable container for transcript

## 🎨 Styling

The project uses:
- **Tailwind CSS 3**: Utility-first CSS framework
- **CSS Variables**: For theme customization
- **Responsive Design**: Mobile-first approach
- **Dark Mode Support**: Theme context for light/dark switching

## 📦 Scripts

```bash
# Development
npm run dev              # Start dev server

# Building
npm run build            # Build for production
npm start                # Start production server

# Code Quality
npm run lint             # Run ESLint
```

## 🔐 Security Considerations

- **Environment Variables**: Never commit `.env.local` - it contains sensitive keys
- **HTTPS**: Always use HTTPS in production for microphone access
- **API Keys**: Keep Vapi public key safe; never expose private keys
- **CORS**: Ensure backend CORS is properly configured
- **Input Validation**: Backend should validate all user inputs

## 📄 License

Proprietary - Vaulta Assessment Project

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review browser console for error messages
3. Verify environment variables are set correctly
4. Check Vapi.ai documentation: https://docs.vapi.ai
5. Review backend logs for API errors

## 📞 Contact

For technical support or questions about this frontend implementation, please contact the development team.

---

**Last Updated**: February 2026
**Version**: 1.0.0
**Status**: Production Ready
**Framework**: Next.js 14 (App Router)
