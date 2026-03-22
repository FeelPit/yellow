'use client'

import Link from 'next/link'
import { useEffect, useRef } from 'react'

function useScrollReveal() {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('revealed')
            observer.unobserve(entry.target)
          }
        })
      },
      { threshold: 0.15 }
    )

    const children = el.querySelectorAll('.reveal')
    children.forEach((child) => observer.observe(child))

    return () => observer.disconnect()
  }, [])

  return ref
}

function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md bg-white/80 border-b border-neutral-100">
      <div className="max-w-6xl mx-auto px-5 h-14 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-1.5">
          <span className="text-lg font-bold text-neutral-900">Yellow</span>
          <span className="w-2 h-2 rounded-full bg-amber-400 -mt-2" />
        </Link>
        <div className="flex items-center gap-4">
          <Link
            href="/assistant"
            className="text-sm text-neutral-500 hover:text-neutral-900 transition hidden sm:block"
          >
            Sign in
          </Link>
          <Link
            href="/assistant"
            className="text-sm font-medium px-4 py-2 rounded-full bg-amber-400 text-neutral-900 hover:bg-amber-300 hover:scale-105 active:scale-[0.98] transition-all duration-200"
          >
            Get started
          </Link>
        </div>
      </div>
    </header>
  )
}

function Hero() {
  return (
    <section className="min-h-[85vh] sm:min-h-screen flex items-center justify-center px-5 pt-14">
      <div className="max-w-2xl text-center">
        <h1 className="text-3xl sm:text-5xl md:text-6xl font-bold text-neutral-900 tracking-tight leading-[1.1] mb-5 sm:mb-6">
          You don&rsquo;t need another
          <br />
          dating app.
        </h1>
        <p className="text-base sm:text-xl text-neutral-500 mb-8 sm:mb-10 max-w-lg mx-auto leading-relaxed">
          You need to understand what you actually want.
        </p>
        <Link
          href="/assistant"
          className="inline-flex items-center gap-2 text-sm sm:text-base font-medium px-6 sm:px-8 py-3 sm:py-3.5 rounded-full bg-amber-400 text-neutral-900 hover:bg-amber-300 hover:scale-105 active:scale-[0.98] transition-all duration-200 shadow-lg shadow-amber-200/50"
        >
          Start the conversation
          <span className="text-base sm:text-lg">→</span>
        </Link>
        <p className="mt-4 text-xs sm:text-sm text-neutral-400">
          Takes 10 minutes. No photos required.
        </p>
      </div>
    </section>
  )
}

