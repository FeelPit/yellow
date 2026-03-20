'use client'

import { useState, useRef, useEffect } from 'react'
import { apiClient } from '@/lib/api'

interface AdvisorMessage {
  role: 'user' | 'advisor'
  content: string
}

interface ChatAdvisorProps {
  conversationId: string
}

const QUICK_PROMPTS = [
  'What should I say next?',
  'How is the conversation going?',
  'Tell me about this person',
]

export default function ChatAdvisor({ conversationId }: ChatAdvisorProps) {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<AdvisorMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (open && messages.length === 0) {
      setMessages([{
        role: 'advisor',
        content: "Hey! I'm here to help with this conversation. Ask me anything — what to say, how it's going, or about the other person.",
      }])
    }
  }, [open, messages.length])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    if (open) inputRef.current?.focus()
  }, [open])

  const sendQuestion = async (question: string) => {
    if (!question.trim() || loading) return

    setMessages((prev) => [...prev, { role: 'user', content: question }])
    setInput('')
    setLoading(true)

    try {
      const res = await apiClient.askAdvisor(conversationId, question)
      setMessages((prev) => [...prev, { role: 'advisor', content: res.answer }])
    } catch {
      setMessages((prev) => [...prev, { role: 'advisor', content: "Sorry, I couldn't get advice right now. Try again." }])
    } finally {
      setLoading(false)
    }
  }

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="fixed left-4 bottom-20 w-11 h-11 rounded-full shadow-lg flex items-center justify-center transition-all hover:scale-105 active:scale-95 z-40"
        style={{ backgroundColor: '#FDB813' }}
        title="Ask Yellow for advice"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
        </svg>
      </button>
    )
  }

  return (
    <div className="fixed left-4 bottom-20 w-80 h-[420px] bg-white rounded-2xl shadow-2xl border border-neutral-100 flex flex-col z-40 overflow-hidden">
      {/* Header */}
      <div
        className="h-11 px-4 flex items-center justify-between shrink-0"
        style={{ backgroundColor: '#FDB813' }}
      >
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-black">Yellow</span>
          <span className="text-[10px] text-black/60">advisor</span>
        </div>
        <button
          onClick={() => setOpen(false)}
          className="w-6 h-6 rounded-full bg-black/10 flex items-center justify-center text-black/60 hover:bg-black/20 transition text-xs"
        >
          ✕
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-3 py-3 scrollbar-hidden">
        <div className="space-y-2.5">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] px-3 py-2 text-xs leading-relaxed ${
                  msg.role === 'user'
                    ? 'rounded-xl rounded-br-sm bg-neutral-100 text-neutral-800'
                    : 'rounded-xl rounded-bl-sm text-neutral-800'
                }`}
                style={msg.role === 'advisor' ? { backgroundColor: '#FDB81320' } : undefined}
              >
                {msg.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div
                className="px-3 py-2 rounded-xl rounded-bl-sm text-xs text-neutral-500"
                style={{ backgroundColor: '#FDB81320' }}
              >
                <span className="animate-pulse">Thinking...</span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      </div>

      {/* Quick prompts */}
      {messages.length <= 1 && !loading && (
        <div className="px-3 pb-2 flex flex-wrap gap-1.5">
          {QUICK_PROMPTS.map((prompt) => (
            <button
              key={prompt}
              onClick={() => sendQuestion(prompt)}
              className="text-[10px] px-2.5 py-1 rounded-full border border-neutral-200 text-neutral-500 hover:bg-neutral-50 transition"
            >
              {prompt}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="px-3 py-2 border-t border-neutral-100 shrink-0">
        <div className="flex items-center gap-1.5">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendQuestion(input)}
            placeholder="Ask Yellow..."
            disabled={loading}
            className="flex-1 h-8 px-3 rounded-lg bg-neutral-50 text-xs text-neutral-800 placeholder-neutral-400 outline-none focus:ring-1 focus:ring-neutral-200 disabled:opacity-50"
          />
          <button
            onClick={() => sendQuestion(input)}
            disabled={!input.trim() || loading}
            className="w-8 h-8 rounded-lg flex items-center justify-center transition-all hover:brightness-105 active:scale-95 disabled:opacity-30"
            style={{ backgroundColor: '#FDB813' }}
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="black" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}
