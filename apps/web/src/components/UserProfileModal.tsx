'use client'

import { useState, useEffect } from 'react'
import { apiClient, FullUserProfile, PhotoResponse, ProfileTraits } from '@/lib/api'

interface UserProfileModalProps {
  userId: string
  username: string
  onClose: () => void
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

export default function UserProfileModal({ userId, username, onClose }: UserProfileModalProps) {
  const [profile, setProfile] = useState<FullUserProfile | null>(null)
  const [photos, setPhotos] = useState<PhotoResponse[]>([])
  const [currentPhoto, setCurrentPhoto] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const [profileData, photosData] = await Promise.all([
          apiClient.getUserProfile(userId),
          apiClient.getUserPhotos(userId),
        ])
        setProfile(profileData)
        setPhotos(photosData)
      } catch (err) {
        console.error('Failed to load profile:', err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [userId])

  const filledTraits = profile?.metrics
    ? (Object.entries(profile.metrics) as [keyof ProfileTraits, string | null][]).filter(
        ([, v]) => v !== null && v !== 'null'
      )
    : []

  const filledSections = profile
    ? SECTION_LABELS.filter(({ key }) => {
        const val = profile[key as keyof FullUserProfile]
        return val && val !== 'null'
      })
    : []

  return (
    <div
      className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-end md:items-center justify-center md:p-4"
      onClick={(e) => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="bg-white rounded-t-2xl md:rounded-2xl w-full md:max-w-md max-h-[92vh] md:max-h-[90vh] overflow-y-auto shadow-xl animate-slide-up md:animate-none">
        {/* Close button */}
        <div className="sticky top-0 bg-white z-10 flex justify-end p-3 pb-0">
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-neutral-100 flex items-center justify-center text-neutral-400 hover:bg-neutral-200 hover:text-neutral-600 transition"
          >
            ✕
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div
              className="w-8 h-8 rounded-full border-2 border-t-transparent animate-spin"
              style={{ borderColor: '#FDB813', borderTopColor: 'transparent' }}
            />
          </div>
        ) : (
          <div className="px-5 pb-6">
            {/* Photo slider */}
            {photos.length > 0 && (
              <div className="mb-4">
                <div className="relative rounded-xl overflow-hidden aspect-square bg-neutral-100">
                  <img
                    src={apiClient.getPhotoUrl(photos[currentPhoto].id)}
                    alt={username}
                    className="w-full h-full object-cover"
                  />
                  {photos.length > 1 && (
                    <>
                      <button
                        onClick={() => setCurrentPhoto((p) => (p - 1 + photos.length) % photos.length)}
                        className="absolute left-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-black/30 text-white flex items-center justify-center backdrop-blur-sm hover:bg-black/50 transition"
                      >
                        ‹
                      </button>
                      <button
                        onClick={() => setCurrentPhoto((p) => (p + 1) % photos.length)}
                        className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-black/30 text-white flex items-center justify-center backdrop-blur-sm hover:bg-black/50 transition"
                      >
                        ›
                      </button>
                      <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-1.5">
                        {photos.map((_, i) => (
                          <div
                            key={i}
                            className={`w-2 h-2 rounded-full transition ${i === currentPhoto ? 'bg-white' : 'bg-white/40'}`}
                          />
                        ))}
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}

            {/* No photos placeholder */}
            {photos.length === 0 && (
              <div className="mb-4 aspect-square rounded-xl bg-neutral-50 flex items-center justify-center">
                <div
                  className="w-20 h-20 rounded-full flex items-center justify-center text-2xl font-bold text-white"
                  style={{ backgroundColor: '#FDB813' }}
                >
                  {username[0]?.toUpperCase()}
                </div>
              </div>
            )}

            {/* Name + age */}
            <div className="mb-1">
              <h2 className="text-xl font-semibold text-neutral-900">
                {username}
                {profile?.age && (
                  <span className="text-neutral-400 font-normal ml-2 text-lg">{profile.age}</span>
                )}
              </h2>
              {profile?.gender && (
                <p className="text-xs text-neutral-400 capitalize">{profile.gender}</p>
              )}
            </div>

            {/* Vibe tags */}
            {profile?.vibe_tags && profile.vibe_tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mb-5 mt-3">
                {profile.vibe_tags.map((tag) => (
                  <span
                    key={tag}
                    className="text-[11px] px-2.5 py-1 rounded-full font-medium"
                    style={{ backgroundColor: '#FDB81320', color: '#8B6914' }}
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}

            {/* Trait insights */}
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
                        className="p-2.5 rounded-lg border border-neutral-100"
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

            {/* Summary sections */}
            {filledSections.length > 0 && (
              <div>
                <h3 className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider mb-3">
                  Summary
                </h3>
                <div className="space-y-2">
                  {filledSections.map(({ key, label }) => {
                    const value = profile![key as keyof FullUserProfile] as string
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

            {/* Empty state */}
            {filledTraits.length === 0 && filledSections.length === 0 && (
              <p className="text-sm text-neutral-400 text-center py-6">
                This person is still building their profile.
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
