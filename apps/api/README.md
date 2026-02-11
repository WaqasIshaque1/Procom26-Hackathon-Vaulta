# Vaulta Voice Agent - Backend

AI-powered voice banking assistant with comprehensive banking operations, fraud protection, and real-time database integration.

## 🚀 Features

### Banking Operations (12 Total)
- ✅ **Account Balance & Transactions** - Real-time balance queries and transaction history
- ✅ **Loan Information** - View loan details, interest rates, terms, and status
- ✅ **Credit Card Management** - Check rewards points, payment due dates, credit limits
- ✅ **Card Listing** - View all customer cards with last 4 digits (secure)
- ✅ **Card Blocking** - Block lost/stolen cards with confirmation
- ✅ **Statement Requests** - Email account statements
- ✅ **Feedback Submission** - Submit complaints, praise, or suggestions

### Security Features (CRITICAL)
- 🚨 **Fraud Reporting** - Immediate account freeze + card block + human escalation
- 🔒 **International Transactions Toggle** - Enable/disable overseas card usage
- 📖 **Cheque Book Requests** - Order new cheque books (secure delivery)

### Technical Features
- 🗄️ **PostgreSQL Database** - 60 customers, full relational schema
- ⚡ **Hybrid Data Source** - Instant mock data + real database
- 🔐 **PIN Authentication** - Secure 4-digit PIN verification
- 🎯 **Multi-Provider LLM** - OpenAI + Google Gemini with fallback
- 📊 **LangSmith Observability** - Complete trace visibility

---

## 📊 Database Schema

**PostgreSQL (Neon Serverless)**
- `customers` (60 rows) - Customer data with PINs, balances, security flags
- `cards` (59 rows) - Card details with rewards, last 4 digits, status
- `transactions` (59 rows) - Transaction history with auto-categories
- `loans` (59 rows) - Loan information
- `feedback` (59 rows) - Customer feedback tracking
- `service_requests` - Fraud reports, cheque books, intl toggles

---

## 🏃 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL database (or use provided Neon connection)
- OpenAI API key
- LangSmith API key (optional but recommended)

### Installation

```bash
# Clone and navigate
cd Backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Database Setup

```bash
# Create schema
python create_schema.py

# Import customer data (60 customers from CSV)
python import_csv.py

# Add security features
python migrate_security_features.py
```

### Run Application

```bash
# Development server with auto-reload
uvicorn app.main:app --reload

# Or use the full stack (backend + frontend + ngrok)
../start-dev.sh
```

---

## 🧪 Test Credentials

### Hardcoded Demo Customer (Instant - 0ms)
- **Customer ID:** `1234`
- **PIN:** `5678`
- **Balance:** $1,250.50
- **Cards:** Debit (0001), Credit (9999) with 12,500 rewards points
- **Loan:** Auto loan $25,000 @ 4.5%

### Database Customers (PostgreSQL)
- **Customer IDs:** `1` to `60`
- **PINs:** `1000` to `1059`
- **Full Data:** Real transactions, loans, cards, balances

---

## 📡 API Endpoints

### Health Checks
- `GET /health` - Basic health check
- `GET /api/health/detailed` - Detailed system status

### Chat / Agent
- `POST /chat/completions` - OpenAI-compatible chat endpoint
- `POST /api/call` - Vapi-style call handler
- `POST /api/vapi/webhook` - Vapi webhook receiver

### Session Management
- `GET /api/sessions` - List all active sessions
- `GET /api/sessions/{session_id}` - Get specific session
- `POST /api/sessions/reset` - Reset session state

### Observability
- `GET /api/observability/status` - LangSmith integration status

---

## 💬 Example Conversations

### Check Balance
```
User: "What's my balance?"
Agent: "I'll need to verify your identity. Please provide your Customer ID and PIN."
User: "Customer ID 1234, PIN 5678"
Agent: "Your checking balance is $1,250.50. Would you like to see recent transactions?"
```

### Report Fraud (CRITICAL)
```
User: "Someone used my card without permission!"
Agent: "⚠️ FRAUD ALERT: Your account has been IMMEDIATELY FROZEN and all cards BLOCKED 
to protect you from further unauthorized transactions. Reference: FRAUD-20260211-1032. 
A fraud specialist will contact you shortly."

[Account frozen, cards blocked, human escalated - all automatic]
```

### Check Rewards Points
```
User: "How many rewards points do I have?"
Agent: "Your Credit card ending in 9999 has 12,500 rewards points! 
That's approximately $125.00 in rewards value."
```

### Order Cheque Book
```
User: "I need a new cheque book"
Agent: "Your cheque book has been ordered! Reference: CHQ-20260211-4053. 
It will be delivered to 123 Main Street, New York, NY 10001 within 7-10 business days."
```

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Database
DATABASE_URL=postgresql://user:pass@host/db

# OpenAI
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini

# Google Gemini (optional fallback)
GOOGLE_API_KEY=...

# LLM Provider Selection
LLM_PROVIDER=openai  # or 'gemini'

# LangSmith (observability)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_PROJECT=vaulta-voice-agent

# Vapi Integration
VAPI_API_KEY=...

# Security
PIN_REDACTION_ENABLED=true
```

---

## 🏗️ Architecture

