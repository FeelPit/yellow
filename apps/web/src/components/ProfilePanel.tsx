'use client'

import { useState, useEffect } from 'react'
import { ProfileSnapshot, ProfileTraits, PhotoResponse, apiClient } from '@/lib/api'

interface ProfilePanelProps {
  snapshot: ProfileSnapshot | null
  username?: string
  age?: number | null
  loading?: boolean
}

const TRAIT_LABELS: Record<keyof ProfileTraits, { label: string; icon: string }> = {
  openness: { label: 'Openness', icon: '◐' },
  emotional_style: { label: 'Emotions', icon: '◑' },
  social_energy: { label: 'Social energy', icon: '◒' },
  conflict_approach: { label: 'Conflict style', icon: '◓' },
  love_language: { label: 'Love language', icon: '♡' },
  lifestyle: { label: 'Lifestyle', icon: '↗' },
  relationship_values: { label: 'In relationships', icon: '∞' },
  humor_and_play: { label: 'Humor & play', icon: '~' },
}

const SECTION_LABELS = [
  { key: 'communication_style', label: 'Communication' },
  { key: 'attachment_style', label: 'Attachment' },
  { key: 'partner_preferences', label: 'Preferences' },
  { key: 'values', label: 'Values' },
] as const

export default function ProfilePanel({ snapshot, username, age, loading = false }: ProfilePanelProps) {
  const [photos, setPhotos] = useState<PhotoResponse[]>([])
  const [currentPhoto, setCurrentPhoto] = useState(0)

  useEffect(() => {
    const loadPhotos = async () => {
      try {
        const data = await apiClient.getPhotos()
        setPhotos(data)
      } catch {}
    }
    loadPhotos()
  }, [snapshot])

  if (loading) {
    return (
      <div className="p-4" data-testid="profile-loading">
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-12 bg-neutral-100 rounded-xl animate-pulse" />
          ))}
        </div>
      </div>
    )
  }

  if (!snapshot) {
    return (
      <div className="p-4 text-center" data-testid="profile-panel">
        <p className="text-xs text-neutral-400 mt-8">
          Start chatting to build your profile
        </p>
      </div>
    )
  }

  const traits = snapshot.metrics
  const filledTraits = traits
    ? (Object.entries(traits) as [keyof ProfileTraits, string | null][]).filter(
        ([, v]) => v !== null && v !== 'null'
      )
    : []

  const filledSections = SECTION_LABELS.filter(({ key }) => {
    const val = snapshot[key as keyof ProfileSnapshot]
    return val && val !== 'null'
  })

  return (
    <div className="p-4" data-testid="profile-panel">
      {/* Photo slider */}
      {photos.length > 0 && (
        <div className="mb-4">
          <div className="relative rounded-xl overflow-hidden aspect-square bg-neutral-100">
            <img
              src={apiClient.getPhotoUrl(photos[currentPhoto].id)}
              alt="Profile photo"
              className="w-full h-full object-cover"
            />
            {photos.length > 1 && (
              <>
                <button
                  onClick={() => setCurrentPhoto((p) => (p - 1 + photos.length) % photos.length)}
                  className="absolute left-1.5 top-1/2 -translate-y-1/2 w-7 h-7 rounded-full bg-black/30 text-white flex items-center justify-center text-xs backdrop-blur-sm hover:bg-black/50 transition"
                >
                  ‹
                </button>
                <button
                  onClick={() => setCurrentPhoto((p) => (p + 1) % photos.length)}
                  className="absolute right-1.5 top-1/2 -translate-y-1/2 w-7 h-7 rounded-full bg-black/30 text-white flex items-center justify-center text-xs backdrop-blur-sm hover:bg-black/50 transition"
                >
                  ›
                </button>
                <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-1">
                  {photos.map((_, i) => (
                    <div
                      key={i}
                      className={`w-1.5 h-1.5 rounded-full transition ${i === currentPhoto ? 'bg-white' : 'bg-white/40'}`}
                    />
                  ))}
                </div>
              </>
            )}
            {photos[currentPhoto].vibe_tags && photos[currentPhoto].vibe_tags!.length > 0 && (
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/50 to-transparent px-3 py-2 pt-6">
                <div className="flex flex-wrap gap-1">
                  {photos[currentPhoto].vibe_tags!.map((tag) => (
                    <span key={tag} className="text-[9px] text-white/90 bg-white/20 backdrop-blur-sm px-1.5 py-0.5 rounded-full">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Name and age */}
      {(username || age) && (
        <div className="mb-4">
          <div className="flex items-baseline gap-2">
            {username && (
              <span className="text-base font-semibold text-neutral-900">{username}</span>
            )}
            {age && (
              <span className="text-sm text-neutral-400">{age}</span>
            )}
          </div>
        </div>
      )}

      {/* Profile readiness */}
      {snapshot.profile_readiness != null && (
        <div className="mb-5">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider">
              Profile readiness
            </span>
            <span className="text-[11px] font-semibold text-neutral-500">
              {snapshot.profile_readiness}%
            </span>
          </div>
          <div className="h-1.5 bg-neutral-100 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-700 ease-out"
              style={{
                width: `${snapshot.profile_readiness}%`,
                backgroundColor: snapshot.profile_readiness >= 85 ? '#22c55e' : '#FDB813',
              }}
            />
          </div>
          <p className="text-[10px] text-neutral-400 mt-1">
            {snapshot.profile_readiness < 30
              ? 'Just getting started — keep chatting'
              : snapshot.profile_readiness < 60
              ? 'Patterns emerging — tell me more'
              : snapshot.profile_readiness < 85
              ? 'Strong picture — a few gaps left'
              : 'Ready to match ✓'}
          </p>
        </div>
      )}

      {/* Trait insights — only filled ones */}
      {filledTraits.length > 0 && (
        <div className="mb-5">
          <h3 className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider mb-3">
            Personality insights
          </h3>
          <div className="space-y-2">
            {filledTraits.map(([key, value]) => {
              const meta = TRAIT_LABELS[key]
              if (!meta) return null
              return (
                <div
                  key={key}
                  className="p-2.5 rounded-lg border border-neutral-100 animate-fade-in"
                  data-testid={`trait-${key}`}
                >
                  <div className="flex items-center gap-1.5 mb-0.5">
                    <span className="text-[10px] text-neutral-300">{meta.icon}</span>
                    <span className="text-[10px] font-semibold text-neutral-400 uppercase tracking-wider">
                      {meta.label}
                    </span>
                  </div>
                  <p className="text-[12px] text-neutral-700 leading-relaxed">{value}</p>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* No insights yet */}
      {filledTraits.length === 0 && filledSections.length === 0 && (
        <p className="text-xs text-neutral-400 text-center mt-4">Analyzing...</p>
      )}

      {/* Profile summaries — only filled ones */}
      {filledSections.length > 0 && (
        <div>
          <h3 className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider mb-3">
            Summary
          </h3>
          <div className="space-y-2">
            {filledSections.map(({ key, label }) => {
              const value = snapshot[key as keyof ProfileSnapshot] as string
              return (
                <div key={key} className="p-2.5 bg-neutral-50 rounded-lg">
                  <div className="text-[10px] font-medium text-neutral-400 mb-0.5">{label}</div>
                  <p className="text-[12px] text-neutral-700 leading-relaxed">{value}</p>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
