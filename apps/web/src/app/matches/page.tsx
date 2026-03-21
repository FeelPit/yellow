'use client'

import { useEffect, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient, LikeStatus, SubscriptionStatus, PhotoResponse } from '@/lib/api'
import UserProfileModal from '@/components/UserProfileModal'

interface Profile {
  age: number | null
  gender: string | null
  communication_style: string | null
  attachment_style: string | null
  partner_preferences: string | null
  values: string | null
}

interface Match {
  user_id: string
  username: string
  profile: Profile
  match_score: number
  match_explanation: string
}

export default function MatchesPage() {
  const router = useRouter()
  const [matches, setMatches] = useState<Match[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentUser, setCurrentUser] = useState<any>(null)
  const [likeStatuses, setLikeStatuses] = useState<Record<string, LikeStatus>>({})
  const [subscription, setSubscription] = useState<SubscriptionStatus | null>(null)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [avatars, setAvatars] = useState<Record<string, string | null>>({})
  const [viewingProfile, setViewingProfile] = useState<{ userId: string; username: string } | null>(null)

  useEffect(() => {
    const initMatches = async () => {
      try {
        const token = localStorage.getItem('yellow_token')
        if (!token) {
          router.push('/assistant')
          return
        }

        apiClient.setToken(token)

        const user = await apiClient.getCurrentUser()
        setCurrentUser(user)

        const [matchesData, subData] = await Promise.all([
          apiClient.getMatches(user.id),
          apiClient.getSubscriptionStatus(),
        ])
        setMatches(matchesData.matches)
        setSubscription(subData)

        const statuses: Record<string, LikeStatus> = {}
        const avatarMap: Record<string, string | null> = {}
        await Promise.all(
          matchesData.matches.map(async (m) => {
            try {
              statuses[m.user_id] = await apiClient.getLikeStatus(m.user_id)
            } catch {
              statuses[m.user_id] = { liked: false, mutual: false }
            }
            try {
              const photos = await apiClient.getUserPhotos(m.user_id)
              avatarMap[m.user_id] = photos.length > 0 ? apiClient.getPhotoUrl(photos[0].id) : null
            } catch {
              avatarMap[m.user_id] = null
            }
          })
        )
        setLikeStatuses(statuses)
        setAvatars(avatarMap)
      } catch (err: any) {
        console.error('Error loading matches:', err)
        if (err.message?.includes('401') || err.message?.includes('authentication')) {
          localStorage.removeItem('yellow_token')
          router.push('/assistant')
        } else {
          setError(err.message || 'Failed to load matches')
        }
      } finally {
        setLoading(false)
      }
    }

    initMatches()
  }, [router])

  const handleLike = useCallback(async (userId: string) => {
    setActionLoading(userId)
    try {
      const status = likeStatuses[userId]
      if (status?.liked) {
        await apiClient.unlikeUser(userId)
        setLikeStatuses((prev) => ({
          ...prev,
          [userId]: { liked: false, mutual: false },
        }))
      } else {
        await apiClient.likeUser(userId)
        const newStatus = await apiClient.getLikeStatus(userId)
        setLikeStatuses((prev) => ({
          ...prev,
          [userId]: newStatus,
        }))
      }
    } catch (err: any) {
      console.error('Like error:', err)
    } finally {
      setActionLoading(null)
    }
  }, [likeStatuses])

  const handleMessage = useCallback(async (userId: string) => {
    setActionLoading(userId + '-msg')
    try {
      const access = await apiClient.checkAccess(userId)
      if (!access.can_message) {
        alert('Like them first — if they like you back, you can chat for free. Or subscribe for unlimited messaging.')
        return
      }
      const conv = await apiClient.startConversationWith(userId)
      router.push(`/chat/${conv.id}`)
    } catch (err: any) {
      if (err.message?.includes('Subscribe') || err.message?.includes('likes')) {
        alert('Like them first — if they like you back, you can chat for free. Or subscribe for unlimited messaging.')
      } else {
        console.error('Message error:', err)
      }
    } finally {
      setActionLoading(null)
    }
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

  if (error) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center px-6">
        <div className="text-center">
          <p className="text-neutral-600 text-sm mb-4">{error}</p>
          <button
            onClick={() => router.push('/assistant')}
            className="h-10 px-5 rounded-xl text-sm font-medium transition-all hover:brightness-105"
            style={{ backgroundColor: '#FDB813', color: '#000' }}
          >
            Go back
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white">
      <header className="h-14 px-4 md:px-6 flex items-center justify-between border-b border-neutral-100 sticky top-0 bg-white z-10">
        <div className="flex items-center gap-2 md:gap-3 min-w-0">
          <div
            className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0"
            style={{ backgroundColor: '#FDB813' }}
          >
            <span className="text-white text-xs font-bold">Y</span>
          </div>
          <h1 className="text-sm font-semibold text-neutral-900">Matches</h1>
          {currentUser && (
            <span className="text-xs text-neutral-400 hidden sm:inline">@{currentUser.username}</span>
          )}
        </div>
        <div className="flex items-center gap-0.5 md:gap-1 shrink-0">
          {subscription && !subscription.active && (
            <span className="text-[10px] text-neutral-400 mr-1 md:mr-2 hidden sm:inline">
              {subscription.free_chats_remaining > 0
                ? `${subscription.free_chats_remaining} free msg`
                : 'No free msgs'}
            </span>
          )}
          <button
            onClick={() => router.push('/conversations')}
            className="h-8 px-2 md:px-3 rounded-lg text-xs font-medium transition-colors hover:bg-neutral-50 text-neutral-600"
          >
            Chats
          </button>
          <button
            onClick={() => router.push('/assistant')}
            className="h-8 px-2 md:px-3 rounded-lg text-xs font-medium transition-colors hover:bg-neutral-50"
            style={{ color: '#FDB813' }}
          >
            <span className="hidden sm:inline">Assistant</span>
            <span className="sm:hidden">AI</span>
          </button>
          <button
            onClick={handleLogout}
            className="h-8 px-2 md:px-3 rounded-lg text-xs text-neutral-400 hover:text-neutral-600 hover:bg-neutral-50 transition-colors"
          >
            <span className="hidden sm:inline">Log out</span>
            <span className="sm:hidden">↗</span>
          </button>
        </div>
      </header>

      <div className="max-w-3xl mx-auto px-4 md:px-6 py-6 md:py-8">
        {matches.length === 0 ? (
          <div className="text-center py-24">
            <div
              className="inline-flex items-center justify-center w-14 h-14 rounded-2xl mb-5"
              style={{ backgroundColor: '#FDB81320' }}
            >
              <span className="text-2xl">💛</span>
            </div>
            <p className="text-neutral-500 text-sm mb-6">
              No matches yet.<br />Complete your profile to see people.
            </p>
            <button
              onClick={() => router.push('/assistant')}
              className="h-10 px-5 rounded-xl text-sm font-medium transition-all hover:brightness-105"
              style={{ backgroundColor: '#FDB813', color: '#000' }}
            >
              Back to chat
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {matches.map((match) => {
              const likeStatus = likeStatuses[match.user_id]
              const isLiked = likeStatus?.liked ?? false
              const isMutual = likeStatus?.mutual ?? false

              return (
                <div
                  key={match.user_id}
                  className="border border-neutral-100 rounded-2xl p-4 md:p-5 transition-all hover:border-neutral-200 hover:shadow-sm"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      {avatars[match.user_id] ? (
                        <img
                          src={avatars[match.user_id]!}
                          alt={match.username}
                          className="w-10 h-10 rounded-full object-cover shrink-0"
                        />
                      ) : (
                        <div
                          className="w-10 h-10 rounded-full flex items-center justify-center shrink-0 text-xs font-bold text-white"
                          style={{ backgroundColor: '#FDB813' }}
                        >
                          {match.username[0]?.toUpperCase()}
                        </div>
                      )}
                      <div>
                        <h2 className="text-base font-semibold text-neutral-900">
                          {match.username}
                          {match.profile.age && (
                            <span className="text-neutral-400 font-normal ml-2 text-sm">
                              {match.profile.age}
                            </span>
                          )}
                        </h2>
                        {isMutual && (
                          <span className="text-[10px] font-medium text-green-600 bg-green-50 px-2 py-0.5 rounded-full">
                            Mutual like
                          </span>
                        )}
                      </div>
                    </div>
                    <span
                      className="text-xs font-medium px-2.5 py-1 rounded-lg"
                      style={{ backgroundColor: '#FDB81315', color: '#B8860B' }}
                    >
                      {Math.round(match.match_score * 100)}%
                    </span>
                  </div>

                  <p className="text-sm text-neutral-500 leading-relaxed mb-4">
                    {match.match_explanation}
                  </p>

                  <div className="flex flex-wrap gap-1.5 md:gap-2 mb-4">
                    {match.profile.communication_style && (
                      <span className="text-[11px] md:text-xs text-neutral-500 bg-neutral-50 px-2 md:px-2.5 py-1 rounded-lg">
                        {match.profile.communication_style.slice(0, 35)}
                        {match.profile.communication_style.length > 35 ? '...' : ''}
                      </span>
                    )}
                    {match.profile.values && (
                      <span className="text-[11px] md:text-xs text-neutral-500 bg-neutral-50 px-2 md:px-2.5 py-1 rounded-lg">
                        {match.profile.values.slice(0, 35)}
                        {match.profile.values.length > 35 ? '...' : ''}
                      </span>
                    )}
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <button
                      onClick={() => handleLike(match.user_id)}
                      disabled={actionLoading === match.user_id}
                      className={`h-9 px-3 md:px-4 rounded-lg text-xs font-medium transition-all duration-200 active:scale-[0.98] border ${
                        isLiked
                          ? 'bg-red-50 border-red-200 text-red-600'
                          : 'bg-white border-neutral-200 text-neutral-600 hover:border-red-200 hover:text-red-500'
                      }`}
                      data-testid={`like-${match.user_id}`}
                    >
                      {actionLoading === match.user_id ? '...' : isLiked ? '♥ Liked' : '♡ Like'}
                    </button>

                    <button
                      onClick={() => setViewingProfile({ userId: match.user_id, username: match.username })}
                      className="h-9 px-3 md:px-4 rounded-lg text-xs font-medium transition-all duration-200 active:scale-[0.98] border border-neutral-200 text-neutral-600 hover:bg-neutral-50"
                    >
                      Profile
                    </button>

                    <button
                      onClick={() => handleMessage(match.user_id)}
                      disabled={actionLoading === match.user_id + '-msg'}
                      className="h-9 px-3 md:px-4 rounded-lg text-xs font-medium transition-all duration-200 hover:brightness-105 active:scale-[0.98]"
                      style={{ backgroundColor: '#FDB813', color: '#000' }}
                      data-testid={`message-${match.user_id}`}
                    >
                      {actionLoading === match.user_id + '-msg' ? '...' : 'Message'}
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {viewingProfile && (
        <UserProfileModal
          userId={viewingProfile.userId}
          username={viewingProfile.username}
          onClose={() => setViewingProfile(null)}
        />
      )}
    </div>
  )
}
