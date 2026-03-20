import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect } from 'vitest'
import ChatMessage from '@/components/ChatMessage'
import { Message } from '@/lib/api'

describe('ChatMessage Component', () => {
  const baseMessage: Message = {
    id: '123',
    session_id: 'session-123',
    role: 'user',
    content: 'Test message',
    created_at: '2026-03-18T12:00:00Z',
  }

  it('renders user message with correct styling', () => {
    render(<ChatMessage message={baseMessage} />)

    const messageElement = screen.getByTestId('message-user')
    expect(messageElement).toBeInTheDocument()
    expect(screen.getByText('Test message')).toBeInTheDocument()
  })

  it('renders assistant message with correct styling', () => {
    const assistantMessage: Message = {
      ...baseMessage,
      role: 'assistant',
      content: 'Assistant response',
    }

    render(<ChatMessage message={assistantMessage} />)

    const messageElement = screen.getByTestId('message-assistant')
    expect(messageElement).toBeInTheDocument()
    expect(screen.getByText('Assistant response')).toBeInTheDocument()
  })

  it('shows thinking toggle for assistant messages with thinking', () => {
    const msg: Message = {
      ...baseMessage,
      role: 'assistant',
      content: 'Some response',
      thinking: 'User seems open and direct.',
    }

    render(<ChatMessage message={msg} showThinking={true} />)

    expect(screen.getByTestId('thinking-toggle')).toBeInTheDocument()
    expect(screen.queryByTestId('thinking-content')).not.toBeInTheDocument()
  })

  it('expands thinking on click', async () => {
    const user = userEvent.setup()
    const msg: Message = {
      ...baseMessage,
      role: 'assistant',
      content: 'Some response',
      thinking: 'User seems open and direct.',
    }

    render(<ChatMessage message={msg} showThinking={true} />)

    await user.click(screen.getByTestId('thinking-toggle'))
    expect(screen.getByTestId('thinking-content')).toBeInTheDocument()
    expect(screen.getByText('User seems open and direct.')).toBeInTheDocument()
  })

  it('hides thinking when showThinking is false', () => {
    const msg: Message = {
      ...baseMessage,
      role: 'assistant',
      content: 'Some response',
      thinking: 'Insight here.',
    }

    render(<ChatMessage message={msg} showThinking={false} />)

    expect(screen.queryByTestId('thinking-toggle')).not.toBeInTheDocument()
  })

  it('does not show thinking toggle for user messages', () => {
    const msg: Message = {
      ...baseMessage,
      role: 'user',
      content: 'User message',
      thinking: null,
    }

    render(<ChatMessage message={msg} showThinking={true} />)

    expect(screen.queryByTestId('thinking-toggle')).not.toBeInTheDocument()
  })
})
