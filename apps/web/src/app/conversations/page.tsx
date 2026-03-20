'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient, ConversationSummary } from '@/lib/api'

export default function ConversationsPage() {
  const router = useRouter()
  const [conversations, setConversations] = useState<ConversationSummary[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const init = async () => {
      try {
        const token = localStorage.getItem('yellow_token')
        if (!token) {
          router.push('/assistant')
          return
        }
        apiClient.setToken(token)
        const convs = await apiClient.listConversations()
        setConversations(convs)
      } catch {
        router.push('/assistant')
      } finally {
        setLoading(false)
      }
    }
    init()
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem('yellow_token')
    router.push('/assistant')
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
    <div className="min-h-screen bg-white">
      <header className="h-14 px-6 flex items-center justify-between border-b border-neutral-100 sticky top-0 bg-white z-10">
        <div className="flex items-center gap-3">
          <div
            className="w-7 h-7 rounded-lg flex items-center justify-center"
            style={{ backgroundColor: '#FDB813' }}
          >
            <span className="text-white text-xs font-bold">Y</span>
          </div>
          <h1 className="text-sm font-semibold text-neutral-900">Chats</h1>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => router.push('/matches')}
            className="h-8 px-3 rounded-lg text-xs font-medium transition-colors hover:bg-neutral-50"
            style={{ color: '#FDB813' }}
          >
            Matches
          </button>
          <button
            onClick={() => router.push('/assistant')}
            className="h-8 px-3 rounded-lg text-xs font-medium transition-colors hover:bg-neutral-50 text-neutral-600"
          >
            Assistant
          </button>
          <button
            onClick={handleLogout}
            className="h-8 px-3 rounded-lg text-xs text-neutral-400 hover:text-neutral-600 hover:bg-neutral-50 transition-colors"
          >
            Log out
          </button>
        </div>
      </header>

      <div className="max-w-2xl mx-auto px-6 py-8">
        {conversations.length === 0 ? (
          <div className="text-center py-24">
            <p className="text-neutral-400 text-sm mb-4">No conversations yet</p>
            <p className="text-neutral-400 text-xs mb-6">
              Like someone on the Matches page — if they like you back, you can chat for free.
            </p>
            <button
              onClick={() => router.push('/matches')}
              className="h-10 px-5 rounded-xl text-sm font-medium transition-all hover:brightness-105"
              style={{ backgroundColor: '#FDB813', color: '#000' }}
            >
              Browse matches
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            {conversations.map((conv) => (
              <button
                key={conv.id}
                onClick={() => router.push(`/chat/${conv.id}`)}
                className="w-full text-left p-4 rounded-xl border border-neutral-100 hover:border-neutral-200 hover:shadow-sm transition-all"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-semibold text-neutral-900">
                    {conv.other_username}
                  </span>
                  {conv.last_message_at && (
                    <span className="text-[10px] text-neutral-400">
                      {new Date(conv.last_message_at).toLocaleDateString()}
                    </span>
                  )}
                </div>
                {conv.last_message ? (
                  <p className="text-xs text-neutral-500 truncate">{conv.last_message}</p>
                ) : (
                  <p className="text-xs text-neutral-400 italic">No messages yet</p>
                )}
                <span className="text-[9px] text-neutral-300 mt-1 inline-block">
                  {conv.access_reason === 'mutual_like'
                    ? 'Mutual like'
                    : conv.access_reason === 'free_message'
                    ? 'Free message'
                    : 'Premium'}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
