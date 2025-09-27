import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Button } from './button'

describe('Button Component', () => {
  it('should render with default props', () => {
    render(<Button>Click me</Button>)

    const button = screen.getByRole('button', { name: 'Click me' })
    expect(button).toBeInTheDocument()
    expect(button).toHaveClass('bg-primary', 'text-primary-foreground')
  })

  it('should render different variants', () => {
    const { rerender } = render(<Button variant="destructive">Delete</Button>)

    let button = screen.getByRole('button')
    expect(button).toHaveClass('bg-destructive', 'text-destructive-foreground')

    rerender(<Button variant="outline">Outline</Button>)
    button = screen.getByRole('button')
    expect(button).toHaveClass('border', 'border-input', 'bg-background')

    rerender(<Button variant="secondary">Secondary</Button>)
    button = screen.getByRole('button')
    expect(button).toHaveClass('bg-secondary', 'text-secondary-foreground')

    rerender(<Button variant="ghost">Ghost</Button>)
    button = screen.getByRole('button')
    expect(button).toHaveClass('hover:bg-accent')

    rerender(<Button variant="link">Link</Button>)
    button = screen.getByRole('button')
    expect(button).toHaveClass('text-primary', 'underline-offset-4')
  })

  it('should render different sizes', () => {
    const { rerender } = render(<Button size="sm">Small</Button>)

    let button = screen.getByRole('button')
    expect(button).toHaveClass('h-9', 'px-3')

    rerender(<Button size="lg">Large</Button>)
    button = screen.getByRole('button')
    expect(button).toHaveClass('h-11', 'px-8')

    rerender(<Button size="icon">Icon</Button>)
    button = screen.getByRole('button')
    expect(button).toHaveClass('h-10', 'w-10')
  })

  it('should handle click events', async () => {
    const user = userEvent.setup()
    const handleClick = vi.fn()

    render(<Button onClick={handleClick}>Click me</Button>)

    const button = screen.getByRole('button')
    await user.click(button)

    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('should be disabled when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>)

    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
    expect(button).toHaveClass('disabled:pointer-events-none', 'disabled:opacity-50')
  })

  it('should accept custom className', () => {
    render(<Button className="custom-class">Custom</Button>)

    const button = screen.getByRole('button')
    expect(button).toHaveClass('custom-class')
  })

  it('should render as child component when asChild is true', () => {
    render(
      <Button asChild>
        <a href="/test">Link Button</a>
      </Button>
    )

    const link = screen.getByRole('link')
    expect(link).toBeInTheDocument()
    expect(link).toHaveAttribute('href', '/test')
    expect(link).toHaveClass('bg-primary')
  })

  it('should forward ref correctly', () => {
    const ref = React.createRef<HTMLButtonElement>()

    render(<Button ref={ref}>Ref Button</Button>)

    expect(ref.current).toBeInstanceOf(HTMLButtonElement)
    expect(ref.current?.textContent).toBe('Ref Button')
  })

  it('should spread additional props', () => {
    render(
      <Button data-testid="test-button" aria-label="Test button">
        Test
      </Button>
    )

    const button = screen.getByTestId('test-button')
    expect(button).toHaveAttribute('aria-label', 'Test button')
  })
})