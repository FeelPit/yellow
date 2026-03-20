import { useState } from 'react'

interface AuthFormProps {
  mode: 'login' | 'register'
  onSubmit: (data: { email: string; username?: string; password: string }) => Promise<void>
  onToggleMode: () => void
  loading: boolean
  error: string | null
}

export default function AuthForm({
  mode,
  onSubmit,
  onToggleMode,
  loading,
  error,
}: AuthFormProps) {
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (mode === 'register') {
      await onSubmit({ email, username, password })
    } else {
      await onSubmit({ email, password })
    }
  }

  const isValid = () => {
    if (!email || !password) return false
    if (mode === 'register' && !username) return false
    if (password.length < 8) return false
    if (mode === 'register' && username.length < 3) return false
    return true
  }

  return (
    <div className="min-h-screen bg-white flex items-center justify-center px-6">
      <div className="w-full max-w-sm">
        <div className="text-center mb-10">
          <div
            className="inline-flex items-center justify-center w-12 h-12 rounded-xl mb-6"
            style={{ backgroundColor: '#FDB813' }}
          >
            <span className="text-white text-lg font-bold">Y</span>
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-neutral-900 mb-1">
            {mode === 'register' ? 'Create account' : 'Sign in'}
          </h1>
          <p className="text-neutral-400 text-sm">
            {mode === 'register' ? 'Start meeting people' : 'Welcome back'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            className="w-full h-12 px-4 bg-neutral-50 border border-neutral-200 rounded-xl text-sm text-neutral-900 placeholder:text-neutral-400 outline-none transition-colors focus:border-neutral-400 focus:bg-white"
            disabled={loading}
            required
          />

          {mode === 'register' && (
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Username"
              className="w-full h-12 px-4 bg-neutral-50 border border-neutral-200 rounded-xl text-sm text-neutral-900 placeholder:text-neutral-400 outline-none transition-colors focus:border-neutral-400 focus:bg-white"
              disabled={loading}
              minLength={3}
              required
            />
          )}

          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            className="w-full h-12 px-4 bg-neutral-50 border border-neutral-200 rounded-xl text-sm text-neutral-900 placeholder:text-neutral-400 outline-none transition-colors focus:border-neutral-400 focus:bg-white"
            disabled={loading}
            minLength={8}
            required
          />

          {error && (
            <div className="px-4 py-3 bg-red-50 border border-red-100 rounded-xl text-sm text-red-600">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !isValid()}
            className="w-full h-12 rounded-xl text-sm font-medium transition-all duration-200 hover:brightness-105 active:scale-[0.98] disabled:opacity-40 disabled:pointer-events-none"
            style={{ backgroundColor: '#FDB813', color: '#000' }}
          >
            {loading ? 'Loading...' : mode === 'register' ? 'Create account' : 'Sign in'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={onToggleMode}
            className="text-sm text-neutral-400 hover:text-neutral-600 transition-colors"
            disabled={loading}
          >
            {mode === 'register'
              ? 'Already have an account? Sign in'
              : "Don't have an account? Create one"}
          </button>
        </div>
      </div>
    </div>
  )
}
