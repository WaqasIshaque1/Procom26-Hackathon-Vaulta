'use client'

import { useRef, useState, useEffect } from 'react' // cleaned up imports
import {
  Activity,
  ArrowLeft,
  Loader2,
  Mic,
  MicOff,
  Moon,
  Phone,
  PhoneOff,
  ShieldCheck,
  Sparkles,
  Sun,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useVapiClient } from '@/hooks/useVapiClient'
import { format } from 'date-fns'
import { cn } from '@/lib/utils'
import { useRouter } from 'next/navigation'
import DashboardLogo from '@/components/ui/DashboardLogo'

/**
 * Main Voice Agent Interface Component
 * Displays the voice call interface with transcript, status, and controls
 * Integrates with Vapi.ai for real-time voice communication
 */
export default function VoiceAgentInterface() {
  const router = useRouter()
  const {
    callStatus,
    messages,
    agentState,
    metrics,
    error,
    startCall,
    stopCall,
    isCallActive,
    isCallLoading,
  } = useVapiClient()

  const scrollRef = useRef<HTMLDivElement>(null)
  const [isDark, setIsDark] = useState(false)
  const [micPermission, setMicPermission] = useState<'granted' | 'denied' | 'prompt' | 'unknown'>('unknown')
  const [showPermissionError, setShowPermissionError] = useState(false)
  const [showFinalOnly, setShowFinalOnly] = useState(false)

  useEffect(() => {
    if (typeof window === 'undefined') return
    const root = document.documentElement
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    const initial = root.classList.contains('dark') || prefersDark
    root.classList.toggle('dark', initial)
    setIsDark(initial)

    checkMicPermission()
  }, [])

  // Clear error when permission is granted
  useEffect(() => {
    if (micPermission === 'granted') {
      setShowPermissionError(false)
    }
  }, [micPermission])

  const checkMicPermission = async () => {
    try {
      if (navigator.permissions && navigator.permissions.query) {
        const result = await navigator.permissions.query({ name: 'microphone' as any })
        setMicPermission(result.state as any)

        result.onchange = () => {
          setMicPermission(result.state as any)
        }
      } else {
        // Fallback for browsers not supporting permissions API
        setMicPermission('prompt')
      }
    } catch (err) {
      console.warn('Permission query failed', err)
      setMicPermission('prompt')
    }
  }

  const requestMicPermission = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      stream.getTracks().forEach(track => track.stop())
      setMicPermission('granted')
      setShowPermissionError(false)
    } catch (err) {
      console.error('Permission denied', err)
      setMicPermission('denied')
    }
  }

  const handleStartCall = () => {
    if (micPermission !== 'granted') {
      setShowPermissionError(true)
      // Attempt to request if not explicitly denied (though user might need to retry manually if 'denied')
      if (micPermission === 'prompt' || micPermission === 'unknown') {
        requestMicPermission()
      }
      return
    }
    setShowPermissionError(false)
    startCall()
  }

  const toggleTheme = () => {
    setIsDark((prev) => {
      const next = !prev
      document.documentElement.classList.toggle('dark', next)
      return next
    })
  }

  // Auto-scroll to latest message
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  // Format flow name for display
  const formatFlowName = (flow: string | null) => {
    if (!flow) return null
    return flow.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())
  }

  const statusConfig = {
    active: {
      label: 'Live session',
      badge: 'bg-indigo-500 text-white border-indigo-500 dark:bg-indigo-500/90',
    },
    loading: {
      label: 'Connecting',
      badge: 'bg-amber-100 text-amber-900 border-amber-200 dark:bg-amber-500/20 dark:text-amber-100 dark:border-amber-500/40',
    },
    ended: {
      label: 'Call ended',
      badge: 'bg-gray-200 text-gray-700 border-gray-200 dark:bg-gray-800 dark:text-gray-200 dark:border-gray-700',
    },
    error: {
      label: 'Needs attention',
      badge: 'bg-rose-500 text-white border-rose-500 dark:bg-rose-500/90',
    },
    inactive: {
      label: 'Ready',
      badge: 'bg-gray-100 text-gray-700 border-gray-200 dark:bg-gray-800 dark:text-gray-200 dark:border-gray-700',
    },
  } as const

  const status = statusConfig[callStatus] ?? statusConfig.inactive
  const visibleMessages = showFinalOnly
    ? messages.filter((msg) => msg.isFinal !== false)
    : messages

  return (
    <div className="relative min-h-screen overflow-hidden bg-gray-950 text-foreground">
      <div className="pointer-events-none absolute inset-0">
        <div
          className="absolute -top-32 right-0 h-[420px] w-[420px] rounded-full bg-gradient-to-br from-indigo-200/70 via-indigo-300/70 to-transparent blur-3xl motion-safe:animate-float dark:from-indigo-900/50 dark:via-indigo-800/40"
          style={{ animationDelay: '0.2s' }}
        />
        <div
          className="absolute top-1/2 -left-24 h-[380px] w-[380px] rounded-full bg-gradient-to-tr from-gray-200/70 via-indigo-200/50 to-transparent blur-3xl motion-safe:animate-float dark:from-gray-900/50 dark:via-indigo-900/40"
          style={{ animationDelay: '0.6s' }}
        />
        <div
          className="absolute bottom-0 right-0 h-[320px] w-[320px] rounded-full bg-gradient-to-tr from-indigo-300/70 via-indigo-200/50 to-transparent blur-3xl motion-safe:animate-float dark:from-indigo-900/50 dark:via-indigo-800/40"
          style={{ animationDelay: '1s' }}
        />
      </div>

      <div className="relative mx-auto flex max-w-6xl flex-col gap-4 sm:gap-8 px-3 pb-8 pt-6 sm:px-4 sm:pb-12 sm:pt-14 motion-safe:animate-fade-in">
        <div className="absolute left-3 top-3 z-30 sm:left-4 sm:top-4">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => {
              sessionStorage.removeItem('intro_gate_passed')
              window.location.reload()
            }}
            className="group flex items-center gap-2 text-indigo-200/65 hover:text-white hover:bg-white/10"
          >
            <ArrowLeft className="h-4 w-4 transition-transform group-hover:-translate-x-1" />
            <span className="hidden sm:inline">Back</span>
          </Button>
        </div>
        <div className="absolute right-3 top-3 z-30 sm:right-4 sm:top-4">
          <Button
            type="button"
            variant="outline"
            size="icon"
            onClick={toggleTheme}
            aria-pressed={isDark}
            aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
            className="h-9 w-9 rounded-full border-slate-200 bg-white/80 text-slate-700 shadow-sm hover:bg-white dark:border-slate-700 dark:bg-slate-900/70 dark:text-slate-100"
          >
            {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>
        </div>
        <header className="flex flex-col gap-4 sm:gap-6 md:flex-row md:items-end md:justify-between motion-safe:animate-fade-up">
          <div className="space-y-3 sm:space-y-4 w-full flex flex-col items-center text-center">
            <div className="flex items-center gap-3">
              <DashboardLogo />
              <div className="inline-flex items-center gap-2 rounded-full bg-white/70 px-2.5 py-1 sm:px-3 sm:py-1.5 text-[10px] sm:text-[11px] font-semibold uppercase tracking-[0.2em] text-indigo-900 shadow-sm ring-1 ring-indigo-200/60 dark:bg-gray-900/70 dark:text-indigo-100 dark:ring-indigo-800/60">
                <span className="h-1.5 w-1.5 sm:h-2 sm:w-2 rounded-full bg-indigo-500" />
                Always-On Security
              </div>
            </div>
            <div className="space-y-2">
              <h1 className="font-nacelle text-4xl font-semibold tracking-tight sm:text-6xl lg:text-7xl bg-gradient-to-br from-white via-indigo-100 to-indigo-400 bg-clip-text text-transparent">
                Vaulta Voice
              </h1>
              <p className="max-w-2xl text-xs sm:text-sm text-indigo-200/65 sm:text-base mx-auto">
                A future-ready voice banking experience with biometric verification, rapid issue routing, and a
                human-ready escalation path.
              </p>
            </div>
          </div>

        </header>

        <div className="grid gap-4 sm:gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <Card className="border-gray-800/80 bg-gray-900/70 shadow-xl shadow-indigo-900/20 backdrop-blur motion-safe:animate-fade-up">
            <CardHeader className="space-y-4 border-b border-gray-800/80 bg-gray-900/60">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <CardTitle className="text-base sm:text-lg font-semibold text-gray-200">
                    Live Transcript
                  </CardTitle>
                  <CardDescription className="text-[10px] sm:text-xs text-indigo-200/65">
                    Real-time voice exchange with structured actions and secure context.
                  </CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setShowFinalOnly((prev) => !prev)}
                    className={cn(
                      'inline-flex items-center gap-2 rounded-full border px-2.5 py-1 text-[10px] sm:text-xs font-semibold transition',
                      showFinalOnly
                        ? 'border-indigo-700/60 bg-indigo-500/20 text-indigo-100'
                        : 'border-gray-700 bg-gray-900/70 text-gray-200'
                    )}
                    aria-pressed={showFinalOnly}
                  >
                    {showFinalOnly ? 'Final Only' : 'Live + Final'}
                  </button>
                  <Badge className={cn('border text-[10px] sm:text-xs', status.badge)}>{status.label}</Badge>
                </div>
              </div>
              <div className="flex flex-wrap gap-2 text-[10px] sm:text-xs">
                {agentState.verified && (
                  <Badge className="border border-indigo-800/60 bg-indigo-500/20 text-indigo-100">
                    Identity Verified
                  </Badge>
                )}
                {agentState.currentFlow && (
                  <Badge className="border border-gray-700 bg-gray-900/70 text-gray-200">
                    Flow: {formatFlowName(agentState.currentFlow)}
                  </Badge>
                )}
                {agentState.escalate && (
                  <Badge className="border border-amber-200 bg-amber-50 text-amber-800 dark:border-amber-700/60 dark:bg-amber-500/20 dark:text-amber-100">
                    Escalation Requested
                  </Badge>
                )}
                {/* {metrics.startTime && (
                  //// TODO: Please show the customer message count
                  <Badge className="border border-slate-200 bg-white/90 text-slate-700 dark:border-slate-700 dark:bg-slate-900/70 dark:text-slate-200">
                    {metrics.messageCount} messages
                  </Badge>
                )} */}
              </div>
            </CardHeader>

            <CardContent className="p-0">
              <div
                className="h-[350px] overflow-y-auto px-3 py-4 sm:h-[520px] sm:px-6 motion-safe:animate-fade-in"
                ref={scrollRef}
              >
                {visibleMessages.length === 0 && !isCallActive && (
                  <div className="flex h-full flex-col items-center justify-center text-center text-indigo-200/65">
                    <div className="rounded-full bg-gray-900/70 p-3 sm:p-4 shadow-sm ring-1 ring-gray-700">
                      <Phone className="h-8 w-8 sm:h-10 sm:w-10 text-gray-400" />
                    </div>
                    <p className="mt-4 text-lg font-semibold text-gray-200">
                      Ready for a secure conversation
                    </p>
                    <p className="mt-2 max-w-sm text-sm text-indigo-200/65">
                      Start a call to see the live transcript, contextual actions, and trusted identity verification.
                    </p>
                    <div className="mt-6 grid w-full max-w-md gap-2 text-xs">
                      {[
                        'My card was stolen',
                        "What's my account balance?",
                        "I can't log into the mobile app",
                      ].map((prompt) => (
                        <div
                          key={prompt}
                          className="rounded-xl border border-gray-700 bg-gray-900/70 px-3 py-2 text-gray-200 shadow-sm"
                        >
                          “{prompt}”
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="space-y-4">
                  {visibleMessages.map((msg, idx) => {
                    const isUser = msg.role === 'user'
                    const isSystem = msg.role === 'system'

                    return (
                      <div
                        key={idx}
                        className={cn(
                          'flex motion-safe:animate-fade-up',
                          isUser ? 'justify-end' : 'justify-start'
                        )}
                      >
                        <div
                          className={cn(
                            'w-full max-w-[85%] rounded-2xl px-3 py-2 sm:px-4 sm:py-3 shadow-sm sm:max-w-[70%]',
                            isUser
                              ? 'bg-gradient-to-br from-indigo-600 via-indigo-600 to-indigo-500 text-white'
                              : isSystem
                                ? 'border border-gray-700 bg-gray-800/80 text-gray-100'
                                : 'border border-gray-700 bg-gray-900/80 text-gray-100'
                          )}
                        >
                          <div className="flex items-center justify-between text-[10px] sm:text-[11px] uppercase tracking-wide">
                            <span
                              className={cn(
                                'font-semibold',
                                isUser ? 'text-indigo-100' : 'text-gray-400'
                              )}
                            >
                              {isUser ? 'You' : isSystem ? 'System' : 'Vaulta'}
                            </span>
                            <span
                              className={cn(
                                isUser ? 'text-indigo-100' : 'text-gray-400'
                              )}
                            >
                              {format(msg.timestamp, 'HH:mm:ss')}
                            </span>
                          </div>
                          <p className="mt-1 sm:mt-2 whitespace-pre-wrap text-xs sm:text-sm leading-relaxed">
                            {msg.content}
                          </p>

                          {msg.toolCalls && msg.toolCalls.length > 0 && (
                            <div
                              className={cn(
                                'mt-2 sm:mt-3 border-t pt-1 sm:pt-2 text-[10px] sm:text-[11px]',
                                isUser
                                  ? 'border-white/30 text-indigo-50'
                                  : 'border-gray-700 text-gray-400'
                              )}
                            >
                              <span className="font-semibold">Tools:</span>{' '}
                              {msg.toolCalls.map((t) => t.name).join(', ')}
                            </div>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>

                {isCallLoading && (
                  <div className="flex items-center justify-center gap-2 py-8 text-xs sm:text-sm text-muted-foreground">
                    <Loader2 className="h-4 w-4 animate-spin text-indigo-500" />
                    Connecting to the voice network...
                  </div>
                )}
              </div>

              {error && (
                <div className="border-t border-rose-200 bg-rose-50 px-4 py-2 sm:px-6 sm:py-3 text-xs sm:text-sm text-rose-800 dark:border-rose-900/60 dark:bg-rose-500/20 dark:text-rose-100">
                  <span className="font-semibold">Error:</span> {error}
                </div>
              )}
            </CardContent>
          </Card>

          <div className="space-y-4 sm:space-y-6">
            <Card
              className="relative z-20 border-gray-800/80 bg-gray-900/70 shadow-lg shadow-indigo-900/20 backdrop-blur motion-safe:animate-fade-up"
              style={{ animationDelay: '0.1s' }}
            >
              <CardHeader className="space-y-2">
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <CardTitle className="text-base font-semibold text-gray-200">
                      Call Control
                    </CardTitle>
                    {/* Network indicator intentionally disabled for assessment scope/privacy. */}
                    {/* If you want IP/location-based misuse deterrence, re-enable the component */}
                    {/* and show it only after explicit user consent on call start. */}

                    {/* Microphone Status Icon */}
                    <div
                      className={cn(
                        "flex items-center justify-center h-8 w-8 rounded-full border transition-colors",
                        micPermission !== 'granted' && "cursor-pointer",
                        micPermission === 'granted'
                          ? "bg-indigo-500/20 border-indigo-700/60 text-indigo-300"
                          : "bg-red-500/20 border-red-700/60 text-red-300 animate-pulse"
                      )}
                      onClick={() => {
                        if (micPermission !== 'granted') requestMicPermission()
                      }}
                      title={micPermission === 'granted' ? "Microphone active" : "Click to enable microphone"}
                    >
                      {micPermission === 'granted' ? (
                        <Mic className="h-4 w-4" />
                      ) : (
                        <MicOff className="h-4 w-4" />
                      )}
                    </div>
                  </div>
                  <Badge className={cn('border text-xs', status.badge)}>{status.label}</Badge>
                </div>
                <CardDescription className="text-xs text-indigo-200/65">
                  Launch a secure session and watch live context updates as the conversation unfolds.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 sm:space-y-5">
                <div className="grid grid-cols-2 gap-3">
                  <div className="rounded-2xl border border-gray-700 bg-gray-800/80 px-3 py-2 sm:px-4 sm:py-3">
                    <p className="text-[10px] sm:text-[11px] uppercase tracking-wide text- text-indigo-200/65">Messages</p>
                    <p className="text-base sm:text-lg font-semibold text-gray-200">
                      {metrics.messageCount}
                    </p>
                  </div>
                  <div className="rounded-2xl border border-gray-700 bg-gray-800/80 px-3 py-2 sm:px-4 sm:py-3">
                    <p className="text-[10px] sm:text-[11px] uppercase tracking-wide text-indigo-200/65">Start Time</p>
                    <p className="text-sm font-semibold text-gray-200">
                      {metrics.startTime ? format(metrics.startTime, 'HH:mm') : '—'}
                    </p>
                  </div>
                </div>

                <div className="flex flex-col items-center justify-center gap-4">
                  {!isCallActive && callStatus !== 'loading' ? (
                    <div className="w-full space-y-2">
                      {showPermissionError && (
                        <div className="flex items-center justify-center gap-2 rounded-lg bg-red-500/20 p-2 text-xs font-medium text-red-300 motion-safe:animate-shake">
                          <MicOff className="h-3.5 w-3.5" />
                          Microphone permission is required for a voice call.
                        </div>
                      )}
                      <div className="relative w-full overflow-hidden rounded-lg p-[2px]">
                        {/* Meteor / Spinning Highlight Effect */}
                        {micPermission === 'granted' && (
                          <div className="absolute inset-[-1000%] animate-[spin_3s_linear_infinite] bg-[conic-gradient(from_90deg_at_50%_50%,#6366f1_0%,#6366f1_40%,#e0e7ff_50%,#6366f1_60%,#6366f1_100%)] opacity-100" />
                        )}

                        {/* Alternative: A cleaner "Searchlight" beam */}
                        {micPermission === 'granted' && (
                          <div className="absolute inset-[-1000%] animate-[spin_4s_linear_infinite] bg-[conic-gradient(from_90deg_at_50%_50%,transparent_0%,#FFFFFF_50%,transparent_100%)] opacity-30 mix-blend-overlay" />
                        )}

                        <Button
                          onClick={handleStartCall}
                          size="lg"
                          className={cn(
                            "relative z-10 w-full py-4 sm:py-6 text-base sm:text-lg text-white shadow-lg transition-all rounded-lg border border-white/10",
                            micPermission === 'granted'
                              ? "bg-indigo-600 hover:bg-indigo-700 shadow-indigo-900/60"
                              : "bg-gray-600 cursor-not-allowed opacity-70 hover:bg-gray-600"
                          )}
                          // We do NOT set disabled={true} here so that onClick can still fire to show the error
                          aria-disabled={micPermission !== 'granted'}
                        >
                          <Phone className="mr-2 h-5 w-5" />
                          Start Secure Call
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <Button
                      onClick={stopCall}
                      size="lg"
                      variant="destructive"
                      className="w-full py-4 sm:py-6 text-base sm:text-lg shadow-lg"
                      disabled={isCallLoading}
                    >
                      <PhoneOff className="mr-2 h-5 w-5" />
                      End Call
                    </Button>
                  )}

                  <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
                    {isCallActive && (
                      <>
                        <Mic className="h-4 w-4 text-indigo-500" />
                        <span className="font-medium text-indigo-300">Listening live</span>
                        <span className="text-gray-600">•</span>
                        Speak naturally
                      </>
                    )}
                    {isCallLoading && <span>Initializing voice connection...</span>}
                    {callStatus === 'ended' && <span>Call ended</span>}
                    {callStatus === 'inactive' && !error && <span>Ready to connect</span>}
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card
              className="relative z-10 border-gray-800/80 bg-gray-900/70 shadow-md backdrop-blur motion-safe:animate-fade-up"
              style={{ animationDelay: '0.2s' }}
            >
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold text-gray-200">
                  Session Snapshot
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-xs text-indigo-200/65">
                <div className="flex items-center justify-between">
                  <span>Status</span>
                  <span className="font-semibold text-gray-200">{callStatus}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Verified</span>
                  <span
                    className={cn(
                      'font-semibold',
                      agentState.verified
                        ? 'text-indigo-400'
                        : 'text-gray-500'
                    )}
                  >
                    {agentState.verified ? 'Yes' : 'No'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Verification Attempts</span>
                  <span className="font-semibold text-gray-200">
                    {agentState.verificationAttempts}
                  </span>
                </div>
                {agentState.customerId && (
                  <div className="flex items-center justify-between">
                    <span>Customer ID</span>
                    <span className="font-semibold text-gray-200">{agentState.customerId}</span>
                  </div>
                )}
                {metrics.startTime && (
                  <div className="flex items-center justify-between">
                    <span>Call Started</span>
                    <span className="font-semibold text-gray-200">
                      {format(metrics.startTime, 'MMM d, HH:mm')}
                    </span>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card
              className="border-gray-800/60 bg-gradient-to-br from-gray-900/80 via-gray-800/40 to-gray-900/80 shadow-md backdrop-blur motion-safe:animate-fade-up"
              style={{ animationDelay: '0.3s' }}
            >
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold text-gray-200">
                  Testing Instructions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-xs text-indigo-200/65">
                <p>
                  <span className="font-semibold">Test Credentials:</span> Customer ID{' '}
                  <code className="rounded bg-gray-800/60 px-1 py-0.5 text-indigo-300">1</code>, PIN{' '}
                  <code className="rounded bg-gray-800/60 px-1 py-0.5 text-indigo-300">1000</code>
                </p>
                <p>
                  <span className="font-semibold">Deep Flows:</span> “My card was stolen” or “What&apos;s my balance?”
                </p>
                <p>
                  <span className="font-semibold">Stub Flows:</span> “Can&apos;t login to app” or “I want to close my account”
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
