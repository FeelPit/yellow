'use client'

import { useState, useEffect, useRef } from 'react'
import posthog from 'posthog-js'
import { apiClient, Message, ProfileSnapshot, ProfileViewData, UserResponse } from '@/lib/api'
import ChatMessage from '@/components/ChatMessage'
import ChatInput from '@/components/ChatInput'
import ProfilePanel from '@/components/ProfilePanel'
import ProfileView from '@/components/ProfileView'
import PhotoManager from '@/components/PhotoManager'
import AuthForm from '@/components/AuthForm'
import ProfileComplete from '@/components/ProfileComplete'

export default function AssistantPage() {
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login')
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [currentUser, setCurrentUser] = useState<UserResponse | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [profileSnapshot, setProfileSnapshot] = useState<ProfileSnapshot | null>(null)
  const [profileReady, setProfileReady] = useState(false)
  const [loading, setLoading] = useState(false)
  const [authLoading, setAuthLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showThinking, setShowThinking] = useState(true)
  const [showPhotoManager, setShowPhotoManager] = useState(false)
  const [profileViewData, setProfileViewData] = useState<ProfileViewData | null>(null)
  const [profileAge, setProfileAge] = useState<number | null>(null)
  const [mobilePanel, setMobilePanel] = useState(false)
  const [showProfileComplete, setShowProfileComplete] = useState(false)
  const prevProfileReady = useRef(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('yellow_token')
      if (token) {
        apiClient.setToken(token)
        try {
          const user = await apiClient.getCurrentUser()
          setCurrentUser(user)
          setIsAuthenticated(true)
          posthog.identify(user.id, { email: user.email, username: user.username })
          await initSession()
        } catch (err) {
          localStorage.removeItem('yellow_token')
          apiClient.setToken(null)
        }
      }
      setAuthLoading(false)
    }

    checkAuth()
  }, [])

  const initSession = async () => {
    try {
      setLoading(true)
      setError(null)

      const sessionResponse = await apiClient.getOrCreateSession()
      setSessionId(sessionResponse.session_id)

      if (sessionResponse.status === 'existing') {
        const messagesResponse = await apiClient.getMessages(sessionResponse.session_id)
        setMessages(messagesResponse)

        try {
          const profileData = await apiClient.getProfile(sessionResponse.session_id)
          if (profileData) {
            const filledTraits = profileData.metrics
              ? Object.values(profileData.metrics).filter((v) => v !== null).length
              : 0
            const estimatedReadiness = Math.min(100, Math.max(filledTraits * 12, 0))
            const isReady = estimatedReadiness >= 85 ||
              (profileData.values && profileData.communication_style) ||
              filledTraits >= 7

            setProfileSnapshot({
              age: profileData.age ?? null,
              gender: profileData.gender ?? null,
              metrics: profileData.metrics,
              communication_style: profileData.communication_style,
              attachment_style: profileData.attachment_style,
              partner_preferences: profileData.partner_preferences,
              values: profileData.values,
              profile_readiness: estimatedReadiness,
            })
            setProfileAge(profileData.age ?? null)
            if (isReady) {
              setProfileReady(true)
              prevProfileReady.current = true
            }
          }
        } catch (err) {
          // Profile not ready yet
        }
      } else {
        const conversationResponse = await apiClient.startConversation(
          sessionResponse.session_id
        )
        setMessages(conversationResponse.messages)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const handleAuth = async (data: { email: string; username?: string; password: string }) => {
    try {
      setError(null)
      let tokenResponse

      if (authMode === 'register') {
        tokenResponse = await apiClient.register({
          email: data.email,
          username: data.username!,
          password: data.password,
        })
      } else {
        tokenResponse = await apiClient.login({
          email: data.email,
          password: data.password,
        })
      }

      localStorage.setItem('yellow_token', tokenResponse.access_token)
      apiClient.setToken(tokenResponse.access_token)

      const user = await apiClient.getCurrentUser()
      setCurrentUser(user)
      setIsAuthenticated(true)
      posthog.identify(user.id, { email: data.email, username: user.username })

      await initSession()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed')
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('yellow_token')
    apiClient.setToken(null)
    posthog.reset()
    setIsAuthenticated(false)
    setCurrentUser(null)
    setSessionId(null)
    setMessages([])
    setProfileSnapshot(null)
    setProfileReady(false)
  }

  const handleSendMessage = async (content: string) => {
    if (!sessionId || !content.trim()) return

    const optimisticUserMsg: Message = {
      id: crypto.randomUUID(),
      session_id: sessionId,
      role: 'user',
      content: content.trim(),
      created_at: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, optimisticUserMsg])

    try {
      setSending(true)
      setError(null)

      const response = await apiClient.sendMessage(sessionId, content)

      setMessages((prev) => {
        const withoutOptimistic = prev.filter((m) => m.id !== optimisticUserMsg.id)
        return [...withoutOptimistic, response.user_message, response.assistant_message]
      })

      if (response.profile_snapshot) {
        setProfileSnapshot(response.profile_snapshot)
        if (response.profile_snapshot.age) {
          setProfileAge(response.profile_snapshot.age)
        }
      }

      const isReady = response.profile_ready ||
        (response.profile_snapshot?.profile_readiness != null && response.profile_snapshot.profile_readiness >= 85)

      if (isReady && !prevProfileReady.current) {
        setProfileReady(true)
        const alreadySeen = localStorage.getItem('yellow_profile_complete_seen')
        if (!alreadySeen) {
          setShowProfileComplete(true)
        }
        prevProfileReady.current = true
      }

      if (response.intent === 'photo_manage') {
        setShowPhotoManager(true)
      }

      if (response.intent === 'view_profile' && response.profile_view) {
        setProfileViewData(response.profile_view)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message')
    } finally {
      setSending(false)
    }
  }

  const handlePhotoUpload = async (file: File) => {
    if (!sessionId) return
    try {
      setSending(true)
      setError(null)
      const result = await apiClient.uploadPhoto(file)
      const botMessage: Message = {
        id: crypto.randomUUID(),
        session_id: sessionId,
        role: 'assistant',
        content: result.message,
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, botMessage])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload photo')
    } finally {
      setSending(false)
    }
  }

  if (authLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div
          className="w-8 h-8 rounded-full border-2 border-t-transparent animate-spin"
          style={{ borderColor: '#FDB813', borderTopColor: 'transparent' }}
        />
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <AuthForm
        mode={authMode}
        onSubmit={handleAuth}
        onToggleMode={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}
        loading={loading}
        error={error}
      />
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div
          className="w-8 h-8 rounded-full border-2 border-t-transparent animate-spin"
          style={{ borderColor: '#FDB813', borderTopColor: 'transparent' }}
        />
      </div>
    )
  }

  return (
    <div className="h-screen bg-white flex flex-col md:flex-row">
      {/* Main chat area */}
      <div className="flex-1 flex flex-col min-w-0 min-h-0">
        <header className="h-14 px-4 md:px-5 flex items-center justify-between border-b border-neutral-100 shrink-0">
          <div className="flex items-center gap-2 md:gap-3">
            <div
              className="w-7 h-7 rounded-lg flex items-center justify-center"
              style={{ backgroundColor: '#FDB813' }}
            >
              <span className="text-white text-xs font-bold">Y</span>
            </div>
            <span className="text-sm text-neutral-400 truncate">@{currentUser?.username}</span>
          </div>

          <div className="flex items-center gap-0.5 md:gap-1">
            <button
              onClick={() => setShowThinking(!showThinking)}
              className={`h-8 px-2 md:px-3 rounded-lg text-xs font-medium transition-colors ${
                showThinking
                  ? 'text-amber-600 bg-amber-50'
                  : 'text-neutral-400 hover:bg-neutral-50'
              }`}
              title={showThinking ? 'Hide AI thinking' : 'Show AI thinking'}
            >
              {showThinking ? '🧠' : '🧠'}
            </button>

            {/* Mobile profile toggle */}
            <button
              onClick={() => setMobilePanel(!mobilePanel)}
              className="md:hidden h-8 px-2 rounded-lg text-xs font-medium text-neutral-400 hover:bg-neutral-50 transition-colors"
              title="Profile"
            >
              👤
            </button>

            {profileReady && (
              <a
                href="/matches"
                className="h-8 px-2 md:px-3 rounded-lg text-xs font-medium flex items-center transition-colors hover:bg-neutral-50"
                style={{ color: '#FDB813' }}
              >
                <span className="hidden sm:inline">Matches</span>
                <span className="sm:hidden">💛</span>
              </a>
            )}

            <button
              onClick={handleLogout}
              className="h-8 px-2 md:px-3 rounded-lg text-xs text-neutral-400 hover:text-neutral-600 hover:bg-neutral-50 transition-colors"
            >
              <span className="hidden sm:inline">Log out</span>
              <span className="sm:hidden">↗</span>
            </button>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 md:px-5 py-4 md:py-6 scrollbar-hidden">
          <div className="max-w-2xl mx-auto">
            {messages.map((message, idx) => (
              <div key={message.id}>
                <ChatMessage
                  message={message}
                  showThinking={showThinking}
                />
                {profileViewData && message.role === 'assistant' && idx === messages.length - 1 && message.content.includes("Here's how your profile looks") && (
                  <ProfileView data={profileViewData} apiBaseUrl={process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'} />
                )}
              </div>
            ))}
            {sending && (
              <div className="flex justify-start mb-4 animate-fade-in">
                <div className="bg-neutral-100 rounded-2xl rounded-bl-md px-4 py-3 flex items-center gap-1">
                  <span className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input */}
        <div className="px-4 md:px-5 py-3 md:py-4 border-t border-neutral-100 shrink-0">
          <div className="max-w-2xl mx-auto">
            <ChatInput
              onSend={handleSendMessage}
              onPhotoUpload={handlePhotoUpload}
              disabled={sending || !sessionId}
            />
          </div>
        </div>

        <PhotoManager
          isOpen={showPhotoManager}
          onClose={() => setShowPhotoManager(false)}
        />
      </div>

      {/* Profile sidebar — desktop */}
      <aside className="hidden md:block w-72 border-l border-neutral-100 overflow-y-auto shrink-0 bg-white">
        <ProfilePanel snapshot={profileSnapshot} username={currentUser?.username} age={profileAge} />
      </aside>

      {/* Profile panel — mobile slide-up */}
      {mobilePanel && (
        <div className="md:hidden fixed inset-0 z-50 flex flex-col">
          <div className="flex-1 bg-black/30" onClick={() => setMobilePanel(false)} />
          <div className="bg-white rounded-t-2xl max-h-[75vh] overflow-y-auto animate-slide-up">
            <div className="flex items-center justify-between px-4 py-3 border-b border-neutral-100 sticky top-0 bg-white z-10">
              <span className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">Profile</span>
              <button
                onClick={() => setMobilePanel(false)}
                className="w-7 h-7 rounded-full bg-neutral-100 flex items-center justify-center text-neutral-400 text-xs"
              >
                ✕
              </button>
            </div>
            <ProfilePanel snapshot={profileSnapshot} username={currentUser?.username} age={profileAge} />
          </div>
        </div>
      )}

      {showProfileComplete && profileSnapshot && (
        <ProfileComplete
          snapshot={profileSnapshot}
          onDismiss={() => setShowProfileComplete(false)}
        />
      )}
    </div>
  )
}
