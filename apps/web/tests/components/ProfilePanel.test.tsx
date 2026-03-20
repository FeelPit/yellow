import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import ProfilePanel from '@/components/ProfilePanel'
import { ProfileSnapshot } from '@/lib/api'

describe('ProfilePanel Component', () => {
  const mockSnapshot: ProfileSnapshot = {
    metrics: {
      openness: 'Shares personal details naturally, approaches new experiences with curiosity.',
      emotional_style: 'Processes emotions thoughtfully before expressing them.',
      social_energy: 'Enjoys deep one-on-one conversation, recharges alone.',
      conflict_approach: null,
      love_language: 'Values quality time and meaningful conversation.',
      lifestyle: null,
      relationship_values: 'Seeks trust, growth, and emotional safety.',
      humor_and_play: null,
    },
    communication_style: 'Direct and thoughtful communicator',
    attachment_style: 'Secure attachment style',
    partner_preferences: 'Looking for emotional intelligence',
    values: 'Values authenticity and growth',
  }

  it('shows placeholder when snapshot is null', () => {
    render(<ProfilePanel snapshot={null} />)
    expect(screen.getByTestId('profile-panel')).toBeInTheDocument()
    expect(screen.getByText(/start chatting/i)).toBeInTheDocument()
  })

  it('shows loading state', () => {
    render(<ProfilePanel snapshot={null} loading={true} />)
    expect(screen.getByTestId('profile-loading')).toBeInTheDocument()
  })

  it('renders trait insight cards', () => {
    render(<ProfilePanel snapshot={mockSnapshot} />)

    expect(screen.getByTestId('profile-panel')).toBeInTheDocument()
    expect(screen.getByText('Personality insights')).toBeInTheDocument()
    expect(screen.getByText('Openness')).toBeInTheDocument()
    expect(screen.getByText(/Shares personal details/)).toBeInTheDocument()
    expect(screen.getByText('Emotions')).toBeInTheDocument()
    expect(screen.getByText(/Processes emotions/)).toBeInTheDocument()
  })

  it('does not render null traits', () => {
    render(<ProfilePanel snapshot={mockSnapshot} />)

    expect(screen.queryByTestId('trait-conflict_approach')).not.toBeInTheDocument()
    expect(screen.queryByTestId('trait-lifestyle')).not.toBeInTheDocument()
  })

  it('renders profile summary sections', () => {
    render(<ProfilePanel snapshot={mockSnapshot} />)

    expect(screen.getByText('Summary')).toBeInTheDocument()
    expect(screen.getByText('Communication')).toBeInTheDocument()
    expect(screen.getByText('Direct and thoughtful communicator')).toBeInTheDocument()
    expect(screen.getByText('Values')).toBeInTheDocument()
    expect(screen.getByText('Values authenticity and growth')).toBeInTheDocument()
  })

  it('handles empty traits gracefully', () => {
    const empty: ProfileSnapshot = {
      metrics: {
        openness: null,
        emotional_style: null,
        social_energy: null,
        conflict_approach: null,
        love_language: null,
        lifestyle: null,
        relationship_values: null,
        humor_and_play: null,
      },
      communication_style: null,
      attachment_style: null,
      partner_preferences: null,
      values: null,
    }

    render(<ProfilePanel snapshot={empty} />)
    expect(screen.getByText('Analyzing...')).toBeInTheDocument()
    expect(screen.queryByText('Summary')).not.toBeInTheDocument()
  })
})
