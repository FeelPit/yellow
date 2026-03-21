import Link from 'next/link'

export default function Home() {
  return (
    <main className="min-h-screen bg-white flex flex-col items-center justify-center px-5 md:px-6">
      <div className="w-full max-w-md text-center">
        <div className="mb-10 md:mb-14">
          <div
            className="inline-flex items-center justify-center w-14 h-14 md:w-16 md:h-16 rounded-2xl mb-6 md:mb-8"
            style={{ backgroundColor: '#FDB813' }}
          >
            <span className="text-white text-xl md:text-2xl font-bold">Y</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-semibold tracking-tight text-neutral-900 mb-3">
            Yellow
          </h1>
          <p className="text-neutral-500 text-base leading-relaxed">
            Find someone who truly gets you
          </p>
        </div>

        <div className="space-y-4 mb-10 md:mb-14 text-left">
          {[
            'AI builds your relationship profile',
            '5 matches every day',
            'People who share your values',
          ].map((text, i) => (
            <div key={i} className="flex items-center gap-3">
              <div
                className="w-2 h-2 rounded-full shrink-0"
                style={{ backgroundColor: '#FDB813' }}
              />
              <span className="text-neutral-600 text-sm">{text}</span>
            </div>
          ))}
        </div>

        <Link
          href="/assistant"
          className="inline-flex items-center justify-center w-full h-12 rounded-xl text-sm font-medium transition-all duration-200 hover:brightness-105 active:scale-[0.98]"
          style={{ backgroundColor: '#FDB813', color: '#000' }}
        >
          Get started
        </Link>

        <p className="mt-8 text-xs text-neutral-400">
          Free · Private
        </p>
      </div>
    </main>
  )
}
