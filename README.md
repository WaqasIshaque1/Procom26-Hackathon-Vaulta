# 🏦 Vaulta AI: Hybrid Voice & Chat AI Agent

> **📞 Live Demo: Talk to Vaulta AI now!**
> 
> *   **+1 (725) 444 4105** (Calls)
> *   **+1 (717) 539 5595** (SMS + Calls)
> *   **+1 (830) 374 0578** (Call)
> *   **[Live Web Interface](https://vaulta-client.vercel.app/)**

This repository hosts a next-generation **Hybrid AI Voice & Chat Agent** built for **Vaulta AI**. It seamlessly handles customer intents through **Omnichannel** interactions—including **Telephony, SMS, Web Voice, and Chat**—enforcing strict banking security guardrails.

---

## 🚀 Key Features

- **Hybrid Interaction:** Engage with the agent via **Voice** (Web & Phone) or **Chat** (Text).
- **No App Installation Required:** Users can interact directly via standard phone calls, SMS, or the web browser—no download needed.
- **Unified Context Management:** Seamlessly maintains conversation history and context across all channels (SMS, Phone Call, Web Voice, and Web Chat).
- **Omnichannel Support:**
  - **Web:** Interactive voice and chat interface.
  - **Telephony:** Call the agent directly via **Twilio** integration.
  - **SMS:** Text the agent for quick inquiries.
- **Advanced Security:**
  - **Identity Verification:** Strict authentication gates before sensitive actions.
  - **Robust Logging:** Comprehensive logging of all errors and traces, ensuring every detail is captured while automatically **redacting sensitive info** (PII/PCI).
- **Intelligent Reasoning:**
  - Powered by **LangGraph** for stateful, deterministic conversation flows.
  - Uses **Gemini API** for high-quality natural language understanding.
- **Robust Infrastructure:**
  - **Turborepo:** High-performance build system for the monorepo.
  - **Redis:** High-performance in-memory database for caching and real-time state management.
  - **Neon DB (PostgreSQL):** Serverless, scalable database for customer data.
  - **LangSmith:** Full observability and tracing of AI execution.
  - **FastAPI:** High-performance backend API.

---

## 🛠️ Technology Stack

We leverage a cutting-edge stack to deliver a secure, responsive, and intelligent experience:

- **Core AI & Orchestration:**
  - **Model Agnostic:** Architected to work with any large language model (LLM).
  - **Gemini API:** Currently configured intelligence engine.
  - **LangChain & LangGraph:** For building stateful, complex agentic workflows.
- **Voice & Telephony:**
  - **Vapi.ai:** Robust voice orchestration system.
  - **Flexible STT/TTS:** Compatible with any provider. Currently enabling **Deepgram Nova-3** (STT) and **ElevenLabs** (TTS) for superior audio quality.
  - **Twilio:** For telephony and SMS capabilities.
  - **Third-Party Integrations:** Seamlessly connects with external automation tools via Vapi's robust tool calling system.
- **Backend & Database:**
  - **FastAPI:** Python-based high-performance web framework.
  - **Redis:** In-memory data structure store used for caching and session state.
  - **Neon DB (PostgreSQL):** reliable & serverless database storage.
  - **Dataset:** [Comprehensive Banking Database](https://github.com/ahsan084/Banking-Dataset/blob/main/Comprehensive_Banking_Database.csv) for realistic banking data simulation.
  - **SQLAlchemy:** ORM for database interactions.
- **Frontend:**
  - **Next.js:** React framework for the web interface.
  - **TailwindCSS:** For modern, responsive styling.
- **Tooling & DevOps:**
  - **Turborepo:** Monorepo build tool.
  - **LangSmith:** For debugging, testing, and monitoring AI chains.

---

## 🤖 What This AI Can Do

The Vaulta AI Agent is capable of handling complex banking scenarios:

1.  **Identity Verification:** Securely authenticates users using Voice ID or PIN verification.
2.  **Card Management:**
    - **Block Card:** Immediately blocks a lost or stolen card after user confirmation.
    - **Replace Card:** Automatically initiates a new card order **only** if the previous card was blocked due to theft or loss.
    - **Card Order Status:** Tracks the shipping and delivery status of new cards.
    - **Payment Controls:** Enable/disable **International Payments** and **E-commerce Payments**.
    - **Limit Management:** Process requests for **Credit Limit Increases**.
3.  **Financial Services:**
    - **Loan Requests:** Assists users in applying for personal or business loans.
    - **Loan Status:** Tracks the progress of active loan applications.
    - **Loan Eligibility:** Automated detection of loan eligibility based on user profile and history.
4.  **Account Inquiries:**
    - **Account Status:** Checks if the account is active, dormant, or frozen.
    - **Balance Check:** Provides real-time account balance updates.
    - **Transaction History:** Reviews recent transactions.
    - **Update Personal Info:** Modifies user details (email, address). *Note: PIN change requests are routed to a secure stub for processing.*
4.  **Security & Fraud:**
    - **Fraud Detection:** Real-time analysis of interactions to detect and flag suspicious behavior.
    - **Block Users:** Instantly freezes all transactions and account activity for flagged users until manual review is completed to prevent unauthorized activity.
5.  **General Support:** Answers FAQs about banking services, hours, and locations.
6.  **Feedback Collection:** Gathers user feedback post-interaction to continuously improve service quality.
7.  **Hybrid Handoff:** seamless transition between voice and chat as needed.

---

## 📂 Repository Structure (Turborepo)

The project is organized as a monorepo:

```text
.
├── Vaulta/
│   ├── apps/
│   │   ├── client/        # Next.js Frontend (Web Interface)
│   │   ├── api/           # FastAPI Backend (AI Logic)
│   │   ├── web/           # (Additional Web App)
│   │   └── docs/          # Documentation
│   └── packages/          # Shared configurations (eslint, tsconfig, etc.)
└── start-dev.sh           # Unified startup script
```

---

## 🚀 Getting Started

We provide a unified script to start the entire development environment (Frontend, Backend, and Ngrok tunnel).

### Prerequisites
- **Bun** (for package management)
- **Python 3.11+**
- **Ngrok** (for exposing the local backend to Vapi/Twilio)

### Quick Start

Simply run the startup script from the root directory:

```bash
./start-dev.sh
```

This script will:
1.  Start an **Ngrok** tunnel to expose your local API.
2.  Launch the **Turborepo** dev environment, starting both the **Client** and **API** apps.
3.  Provide you with the public URL to configure in your Vapi dashboard.

---

## ⚖️ Engineering Decisions

### **Turborepo (Monorepo)**
We migrated to a monorepo to manage the Frontend and Backend in a single codebase. This improves code sharing, standardizes tooling, and simplifies the deployment pipeline.

### **LangGraph State Machine**
We chose **LangGraph** over linear chains to ensure **deterministic routing**. In banking, security is paramount. We need absolute control over the conversation flow—for example, ensuring a user *cannot* reach the "Block Card" capability without passing the "Identity Verification" node first.

### **Vapi.ai for Voice**
Using **Vapi.ai** allows us to offload the complexities of voice activity detection, interruption handling, and latency optimization, letting us focus on the banking logic and security guardrails.

---

## 🧪 Validation

- **Voice Test:** Call the phone number linked to the agent or use the web interface. Say "I lost my card" to test the security gate.
- **Chat Test:** Use the chat interface to ask for your balance.
- **SMS Test:** Send a text message to the Twilio number to verify SMS handling.
