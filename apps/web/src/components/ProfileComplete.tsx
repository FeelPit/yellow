'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { ProfileSnapshot } from '@/lib/api'

interface ProfileCompleteProps {
  snapshot: ProfileSnapshot
  onDismiss: () => void
}

const INSIGHT_PRIORITY: { key: keyof ProfileSnapshot; label: string }[] = [
  { key: 'attachment_style', label: 'How you attach' },
  { key: 'values', label: 'What drives you' },
  { key: 'communication_style', label: 'How you connect' },
  { key: 'partner_preferences', label: 'What you need' },
]

export default function ProfileComplete({ snapshot, onDismiss }: ProfileCompleteProps) {
  const router = useRouter()
  const [visible, setVisible] = useState(false)
  const [cardsVisible, setCardsVisible] = useState<boolean[]>([false, false, false])
  const [ctaVisible, setCtaVisible] = useState(false)

  const insights = INSIGHT_PRIORITY
    .filter(({ key }) => {
      const val = snapshot[key]
      return val && val !== 'null'
    })
    .slice(0, 3)
    .map(({ key, label }) => ({
      label,
      text: snapshot[key] as string,
    }))

  useEffect(() => {
    requestAnimationFrame(() => setVisible(true))

    insights.forEach((_, i) => {
      setTimeout(() => {
        setCardsVisible((prev) => {
          const next = [...prev]
          next[i] = true
          return next
        })
      }, 600 + i * 200)
    })

    setTimeout(() => setCtaVisible(true), 600 + insights.length * 200 + 200)
  }, [])

  const handleGo = () => {
    localStorage.setItem('yellow_profile_complete_seen', 'true')
    router.push('/matches')
  }

  const handleStay = () => {
    localStorage.setItem('yellow_profile_complete_seen', 'true')
    onDismiss()
  }

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center px-5"
      style={{
        backgroundColor: 'rgba(10, 10, 10, 0.97)',
        opacity: visible ? 1 : 0,
        transition: 'opacity 0.5s ease-out',
      }}
    >
      <div
        className="max-w-lg w-full text-center"
        style={{
          transform: visible ? 'scale(1)' : 'scale(0.95)',
          opacity: visible ? 1 : 0,
          transition: 'all 0.6s cubic-bezier(0.16, 1, 0.3, 1)',
        }}
      >
        <h1 className="text-3xl sm:text-4xl font-bold text-white tracking-tight mb-3">
          Yellow figured you out.
        </h1>
        <p className="text-neutral-400 text-base sm:text-lg mb-10">
          Here&rsquo;s what we know about you:
        </p>

        <div className="space-y-3 mb-10">
          {insights.map((insight, i) => (
            <div
              key={i}
              className="rounded-xl border border-white/10 bg-white/5 p-4 sm:p-5 text-left"
              style={{
                opacity: cardsVisible[i] ? 1 : 0,
                transform: cardsVisible[i] ? 'translateY(0)' : 'translateY(16px)',
                transition: 'all 0.5s cubic-bezier(0.16, 1, 0.3, 1)',
              }}
            >
              <div className="text-[11px] font-semibold text-amber-400 uppercase tracking-widest mb-1.5">
                {insight.label}
              </div>
              <p className="text-sm text-neutral-300 leading-relaxed">
                {insight.text}
              </p>
            </div>
          ))}
        </div>

        <div
          style={{
            opacity: ctaVisible ? 1 : 0,
            transform: ctaVisible ? 'translateY(0)' : 'translateY(12px)',
            transition: 'all 0.5s cubic-bezier(0.16, 1, 0.3, 1)',
          }}
        >
          <div className="w-12 mx-auto border-t border-white/10 mb-8" />

          <p className="text-neutral-400 text-sm sm:text-base mb-8">
            Ready to meet someone who actually gets you?
          </p>

          <button
            onClick={handleGo}
            className="inline-flex items-center gap-2 text-sm sm:text-base font-semibold px-8 py-3.5 rounded-full bg-amber-400 text-neutral-900 hover:bg-amber-300 hover:scale-105 active:scale-[0.98] transition-all duration-200 shadow-lg shadow-amber-400/20"
          >
            See your matches
            <span className="text-lg">→</span>
          </button>

          <button
            onClick={handleStay}
            className="block mx-auto mt-5 text-xs text-neutral-500 hover:text-neutral-300 transition"
          >
            Keep chatting — I&rsquo;ll check matches later
          </button>
        </div>
      </div>
    </div>
  )
}
