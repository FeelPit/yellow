import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import AuthForm from '@/components/AuthForm'

describe('AuthForm', () => {
  it('renders login form', () => {
    render(
      <AuthForm
        mode="login"
        onSubmit={vi.fn()}
        onToggleMode={vi.fn()}
        loading={false}
        error={null}
      />
    )

    expect(screen.getByRole('heading', { name: 'Sign in' })).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Email')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument()
    expect(screen.queryByPlaceholderText('Username')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })

  it('renders register form', () => {
    render(
      <AuthForm
        mode="register"
        onSubmit={vi.fn()}
        onToggleMode={vi.fn()}
        loading={false}
        error={null}
      />
    )

    expect(screen.getByRole('heading', { name: 'Create account' })).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Email')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Username')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument()
  })

  it('submits login form', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined)
    const user = userEvent.setup()

    render(
      <AuthForm
        mode="login"
        onSubmit={onSubmit}
        onToggleMode={vi.fn()}
        loading={false}
        error={null}
      />
    )

    await user.type(screen.getByPlaceholderText('Email'), 'test@example.com')
    await user.type(screen.getByPlaceholderText('Password'), 'password123')
    await user.click(screen.getByRole('button', { name: /sign in/i }))

    expect(onSubmit).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123',
    })
  })

  it('submits register form', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined)
    const user = userEvent.setup()

    render(
      <AuthForm
        mode="register"
        onSubmit={onSubmit}
        onToggleMode={vi.fn()}
        loading={false}
        error={null}
      />
    )

    await user.type(screen.getByPlaceholderText('Email'), 'new@example.com')
    await user.type(screen.getByPlaceholderText('Username'), 'newuser')
    await user.type(screen.getByPlaceholderText('Password'), 'password123')
    await user.click(screen.getByRole('button', { name: /create account/i }))

    expect(onSubmit).toHaveBeenCalledWith({
      email: 'new@example.com',
      username: 'newuser',
      password: 'password123',
    })
  })

  it('toggles between login and register', async () => {
    const onToggleMode = vi.fn()
    const user = userEvent.setup()

    render(
      <AuthForm
        mode="login"
        onSubmit={vi.fn()}
        onToggleMode={onToggleMode}
        loading={false}
        error={null}
      />
    )

    await user.click(screen.getByText(/don't have an account/i))
    expect(onToggleMode).toHaveBeenCalled()
  })

  it('displays error message', () => {
    render(
      <AuthForm
        mode="login"
        onSubmit={vi.fn()}
        onToggleMode={vi.fn()}
        loading={false}
        error="Invalid credentials"
      />
    )

    expect(screen.getByText('Invalid credentials')).toBeInTheDocument()
  })
})
