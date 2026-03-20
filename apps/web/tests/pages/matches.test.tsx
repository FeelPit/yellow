import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import MatchesPage from '@/app/matches/page'

const mockPush = vi.fn()
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}))

function mockFetch(matchesData: any = null) {
  return vi.fn((url: string) => {
    if (url.includes('/auth/me')) {
      return Promise.resolve({
        ok: true,
        json: async () => ({
          id: 'user-123',
          email: 'test@example.com',
          username: 'testuser',
          created_at: '2026-03-18T12:00:00Z',
        }),
      })
    }

    if (url.includes('/subscription')) {
      return Promise.resolve({
        ok: true,
        json: async () => ({
          active: false,
          plan: null,
          expires_at: null,
          free_chats_remaining: 1,
        }),
      })
    }

    if (url.includes('/likes') && url.includes('/status')) {
      return Promise.resolve({
        ok: true,
        json: async () => ({ liked: false, mutual: false }),
      })
    }

    if (url.includes('/photos/user/')) {
      return Promise.resolve({
        ok: true,
        json: async () => ([]),
      })
    }

    if (url.includes('/matches')) {
      const data = matchesData || {
        matches: [
          {
            user_id: 'match-1',
            username: 'alice',
            profile: {
              communication_style: 'Direct and honest',
              attachment_style: 'Secure',
              partner_preferences: 'Looking for emotional intelligence',
              values: 'Values authenticity',
            },
            match_score: 0.85,
            match_explanation: 'You both value authenticity and emotional intelligence.',
          },
          {
            user_id: 'match-2',
            username: 'bob',
            profile: {
              communication_style: 'Thoughtful listener',
              attachment_style: 'Secure',
              partner_preferences: 'Seeks understanding partner',
              values: 'Values empathy',
            },
            match_score: 0.75,
            match_explanation: 'You both have similar communication styles.',
          },
          {
            user_id: 'match-3',
            username: 'carol',
            profile: {
              communication_style: 'Warm and expressive',
              attachment_style: 'Secure',
              partner_preferences: 'Looking for adventure',
              values: 'Values spontaneity',
            },
            match_score: 0.65,
            match_explanation: 'You both are looking for meaningful connections.',
          },
        ],
        total: 3,
      }
      return Promise.resolve({ ok: true, json: async () => data })
    }

    return Promise.resolve({ ok: true, json: async () => ({}) })
  }) as any
}

describe('Matches Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('redirects to assistant if not authenticated', async () => {
    global.fetch = mockFetch()
    render(<MatchesPage />)

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/assistant')
    })
  })

  it('displays matches after loading', async () => {
    localStorage.setItem('yellow_token', 'test-token')
    global.fetch = mockFetch()
    render(<MatchesPage />)

    await waitFor(() => {
      expect(screen.getByText('Matches')).toBeInTheDocument()
    })

    expect(screen.getByText('alice')).toBeInTheDocument()
    expect(screen.getByText('bob')).toBeInTheDocument()
    expect(screen.getByText('carol')).toBeInTheDocument()
  })

  it('displays match scores', async () => {
    localStorage.setItem('yellow_token', 'test-token')
    global.fetch = mockFetch()
    render(<MatchesPage />)

    await waitFor(() => {
      expect(screen.getByText('85%')).toBeInTheDocument()
    })
    expect(screen.getByText('75%')).toBeInTheDocument()
  })

  it('shows like and message buttons', async () => {
    localStorage.setItem('yellow_token', 'test-token')
    global.fetch = mockFetch()
    render(<MatchesPage />)

    await waitFor(() => {
      const likeButtons = screen.getAllByText('♡ Like')
      expect(likeButtons).toHaveLength(3)
    })

    const msgButtons = screen.getAllByText('Message')
    expect(msgButtons).toHaveLength(3)
  })

  it('shows empty state when no matches', async () => {
    localStorage.setItem('yellow_token', 'test-token')
    global.fetch = mockFetch({ matches: [], total: 0 })
    render(<MatchesPage />)

    await waitFor(() => {
      expect(screen.getByText(/No matches yet/)).toBeInTheDocument()
    })
  })

  it('displays free chats remaining', async () => {
    localStorage.setItem('yellow_token', 'test-token')
    global.fetch = mockFetch()
    render(<MatchesPage />)

    await waitFor(() => {
      expect(screen.getByText(/1 free message/)).toBeInTheDocument()
    })
  })

  it('displays current user info', async () => {
    localStorage.setItem('yellow_token', 'test-token')
    global.fetch = mockFetch()
    render(<MatchesPage />)

    await waitFor(() => {
      expect(screen.getByText('@testuser')).toBeInTheDocument()
    })
  })
})
