import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import Home from '@/app/page'

describe('Home Page', () => {
  it('renders heading', () => {
    render(<Home />)
    expect(screen.getByRole('heading', { name: 'Yellow' })).toBeInTheDocument()
  })

  it('renders link to assistant page', () => {
    render(<Home />)
    const link = screen.getByRole('link', { name: /get started/i })
    expect(link).toBeInTheDocument()
    expect(link).toHaveAttribute('href', '/assistant')
  })
})
