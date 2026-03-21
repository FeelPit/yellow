'use client'

import { useEffect, useState, useRef } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { apiClient, DirectMessage } from '@/lib/api'
import UserProfileModal from '@/components/UserProfileModal'
import ChatAdvisor from '@/components/ChatAdvisor'

export default function ChatPage() {
  const router = useRouter()
  const params = useParams()
  const conversationId = params.id as string

  const [messages, setMessages] = useState<DirectMessage[]>([])
  const [otherUsername, setOtherUsername] = useState('')
  const [otherUserId, setOtherUserId] = useState('')
  const [currentUserId, setCurrentUserId] = useState('')
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [loading, setLoading] = useState(true)
  const [showProfile, setShowProfile] = useState(false)
  const [icebreaker, setIcebreaker] = useState<string | null>(null)
  const [icebreakerLoading, setIcebreakerLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const init = async () => {
      try {
        const token = localStorage.getItem('yellow_token')
        if (!token) {
          router.push('/assistant')
          return
        }
        apiClient.setToken(token)

        const user = await apiClient.getCurrentUser()
        setCurrentUserId(user.id)

        const convs = await apiClient.listConversations()
        const conv = convs.find((c) => c.id === conversationId)
        if (conv) {
          setOtherUsername(conv.other_username)
          setOtherUserId(conv.other_user_id)
        }

        const msgs = await apiClient.getConversationMessages(conversationId)
        setMessages(msgs)

        if (msgs.length === 0) {
          setIcebreakerLoading(true)
          try {
            const res = await apiClient.askAdvisor(
              conversationId,
              'Suggest one great opening message I could send. Give me just the message text, nothing else — no quotes, no explanation.'
            )
            setIcebreaker(res.answer)
          } catch {
            setIcebreaker(null)
          } finally {
            setIcebreakerLoading(false)
          }
        }
      } catch {
        router.push('/conversations')
      } finally {
        setLoading(false)
      }
    }
    init()
  }, [router, conversationId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || sending) return
    const text = input.trim()
    setInput('')
    setSending(true)

    try {
      const msg = await apiClient.sendDirectMessage(conversationId, text)
      setMessages((prev) => [...prev, msg])
    } catch (err: any) {
      console.error('Send error:', err)
      setInput(text)
    } finally {
      setSending(false)
    }
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
    <div className="h-screen bg-white flex flex-col">
      <header className="h-14 px-4 md:px-6 flex items-center justify-between border-b border-neutral-100 shrink-0">
        <div className="flex items-center gap-2 md:gap-3 min-w-0">
          <button
            onClick={() => router.push('/conversations')}
            className="text-xs text-neutral-400 hover:text-neutral-600 transition-colors shrink-0"
          >
            ←
          </button>
          <span className="text-sm font-semibold text-neutral-900 truncate">{otherUsername}</span>
        </div>
        {otherUserId && (
          <button
            onClick={() => setShowProfile(true)}
            className="h-8 px-2.5 md:px-3 rounded-lg text-xs font-medium border border-neutral-200 text-neutral-600 hover:bg-neutral-50 transition-colors shrink-0"
          >
            Profile
          </button>
        )}
      </header>

      <div className="flex-1 overflow-y-auto px-4 md:px-6 py-4 scrollbar-hidden">
        {messages.length === 0 && (
          <div className="max-w-sm mx-auto mt-10">
            <div className="text-center mb-5">
              <div
                className="inline-flex items-center justify-center w-10 h-10 rounded-full mb-3"
                style={{ backgroundColor: '#FDB81320' }}
              >
                <span className="text-lg">💬</span>
              </div>
              <p className="text-xs text-neutral-400">
                Start a conversation with {otherUsername}
              </p>
            </div>

            {icebreakerLoading && (
              <div className="rounded-xl border border-neutral-100 p-4 text-center">
                <div className="flex items-center justify-center gap-2">
                  <div
                    className="w-4 h-4 rounded-full border-2 border-t-transparent animate-spin"
                    style={{ borderColor: '#FDB813', borderTopColor: 'transparent' }}
                  />
                  <span className="text-xs text-neutral-400">Yellow is thinking of an opener...</span>
                </div>
              </div>
            )}

            {icebreaker && !icebreakerLoading && (
              <button
                onClick={() => {
                  setInput(icebreaker)
                  setIcebreaker(null)
                }}
                className="w-full text-left rounded-xl border border-neutral-100 p-4 hover:border-neutral-200 hover:shadow-sm transition-all group"
              >
                <div className="flex items-center gap-1.5 mb-2">
                  <div
                    className="w-4 h-4 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: '#FDB813' }}
                  >
                    <span className="text-[8px] font-bold text-white">Y</span>
                  </div>
                  <span className="text-[10px] font-semibold text-neutral-400 uppercase tracking-wider">
                    Suggested opener
                  </span>
                </div>
                <p className="text-sm text-neutral-700 leading-relaxed">
                  {icebreaker}
                </p>
                <p className="text-[10px] text-neutral-300 mt-2 group-hover:text-neutral-400 transition-colors">
                  Tap to use this message
                </p>
              </button>
            )}
          </div>
        )}

        <div className="space-y-3 max-w-xl mx-auto">
          {messages.map((msg) => {
            const isMine = msg.sender_id === currentUserId
            return (
              <div
                key={msg.id}
                className={`flex ${isMine ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[75%] px-3.5 py-2.5 text-sm leading-relaxed ${
                    isMine
                      ? 'rounded-2xl rounded-br-md text-neutral-900'
                      : 'rounded-2xl rounded-bl-md text-neutral-800'
                  }`}
                  style={{
                    backgroundColor: isMine ? '#FDB813' : '#F5F5F5',
                  }}
                >
                  {msg.content}
                </div>
              </div>
            )
          })}
          <div ref={bottomRef} />
        </div>
      </div>

      <div className="px-4 md:px-6 py-3 border-t border-neutral-100 shrink-0">
        <div className="max-w-xl mx-auto flex items-center gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type a message..."
            className="flex-1 h-10 px-4 rounded-xl bg-neutral-50 text-sm text-neutral-800 placeholder-neutral-400 outline-none focus:ring-1 focus:ring-neutral-200"
            data-testid="dm-input"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || sending}
            className="w-10 h-10 rounded-xl flex items-center justify-center transition-all hover:brightness-105 active:scale-95 disabled:opacity-40"
            style={{ backgroundColor: '#FDB813' }}
            data-testid="dm-send"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="black" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </div>
      </div>

      {showProfile && otherUserId && (
        <UserProfileModal
          userId={otherUserId}
          username={otherUsername}
          onClose={() => setShowProfile(false)}
        />
      )}

      <ChatAdvisor conversationId={conversationId} />
    </div>
  )
}
