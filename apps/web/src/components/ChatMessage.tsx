'use client'

import { useState } from 'react'
import { Message } from '@/lib/api'

interface ChatMessageProps {
  message: Message
  showThinking?: boolean
}

export default function ChatMessage({ message, showThinking = true }: ChatMessageProps) {
  const isUser = message.role === 'user'
  const [expanded, setExpanded] = useState(false)
  const hasThinking = !isUser && message.thinking

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3`}
      data-testid={`message-${message.role}`}
    >
      <div className="max-w-[75%]">
        {hasThinking && showThinking && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 mb-1 text-[10px] text-neutral-400 hover:text-neutral-500 transition-colors"
            data-testid="thinking-toggle"
          >
            <svg
              width="12"
              height="12"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className={`transition-transform duration-200 ${expanded ? 'rotate-90' : ''}`}
            >
              <polyline points="9 18 15 12 9 6" />
            </svg>
            AI thinking
          </button>
        )}

        {hasThinking && showThinking && expanded && (
          <div
            className="mb-1.5 px-3 py-2 text-[11px] text-neutral-500 bg-amber-50 border border-amber-100 rounded-lg leading-relaxed animate-fade-in"
            data-testid="thinking-content"
          >
            {message.thinking}
          </div>
        )}

        <div
          className={`px-4 py-2.5 text-sm leading-relaxed ${
            isUser
              ? 'rounded-2xl rounded-br-md text-neutral-900'
              : 'rounded-2xl rounded-bl-md text-neutral-800'
          }`}
          style={{
            backgroundColor: isUser ? '#FDB813' : '#F5F5F5',
          }}
        >
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>
      </div>
    </div>
  )
}
