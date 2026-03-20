import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import ChatInput from '@/components/ChatInput'

describe('ChatInput Component', () => {
  it('renders input and send button', () => {
    render(<ChatInput onSend={vi.fn()} />)
    
    expect(screen.getByTestId('chat-input')).toBeInTheDocument()
    expect(screen.getByTestId('send-button')).toBeInTheDocument()
  })

  it('calls onSend with message when submitted', async () => {
    const onSend = vi.fn()
    const user = userEvent.setup()
    
    render(<ChatInput onSend={onSend} />)
    
    const input = screen.getByTestId('chat-input')
    const button = screen.getByTestId('send-button')
    
    await user.type(input, 'Hello world')
    await user.click(button)
    
    expect(onSend).toHaveBeenCalledWith('Hello world')
  })

  it('clears input after sending', async () => {
    const user = userEvent.setup()
    
    render(<ChatInput onSend={vi.fn()} />)
    
    const input = screen.getByTestId('chat-input') as HTMLInputElement
    const button = screen.getByTestId('send-button')
    
    await user.type(input, 'Test message')
    await user.click(button)
    
    expect(input.value).toBe('')
  })

  it('does not send empty messages', async () => {
    const onSend = vi.fn()
    const user = userEvent.setup()
    
    render(<ChatInput onSend={onSend} />)
    
    const button = screen.getByTestId('send-button')
    await user.click(button)
    
    expect(onSend).not.toHaveBeenCalled()
  })

  it('trims whitespace from messages', async () => {
    const onSend = vi.fn()
    const user = userEvent.setup()
    
    render(<ChatInput onSend={onSend} />)
    
    const input = screen.getByTestId('chat-input')
    const button = screen.getByTestId('send-button')
    
    await user.type(input, '  Hello  ')
    await user.click(button)
    
    expect(onSend).toHaveBeenCalledWith('Hello')
  })

  it('disables input and button when disabled prop is true', () => {
    render(<ChatInput onSend={vi.fn()} disabled={true} />)
    
    const input = screen.getByTestId('chat-input')
    const button = screen.getByTestId('send-button')
    
    expect(input).toBeDisabled()
    expect(button).toBeDisabled()
  })
})