```
Voice Layer (Vapi)
    ↓
FastAPI (/chat/completions)
    ↓
Credential Detection & Redaction
    ↓
LangGraph Workflow
    ├─→ Intent Router (classify request)
    ├─→ Auth Gate (verify if needed)
    └─→ Flow Handlers
        ├─→ Account Flow (balance, transactions, loans)
        ├─→ Card Flow (block, list, rewards)
        ├─→ Security Flow (fraud, intl, cheque)
        └─→ Feedback Flow
    ↓
Banking API (hybrid data source)
    ├─→ MOCK_CUSTOMERS (instant - 0ms)
    └─→ PostgreSQL (real data - 50-4000ms)
    ↓
LangSmith (observability)
```

---

## 🔐 Security Features

### PII Protection
- ✅ PINs never logged or traced
- ✅ Customer IDs hashed in traces
- ✅ Account numbers masked
- ✅ Credentials redacted: `[REDACTED_ID]`, `[REDACTED_PIN]`

### Authentication
- ✅ 4-digit PIN verification
- ✅ Identity required for sensitive operations
- ✅ Session-based state management
- ✅ Auth lockout after 3 failed attempts

###Critical Security Actions
- 🚨 **Fraud Detection** - Highest priority in intent routing
- 🚨 **Immediate Freeze** - Account locked, cards blocked instantly
- 🚨 **Human Escalation** - Mandatory review, cannot unfreeze via voice
- 🚨 **Audit Trail** - All actions logged in service_requests table

---

## 📚 Testing

### Run Test Suite
```bash
# Unit tests
pytest tests/

# Integration tests
python -m pytest tests/integration/

# Manual testing with cURL
curl -X POST http://localhost:8000/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-1",
    "messages": [
      {"role": "user", "content": "Check my balance"}
    ]
  }'
```

### Test Documentation
- **TEST_SCENARIOS.md** - 30 comprehensive test cases
- **CODE_DOCUMENTATION.md** - Complete technical documentation

---

## 📊 Performance

**Hardcoded Customer (1234):**
- Authentication: 0ms
- Balance query: 0-5ms
- Transaction history: 0-5ms

**Database Customer (1-60):**
- Authentication: 50-4000ms (network latency)
- Balance query: 100-200ms
- Transaction history: 150-300ms

**Hybrid Strategy Benefits:**
- Instant demos and testing
- Real production data when needed
- No database for simple queries
- Graceful fallback on DB errors

---

## 🚀 Deployment

### Render (Production)
```yaml
# render.yaml
services:
  - type: web
    name: vaulta-voice-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
 - key: OPENAI_API_KEY
      - key: LANGCHAIN_API_KEY
```

### Local Development
```bash
# Quick start (all services)
./start-dev.sh

# Backend only
uvicorn app.main:app --reload

# With specific port
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 📁 Project Structure

```
Backend/
├── app/
│   ├── main.py                      # FastAPI application
│   ├── api/
│   │   └── vapi_routes.py          # Chat completions endpoint
│   ├── agents/
│   │   ├── graph.py                # LangGraph workflow
│   │   ├── state.py                # State schema
│   │   ├── prompts.py              # System prompts
│   │   └── nodes/
│   │       ├── intent_router.py    # Intent classification
│   │       ├── account_flow.py     # Account operations (10 handlers)
│   │       ├── card_flow.py        # Card management
│   │       └── greeting_handler.py # Small talk
│   ├── services/
│   │   ├── banking_api.py          # Banking operations (12 functions)
│   │   └── session_manager.py      # Session state
│   └── core/
│       ├── config.py               # Configuration
│       ├── database.py             # PostgreSQL connection
│       ├── security.py             # PII redaction
│       └── llm_factory.py          # Multi-provider LLM
├── tests/                           # Test suite
├── CODE_DOCUMENTATION.md            # Technical docs
├── TEST_SCENARIOS.md                # Test cases
├── README.md                        # This file
└── requirements.txt                 # Dependencies
```

---

## 🛠️ Troubleshooting

### Database Connection Issues
```bash
# Test connection
python -c "
import psycopg2
conn = psycopg2.connect('postgresql://...')
print('✅ Connected!')
"

# Check tables
python inspect_db.py
```

### Missing Dependencies
```bash
pip install -r requirements.txt --upgrade
```

### LangSmith Not Tracing
```bash
# Verify environment variables
echo $LANGCHAIN_TRACING_V2  # should be 'true'
echo $LANGCHAIN_API_KEY     # should start with 'ls__'
```

---

## 📖 Documentation

- **CODE_DOCUMENTATION.md** - Complete technical documentation
- **TEST_SCENARIOS.md** - 30 test cases with expected outcomes
- **implementation_plan.md** - Security features implementation plan
- **new_capabilities.md** - Banking features quick reference
- **security_features.md** - Security features guide

---

## 🎯 Key Highlights

- ✅ **12 Banking Operations** - Comprehensive coverage
- ✅ **3 Critical Security Features** - Fraud protection, intl toggle, cheque books
- ✅ **PostgreSQL Integration** - 60 customers, full schema
- ✅ **Hybrid Performance** - 0ms for demos, real DB for production
- ✅ **Multi-Provider LLM** - OpenAI + Gemini with fallback
- ✅ **Voice Optimized** - Spoken number normalization
- ✅ **Production Ready** - Security, observability, error handling

---

## 📄 License

This project is developed for the Vaulta voice banking assessment.

## 🤝 Support

For questions or issues, refer to:
- CODE_DOCUMENTATION.md for technical details
- TEST_SCENARIOS.md for testing guidance
- .env.example for configuration options