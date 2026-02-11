// Vapi Call Status
export type CallStatus = 
  | 'inactive'
  | 'loading'
  | 'active'
  | 'ended'
  | 'error'

// Agent Flow Types (matching backend)
export type FlowType =
  | 'card_atm_issues'
  | 'account_servicing'
  | 'account_opening'
  | 'digital_support'
  | 'transfers_bill_payments'
  | 'account_closure'

// Message Types
export interface TranscriptMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  toolCalls?: ToolCall[]
  isFinal?: boolean
}

// Tool Call Information
export interface ToolCall {
  id: string
  name: string
  arguments: Record<string, any>
  result?: any
}

// Agent State (synced with backend)
export interface AgentState {
  verified: boolean
  currentFlow: FlowType | null
  verificationAttempts: number
  escalate: boolean
  customerId: string | null
}

// Call Metrics
export interface CallMetrics {
  duration: number
  startTime: Date | null
  endTime: Date | null
  messageCount: number
}

// Vapi Events
export interface VapiCallStartEvent {
  type: 'call-start'
  callId: string
}

export interface VapiCallEndEvent {
  type: 'call-end'
  callId: string
  endedReason?: string
}

export interface VapiTranscriptEvent {
  type: 'transcript'
  role: 'user' | 'assistant'
  transcript: string
  timestamp: number
}

export interface VapiErrorEvent {
  type: 'error'
  error: {
    message: string
    code?: string
  }
}

export interface VapiFunctionCallEvent {
  type: 'function-call'
  functionCall: {
    name: string
    parameters: Record<string, any>
  }
}

export type VapiEvent =
  | VapiCallStartEvent
  | VapiCallEndEvent
  | VapiTranscriptEvent
  | VapiErrorEvent
  | VapiFunctionCallEvent
