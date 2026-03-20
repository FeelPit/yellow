import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import AssistantPage from '@/app/assistant/page'

describe('Assistant Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()

    global.fetch = vi.fn((url) => {
      if (url.includes('/auth/register') || url.includes('/auth/login')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            access_token: 'test-token-123',
            token_type: 'bearer',
          }),
        })
      }

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

      if (url.includes('/session') && !url.includes('/start') && !url.includes('/message')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            session_id: 'test-session-123',
            status: 'created',
          }),
        })
      }

      if (url.includes('/start')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            messages: [
              {
                id: '1',
                session_id: 'test-session-123',
                role: 'assistant',
                content: 'What brings you to Yellow today?',
                thinking: null,
                created_at: '2026-03-18T12:00:00Z',
              },
            ],
          }),
        })
      }

      if (url.includes('/message')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            user_message: {
              id: '4',
              session_id: 'test-session-123',
              role: 'user',
              content: 'My answer',
              thinking: null,
              created_at: '2026-03-18T12:00:03Z',
            },
            assistant_message: {
              id: '5',
              session_id: 'test-session-123',
              role: 'assistant',
              content: 'Follow-up question?',
              thinking: 'User is open and communicative.',
              created_at: '2026-03-18T12:00:04Z',
            },
            profile_ready: false,
            profile_snapshot: {
              age: null,
              gender: null,
              metrics: {
                openness: 'Shares willingly, comfortable with self-disclosure.',
                emotional_style: null,
                social_energy: 'Approachable and ready to engage.',
                conflict_approach: null,
                love_language: null,
                lifestyle: null,
                relationship_values: null,
                humor_and_play: null,
              },
              communication_style: 'Direct communicator',
              attachment_style: null,
              partner_preferences: null,
              values: null,
            },
            intent: null,
            profile_view: null,
          }),
        })
      }

      return Promise.reject(new Error('Unknown URL'))
    }) as any
  })

  it('renders login form initially', () => {
    render(<AssistantPage />)

    expect(screen.getByRole('heading', { name: 'Sign in' })).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Email')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument()
  })

  it('renders initial questions after login', async () => {
    const user = userEvent.setup()
    render(<AssistantPage />)

    await user.type(screen.getByPlaceholderText('Email'), 'test@example.com')
    await user.type(screen.getByPlaceholderText('Password'), 'password123')
    await user.click(screen.getByRole('button', { name: /sign in/i }))

    await waitFor(() => {
      expect(screen.getByText('What brings you to Yellow today?')).toBeInTheDocument()
    })
  })

  it('sends message and shows trait insights in profile', async () => {
    const user = userEvent.setup()
    render(<AssistantPage />)

    await user.type(screen.getByPlaceholderText('Email'), 'test@example.com')
    await user.type(screen.getByPlaceholderText('Password'), 'password123')
    await user.click(screen.getByRole('button', { name: /sign in/i }))

    await waitFor(() => {
      expect(screen.getByText('What brings you to Yellow today?')).toBeInTheDocument()
    })

    const input = screen.getByTestId('chat-input')
    await user.type(input, 'My answer')
    await user.click(screen.getByTestId('send-button'))

    await waitFor(() => {
      expect(screen.getByText('My answer')).toBeInTheDocument()
    })
    expect(screen.getByText('Follow-up question?')).toBeInTheDocument()

    await waitFor(() => {
      expect(screen.getByText('Openness')).toBeInTheDocument()
    })
    expect(screen.getByText(/Shares willingly/)).toBeInTheDocument()
  })

  it('toggles to register form', async () => {
    const user = userEvent.setup()
    render(<AssistantPage />)

    await user.click(screen.getByText(/don't have an account/i))

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Create account' })).toBeInTheDocument()
    })
    expect(screen.getByPlaceholderText('Username')).toBeInTheDocument()
  })

  it('renders camera button for photo upload', async () => {
    const user = userEvent.setup()
    render(<AssistantPage />)

    await user.type(screen.getByPlaceholderText('Email'), 'test@example.com')
    await user.type(screen.getByPlaceholderText('Password'), 'password123')
    await user.click(screen.getByRole('button', { name: /sign in/i }))

    await waitFor(() => {
      expect(screen.getByText('What brings you to Yellow today?')).toBeInTheDocument()
    })

    expect(screen.getByTestId('camera-button')).toBeInTheDocument()
  })

  it('shows thinking toggle on assistant messages', async () => {
    const user = userEvent.setup()
    render(<AssistantPage />)

    await user.type(screen.getByPlaceholderText('Email'), 'test@example.com')
    await user.type(screen.getByPlaceholderText('Password'), 'password123')
    await user.click(screen.getByRole('button', { name: /sign in/i }))

    await waitFor(() => {
      expect(screen.getByText('What brings you to Yellow today?')).toBeInTheDocument()
    })

    const input = screen.getByTestId('chat-input')
    await user.type(input, 'My answer')
    await user.click(screen.getByTestId('send-button'))

    await waitFor(() => {
      expect(screen.getByText('Follow-up question?')).toBeInTheDocument()
    })

    const toggles = screen.getAllByTestId('thinking-toggle')
    expect(toggles.length).toBeGreaterThan(0)
  })
})