function HowItWorks() {
  const ref = useScrollReveal()

  const steps = [
    {
      num: '01',
      title: 'Talk to Yellow',
      desc: 'An AI that asks the questions you\'ve never asked yourself.',
    },
    {
      num: '02',
      title: 'Understand yourself',
      desc: 'See your patterns, values, and what you actually need.',
    },
    {
      num: '03',
      title: 'Meet the right person',
      desc: 'Matched by character, not photos.',
    },
  ]

  return (
    <section className="py-16 sm:py-32 px-5" ref={ref}>
      <div className="max-w-5xl mx-auto">
        <h2 className="reveal text-xs sm:text-sm font-semibold text-amber-500 uppercase tracking-widest mb-3 text-center">
          How it works
        </h2>
        <p className="reveal text-xl sm:text-3xl font-bold text-neutral-900 text-center mb-10 sm:mb-16 tracking-tight">
          Three steps to someone who gets you
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 sm:gap-12">
          {steps.map((step, i) => (
            <div
              key={i}
              className="reveal text-center sm:text-left"
              style={{ transitionDelay: `${i * 100}ms` }}
            >
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-amber-50 text-amber-500 font-bold text-sm mb-5">
                {step.num}
              </div>
              <h3 className="text-lg font-semibold text-neutral-900 mb-2">
                {step.title}
              </h3>
              <p className="text-neutral-500 text-sm leading-relaxed">
                {step.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function Discover() {
  const ref = useScrollReveal()

  const cards = [
    {
      icon: '◐',
      title: 'Who you are in relationships',
      desc: 'Your communication style, emotional patterns, and the things you don\'t notice about yourself.',
    },
    {
      icon: '◑',
      title: 'What you actually need',
      desc: 'Not what you think you want — what makes you feel safe, seen, and alive.',
    },
    {
      icon: '◒',
      title: 'The kind of person who\'ll get you',
      desc: 'Someone matched to your depth, not your surface.',
    },
  ]

  return (
    <section className="py-16 sm:py-32 px-5 bg-neutral-50" ref={ref}>
      <div className="max-w-5xl mx-auto">
        <h2 className="reveal text-xs sm:text-sm font-semibold text-amber-500 uppercase tracking-widest mb-3 text-center">
          What you&rsquo;ll discover
        </h2>
        <p className="reveal text-xl sm:text-3xl font-bold text-neutral-900 text-center mb-10 sm:mb-16 tracking-tight">
          An honest mirror before a match
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          {cards.map((card, i) => (
            <div
              key={i}
              className="reveal bg-white rounded-2xl p-6 sm:p-8 border border-neutral-100"
              style={{ transitionDelay: `${i * 100}ms` }}
            >
              <span className="text-2xl text-amber-400 block mb-4">{card.icon}</span>
              <h3 className="text-base font-semibold text-neutral-900 mb-2">
                {card.title}
              </h3>
              <p className="text-sm text-neutral-500 leading-relaxed">
                {card.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function PullQuote() {
  const ref = useScrollReveal()

  return (
    <section className="py-16 sm:py-32 px-5" ref={ref}>
      <div className="max-w-3xl mx-auto text-center">
        <div className="reveal">
          <span className="text-3xl sm:text-4xl text-amber-300 block mb-4 sm:mb-6">&ldquo;</span>
          <p className="text-xl sm:text-3xl md:text-4xl font-semibold text-neutral-900 leading-snug tracking-tight">
            When you understand yourself&thinsp;&mdash;&thinsp;the right person finds you.
          </p>
        </div>
      </div>
    </section>
  )
}

function FinalCta() {
  const ref = useScrollReveal()

  return (
    <section className="py-16 sm:py-32 px-5 bg-amber-50" ref={ref}>
      <div className="max-w-2xl mx-auto text-center">
        <h2 className="reveal text-xl sm:text-3xl md:text-4xl font-bold text-neutral-900 tracking-tight mb-3 sm:mb-4">
          Ready to actually understand yourself?
        </h2>
        <p className="reveal text-neutral-500 mb-8 sm:mb-10 text-sm sm:text-base">
          No swiping. No photos. Just an honest conversation.
        </p>
        <div className="reveal">
          <Link
            href="/assistant"
            className="inline-flex items-center gap-2 text-sm sm:text-base font-medium px-6 sm:px-8 py-3 sm:py-3.5 rounded-full bg-amber-400 text-neutral-900 hover:bg-amber-300 hover:scale-105 active:scale-[0.98] transition-all duration-200 shadow-lg shadow-amber-200/50"
          >
            Start for free
            <span className="text-lg">→</span>
          </Link>
        </div>
      </div>
    </section>
  )
}

function Footer() {
  return (
    <footer className="py-8 px-5 border-t border-neutral-100">
      <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2 text-sm text-neutral-400">
        <span>Yellow &copy; 2026</span>
        <a
          href="https://ydate.fr"
          className="hover:text-neutral-600 transition"
          target="_blank"
          rel="noopener noreferrer"
        >
          ydate.fr
        </a>
      </div>
    </footer>
  )
}

export default function Home() {
  return (
    <>
      <Header />
      <main>
        <Hero />
        <HowItWorks />
        <Discover />
        <PullQuote />
        <FinalCta />
      </main>
      <Footer />
    </>
  )
}
