'use client'

import { useEffect, useState, useCallback, useRef } from 'react'
import Vapi from '@vapi-ai/web'
import type {
  CallStatus,
  TranscriptMessage,
  AgentState,
  CallMetrics,
  VapiEvent,
  ToolCall,
} from '@/types/vapi'
import { sanitizeError } from '@/lib/error-utils'
import type { FlowType } from '@/types/vapi'

/**
 * Custom hook for Vapi.ai integration
 * Manages call status, transcripts, agent state, and metrics
 */
const DEFAULT_AGENT_STATE: AgentState = {
  verified: false,
  currentFlow: null,
  verificationAttempts: 0,
  escalate: false,
  customerId: null,
}

const FLOW_TYPES: FlowType[] = [
  'card_atm_issues',
  'account_servicing',
  'account_opening',
  'digital_support',
  'transfers_bill_payments',
  'account_closure',
]

const normalizeFlow = (flow: unknown): FlowType | null => {
  if (typeof flow !== 'string') return null
  const normalized = flow.trim().toLowerCase()
  return FLOW_TYPES.includes(normalized as FlowType) ? (normalized as FlowType) : null
}

const extractAgentStateFromObject = (payload: unknown): Partial<AgentState> | null => {
  if (!payload || typeof payload !== 'object') return null

  const candidate: any =
    (payload as any).agentState ??
    (payload as any).agent_state ??
    (payload as any).state ??
    payload

  if (!candidate || typeof candidate !== 'object') return null

  const next: Partial<AgentState> = {}

  if (typeof candidate.verified === 'boolean') {
    next.verified = candidate.verified
  }

  const flow =
    candidate.currentFlow ??
    candidate.current_flow ??
    candidate.flow ??
    candidate.currentFlowType

  const normalizedFlow = normalizeFlow(flow)
  if (normalizedFlow) {
    next.currentFlow = normalizedFlow
  }

  const attempts =
    candidate.verificationAttempts ??
    candidate.verification_attempts ??
    candidate.attempts ??
    candidate.verifyAttempts

  if (typeof attempts === 'number' && Number.isFinite(attempts)) {
    next.verificationAttempts = attempts
  }

  const escalation =
    candidate.escalate ??
    candidate.escalation ??
    candidate.needsEscalation ??
    candidate.needsHuman

  if (typeof escalation === 'boolean') {
    next.escalate = escalation
  }

  const customerId = candidate.customerId ?? candidate.customer_id ?? candidate.userId
  if (typeof customerId === 'string' && customerId.trim()) {
    next.customerId = customerId
  }

  return Object.keys(next).length > 0 ? next : null
}

const extractAgentStateFromMessage = (message: any): Partial<AgentState> | null => {
  if (!message || typeof message !== 'object') return null

  if (message.type === 'metadata') {
    const raw = message.metadata
    if (typeof raw === 'string') {
      try {
        return extractAgentStateFromObject(JSON.parse(raw))
      } catch {
        return null
      }
    }
    return extractAgentStateFromObject(raw)
  }

  return extractAgentStateFromObject(message)
}

const getGreetingMessage = () => {
  const hours = new Date().getHours()
  const greeting =
    hours < 12 ? 'Good morning' : hours < 18 ? 'Good afternoon' : 'Good evening'
  return `${greeting}. This conversation currently supports English only. For urgent assistance, call our hotline at 1-800-123-4567.`
}

const shouldMergeTranscript = (previous: TranscriptMessage, next: TranscriptMessage) => {
  if (previous.role !== next.role) return false
  const prevText = previous.content.trim()
  const nextText = next.content.trim()
  if (!prevText || !nextText) return false

  const prevTime = previous.timestamp instanceof Date ? previous.timestamp.getTime() : 0
  const nextTime = next.timestamp instanceof Date ? next.timestamp.getTime() : 0
  const withinWindow = prevTime > 0 && nextTime > 0 ? nextTime - prevTime <= 3500 : true

  if (!withinWindow) return false
  if (previous.isFinal === false) return true

  return (
    nextText.startsWith(prevText) ||
    prevText.startsWith(nextText) ||
    nextText === prevText
  )
}

