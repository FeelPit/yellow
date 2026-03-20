'use client'

import { useState, useEffect, useRef } from 'react'
import { apiClient, Message, ProfileSnapshot, ProfileViewData, UserResponse } from '@/lib/api'
import ChatMessage from '@/components/ChatMessage'
import ChatInput from '@/components/ChatInput'
import ProfilePanel from '@/components/ProfilePanel'
import ProfileView from '@/components/ProfileView'
import PhotoManager from '@/components/PhotoManager'
import AuthForm from '@/components/AuthForm'

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
            setProfileSnapshot({
              age: profileData.age ?? null,
              gender: profileData.gender ?? null,
              metrics: profileData.metrics,
              communication_style: profileData.communication_style,
              attachment_style: profileData.attachment_style,
              partner_preferences: profileData.partner_preferences,
              values: profileData.values,
            })
            setProfileAge(profileData.age ?? null)
            if (profileData.values && profileData.communication_style) {
              setProfileReady(true)
            }
          }
        } catch (err) {
          // Profile not ready yet — that's fine
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

      await initSession()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed')
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('yellow_token')
    apiClient.setToken(null)
    setIsAuthenticated(false)
    setCurrentUser(null)
    setSessionId(null)
    setMessages([])
    setProfileSnapshot(null)
    setProfileReady(false)
  }

  const handleSendMessage = async (content: string) => {
    if (!sessionId || !content.trim()) return

    try {
      setSending(true)
      setError(null)

      const response = await apiClient.sendMessage(sessionId, content)

      setMessages((prev) => [
        ...prev,
        response.user_message,
        response.assistant_message,
      ])

      if (response.profile_snapshot) {
        setProfileSnapshot(response.profile_snapshot)
        if (response.profile_snapshot.age) {
          setProfileAge(response.profile_snapshot.age)
        }
      }

      if (response.profile_ready) {
        setProfileReady(true)
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
    <div className="h-screen bg-white flex">
      {/* Main chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-14 px-5 flex items-center justify-between border-b border-neutral-100 shrink-0">
          <div className="flex items-center gap-3">
            <div
              className="w-7 h-7 rounded-lg flex items-center justify-center"
              style={{ backgroundColor: '#FDB813' }}
            >
              <span className="text-white text-xs font-bold">Y</span>
            </div>
            <span className="text-sm text-neutral-400">@{currentUser?.username}</span>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={() => setShowThinking(!showThinking)}
              className={`h-8 px-3 rounded-lg text-xs font-medium transition-colors ${
                showThinking
                  ? 'text-amber-600 bg-amber-50'
                  : 'text-neutral-400 hover:bg-neutral-50'
              }`}
              title={showThinking ? 'Hide AI thinking' : 'Show AI thinking'}
            >
              {showThinking ? '🧠 Thinking' : '🧠'}
            </button>

            {profileReady && (
              <a
                href="/matches"
                className="h-8 px-3 rounded-lg text-xs font-medium flex items-center transition-colors hover:bg-neutral-50"
                style={{ color: '#FDB813' }}
              >
                Matches
              </a>
            )}

            <button
              onClick={handleLogout}
              className="h-8 px-3 rounded-lg text-xs text-neutral-400 hover:text-neutral-600 hover:bg-neutral-50 transition-colors"
            >
              Log out
            </button>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-5 py-6 scrollbar-hidden">
          <div className="max-w-2xl mx-auto">
            {messages.map((message, idx) => (
              <div key={message.id}>
                <ChatMessage
                  message={message}
                  showThinking={showThinking}
                />
                {/* Show profile view inline right after the view_profile response */}
                {profileViewData && message.role === 'assistant' && idx === messages.length - 1 && message.content.includes("Here's how your profile looks") && (
                  <ProfileView data={profileViewData} apiBaseUrl={process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'} />
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input */}
        <div className="px-5 py-4 border-t border-neutral-100 shrink-0">
          <div className="max-w-2xl mx-auto">
            <ChatInput
              onSend={handleSendMessage}
              onPhotoUpload={handlePhotoUpload}
              disabled={sending || !sessionId}
            />
          </div>
        </div>

        {/* Photo Manager Modal */}
        <PhotoManager
          isOpen={showPhotoManager}
          onClose={() => setShowPhotoManager(false)}
        />
      </div>

      {/* Profile sidebar — always visible */}
      <aside className="w-72 border-l border-neutral-100 overflow-y-auto shrink-0 bg-white">
        <ProfilePanel snapshot={profileSnapshot} username={currentUser?.username} age={profileAge} />
      </aside>
    </div>
  )
}