const countFinalMessages = (items: TranscriptMessage[]) =>
  items.reduce((count, msg) => {
    if (msg.role === 'system') return count
    if (msg.isFinal === false) return count
    return count + 1
  }, 0)

export function useVapiClient() {
  const [vapi, setVapi] = useState<Vapi | null>(null)
  const [callStatus, setCallStatus] = useState<CallStatus>('inactive')
  const callStatusRef = useRef<CallStatus>('inactive')
  const [messages, setMessages] = useState<TranscriptMessage[]>([])
  const pendingToolCallsRef = useRef<ToolCall[]>([])
  const silenceWarningTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const silenceHangupTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const silenceWarnedRef = useRef(false)
  const [agentState, setAgentState] = useState<AgentState>(DEFAULT_AGENT_STATE)
  const [metrics, setMetrics] = useState<CallMetrics>({
    duration: 0,
    startTime: null,
    endTime: null,
    messageCount: 0,
  })
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    callStatusRef.current = callStatus
  }, [callStatus])

  useEffect(() => {
    const nextCount = countFinalMessages(messages)
    setMetrics((prev) =>
      prev.messageCount === nextCount ? prev : { ...prev, messageCount: nextCount }
    )
  }, [messages])

  // Initialize Vapi client
  useEffect(() => {
    const publicKey = process.env.NEXT_PUBLIC_VAPI_PUBLIC_KEY

    if (!publicKey) {
      // Intentionally passing the technical error to sanitizeError so it can be logged internally
      setError(sanitizeError(new Error('VAPI public key not configured'), 'Initialization'))
      return
    }

    try {
      const vapiClient = new Vapi(publicKey)
      setVapi(vapiClient)
    } catch (err) {
      setError(sanitizeError(err, 'Vapi Initialization'))
    }
  }, [])

  // Set up Vapi event listeners
  useEffect(() => {
    if (!vapi) return

    const warningMessages = [
      'Hey, are you still there?',
      'Are you still there? Please let me know if you have any other questions.',
      'Do you still want to continue talking?',
    ]

    const closingMessage =
      'It seems like you might be busy. If you have any further questions, please don’t hesitate to call us back. Have a great day!'

    const clearSilenceTimers = () => {
      if (silenceWarningTimeoutRef.current) {
        clearTimeout(silenceWarningTimeoutRef.current)
        silenceWarningTimeoutRef.current = null
      }
      if (silenceHangupTimeoutRef.current) {
        clearTimeout(silenceHangupTimeoutRef.current)
        silenceHangupTimeoutRef.current = null
      }
    }

    const scheduleSilenceTimers = () => {
      clearSilenceTimers()
      silenceWarnedRef.current = false

      silenceWarningTimeoutRef.current = setTimeout(() => {
        if (callStatusRef.current !== 'active') return
        silenceWarnedRef.current = true

        const warning =
          warningMessages[Math.floor(Math.random() * warningMessages.length)]

        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: warning,
            timestamp: new Date(),
            isFinal: true,
          },
        ])

        silenceHangupTimeoutRef.current = setTimeout(async () => {
          if (callStatusRef.current !== 'active') return

          setMessages((prev) => [
            ...prev,
            {
              role: 'assistant',
              content: closingMessage,
              timestamp: new Date(),
              isFinal: true,
            },
          ])

          try {
            await vapi.stop()
            pendingToolCallsRef.current = []
            setCallStatus('ended')
          } catch (err) {
            console.error('Failed to auto-end call:', err)
          } finally {
            clearSilenceTimers()
          }
        }, 5000)
      }, 15000)
    }

    const recordUserActivity = () => {
      clearSilenceTimers()
      silenceWarnedRef.current = false
      if (callStatusRef.current === 'active') {
        scheduleSilenceTimers()
      }
    }

    // Call started
    const handleCallStart = () => {
      console.log('Call started')
      setCallStatus('active')
      setMetrics((prev) => ({
        ...prev,
        startTime: new Date(),
      }))
      pendingToolCallsRef.current = []
      setAgentState(DEFAULT_AGENT_STATE)
      setError(null)
      scheduleSilenceTimers()
    }

    // Call ended
    const handleCallEnd = () => {
      console.log('Call ended')
      setCallStatus('ended')
      setMetrics((prev) => ({
        ...prev,
        endTime: new Date(),
      }))
      clearSilenceTimers()
    }

    // Speech started (user speaking)
    const handleSpeechStart = (event?: any) => {
      if (event?.role && event.role !== 'user') return
      console.log('User started speaking')
      recordUserActivity()
    }

    // Speech ended (user stopped speaking)
    const handleSpeechEnd = () => {
      console.log('User stopped speaking')
    }

    // Volume level updates
    const handleVolumeLevel = (volume: number) => {
      // Can be used for visual indicators
    }

    // Transcript updates
    const appendToolCallsToLastAssistant = (toolCalls: ToolCall[]) => {
      if (toolCalls.length === 0) return

      setMessages((prev) => {
        for (let i = prev.length - 1; i >= 0; i -= 1) {
          if (prev[i].role === 'assistant') {
            const updated = [...prev]
            updated[i] = {
              ...updated[i],
              toolCalls: [...(updated[i].toolCalls || []), ...toolCalls],
            }
            return updated
          }
        }
        // No assistant message yet; keep them queued
        pendingToolCallsRef.current.push(...toolCalls)
        return prev
      })
    }

    const handleMessage = (message: any) => {
      console.log('Message received:', message)

      const agentStatePatch = extractAgentStateFromMessage(message)
      if (agentStatePatch) {
        setAgentState((prev) => ({
          ...prev,
          ...agentStatePatch,
        }))
      }

      if (typeof message.type === 'string' && message.type.startsWith('transcript')) {
        if (message.role === 'user') {
          recordUserActivity()
        }
        const transcriptType =
          message.transcriptType ||
          (message.type.includes('final') ? 'final' : 'partial')
        const isFinal =
          typeof message.isFinal === 'boolean' ? message.isFinal : transcriptType === 'final'
        const content = message.transcript || message.transcriptText || ''

        setMessages((prev) => {
          const nextMessage: TranscriptMessage = {
            role: message.role,
            content,
            timestamp: new Date(),
            isFinal,
          }

          const lastIdx = (() => {
            for (let i = prev.length - 1; i >= 0; i -= 1) {
              if (prev[i].role === nextMessage.role) return i
            }
            return -1
          })()

          const attachToolCalls = (existing?: TranscriptMessage) => {
            if (nextMessage.role !== 'assistant') return existing?.toolCalls
            if (pendingToolCallsRef.current.length === 0) return existing?.toolCalls
            const merged = [...(existing?.toolCalls || []), ...pendingToolCallsRef.current]
            pendingToolCallsRef.current = []
            return merged
          }

          if (lastIdx >= 0 && shouldMergeTranscript(prev[lastIdx], nextMessage)) {
            const updated = [...prev]
            const previous = prev[lastIdx]
            const mergedContent =
              nextMessage.content.length >= previous.content.length
                ? nextMessage.content
                : previous.content

            const mergedIsFinal = previous.isFinal === true || isFinal

            updated[lastIdx] = {
              ...previous,
              content: mergedContent,
              timestamp: nextMessage.timestamp,
              isFinal: mergedIsFinal,
              toolCalls: attachToolCalls(previous),
            }
            return updated
          }

          nextMessage.toolCalls = attachToolCalls()
          return [...prev, nextMessage]
        })
      }

      // Handle function calls (tool usage)
      if (message.type === 'function-call') {
        console.log('Function called:', message.functionCall)
        appendToolCallsToLastAssistant([
          {
            id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
            name: message.functionCall.name,
            arguments: message.functionCall.parameters,
          },
        ])
      }

      if (message.type === 'tool-calls' && Array.isArray(message.toolCallList)) {
        appendToolCallsToLastAssistant(
          message.toolCallList.map((toolCall: any, idx: number) => ({
            id: toolCall.id || `${Date.now()}-${idx}`,
            name: toolCall.name,
            arguments: toolCall.arguments || toolCall.parameters || {},
          }))
        )
      }
    }

    // Error handling
    const handleError = (error: any) => {
      setError(sanitizeError(error, 'Vapi Runtime Error'))
      setCallStatus('error')
    }

    // Register event listeners
    vapi.on('call-start', handleCallStart)
    vapi.on('call-end', handleCallEnd)
    vapi.on('speech-start', handleSpeechStart)
    vapi.on('speech-end', handleSpeechEnd)
    vapi.on('volume-level', handleVolumeLevel)
    vapi.on('message', handleMessage)
    vapi.on('error', handleError)

    // Cleanup
    return () => {
      vapi.off('call-start', handleCallStart)
      vapi.off('call-end', handleCallEnd)
      vapi.off('speech-start', handleSpeechStart)
      vapi.off('speech-end', handleSpeechEnd)
      vapi.off('volume-level', handleVolumeLevel)
      vapi.off('message', handleMessage)
      vapi.off('error', handleError)
      clearSilenceTimers()
    }
  }, [vapi])

  // Start call function
  const startCall = useCallback(async () => {
    if (!vapi) {
      setError('Voice client not initialized')
      return
    }

    const assistantId = process.env.NEXT_PUBLIC_VAPI_ASSISTANT_ID

    if (!assistantId) {
      setError(sanitizeError(new Error('Assistant configuration missing'), 'Start Call'))
      return
    }

    try {
      setCallStatus('loading')
      setMessages([])
      pendingToolCallsRef.current = []
      setAgentState(DEFAULT_AGENT_STATE)
      setError(null)

      await vapi.start(assistantId)

      // Initial greeting message
      setMessages([
        {
          role: 'assistant',
          content: getGreetingMessage(),
          timestamp: new Date(),
          isFinal: true,
        },
      ])
    } catch (err: any) {
      setError(sanitizeError(err, 'Start Call'))
      setCallStatus('error')
    }
  }, [vapi])

  // Stop call function
  const stopCall = useCallback(async () => {
    if (!vapi) return

    try {
      await vapi.stop()
      pendingToolCallsRef.current = []
      if (silenceWarningTimeoutRef.current) {
        clearTimeout(silenceWarningTimeoutRef.current)
        silenceWarningTimeoutRef.current = null
      }
      if (silenceHangupTimeoutRef.current) {
        clearTimeout(silenceHangupTimeoutRef.current)
        silenceHangupTimeoutRef.current = null
      }
      setCallStatus('ended')
    } catch (err) {
      console.error('Failed to stop call:', err)
    }
  }, [vapi])

  // Clear messages
  const clearMessages = useCallback(() => {
    setMessages([])
    pendingToolCallsRef.current = []
    if (silenceWarningTimeoutRef.current) {
      clearTimeout(silenceWarningTimeoutRef.current)
      silenceWarningTimeoutRef.current = null
    }
    if (silenceHangupTimeoutRef.current) {
      clearTimeout(silenceHangupTimeoutRef.current)
      silenceHangupTimeoutRef.current = null
    }
    setMetrics({
      duration: 0,
      startTime: null,
      endTime: null,
      messageCount: 0,
    })
  }, [])

  return {
    callStatus,
    messages,
    agentState,
    metrics,
    error,
    startCall,
    stopCall,
    clearMessages,
    isCallActive: callStatus === 'active',
    isCallLoading: callStatus === 'loading',
  }
}
