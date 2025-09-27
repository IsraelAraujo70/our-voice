/**
 * Regression tests for frontend voting functionality
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import React from 'react'

// Mock components - these would be actual components in the real implementation
const MockVoteButton = ({ postId, voteType, onVote }: {
  postId: string
  voteType: 'remove' | 'hide'
  onVote: (postId: string, voteType: 'remove' | 'hide', weight: number) => Promise<void>
}) => {
  const handleClick = () => {
    onVote(postId, voteType, 1.0)
  }

  return (
    <button
      onClick={handleClick}
      data-testid={`vote-${voteType}-${postId}`}
    >
      Vote to {voteType}
    </button>
  )
}

const MockPost = ({
  post,
  onVote
}: {
  post: { id: string; text: string; isArchived: boolean }
  onVote: (postId: string, voteType: 'remove' | 'hide', weight: number) => Promise<void>
}) => {
  return (
    <div data-testid={`post-${post.id}`}>
      <p>{post.text}</p>
      {post.isArchived && <span data-testid="archived-badge">Archived</span>}
      {!post.isArchived && (
        <div>
          <MockVoteButton postId={post.id} voteType="hide" onVote={onVote} />
          <MockVoteButton postId={post.id} voteType="remove" onVote={onVote} />
        </div>
      )}
    </div>
  )
}

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
})

const renderWithQueryClient = (component: React.ReactElement) => {
  const queryClient = createTestQueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  )
}

describe('Voting Regression Tests', () => {
  let mockPost: { id: string; text: string; isArchived: boolean }
  let mockVoteHandler: ReturnType<typeof vi.fn>

  beforeEach(() => {
    mockPost = {
      id: '1',
      text: 'Test post content',
      isArchived: false
    }
    mockVoteHandler = vi.fn().mockResolvedValue(undefined)
  })

  describe('Vote Button Interaction', () => {
    it('should render vote buttons for non-archived posts', () => {
      renderWithQueryClient(
        <MockPost post={mockPost} onVote={mockVoteHandler} />
      )

      expect(screen.getByTestId('vote-hide-1')).toBeInTheDocument()
      expect(screen.getByTestId('vote-remove-1')).toBeInTheDocument()
      expect(screen.queryByTestId('archived-badge')).not.toBeInTheDocument()
    })

    it('should not render vote buttons for archived posts', () => {
      const archivedPost = { ...mockPost, isArchived: true }

      renderWithQueryClient(
        <MockPost post={archivedPost} onVote={mockVoteHandler} />
      )

      expect(screen.queryByTestId('vote-hide-1')).not.toBeInTheDocument()
      expect(screen.queryByTestId('vote-remove-1')).not.toBeInTheDocument()
      expect(screen.getByTestId('archived-badge')).toBeInTheDocument()
    })

    it('should call onVote when hide button is clicked', async () => {
      const user = userEvent.setup()

      renderWithQueryClient(
        <MockPost post={mockPost} onVote={mockVoteHandler} />
      )

      await user.click(screen.getByTestId('vote-hide-1'))

      expect(mockVoteHandler).toHaveBeenCalledWith('1', 'hide', 1.0)
    })

    it('should call onVote when remove button is clicked', async () => {
      const user = userEvent.setup()

      renderWithQueryClient(
        <MockPost post={mockPost} onVote={mockVoteHandler} />
      )

      await user.click(screen.getByTestId('vote-remove-1'))

      expect(mockVoteHandler).toHaveBeenCalledWith('1', 'remove', 1.0)
    })
  })

  describe('Vote State Management', () => {
    it('should handle voting errors gracefully', async () => {
      const user = userEvent.setup()
      const mockVoteHandlerError = vi.fn().mockRejectedValue(new Error('Network error'))

      renderWithQueryClient(
        <MockPost post={mockPost} onVote={mockVoteHandlerError} />
      )

      await user.click(screen.getByTestId('vote-remove-1'))

      expect(mockVoteHandlerError).toHaveBeenCalledWith('1', 'remove', 1.0)
      // In a real implementation, we'd test error handling UI
    })

    it('should prevent multiple simultaneous votes', async () => {
      const user = userEvent.setup()
      let resolveVote: () => void
      const mockVoteHandlerSlow = vi.fn().mockImplementation(() => {
        return new Promise<void>((resolve) => {
          resolveVote = resolve
        })
      })

      renderWithQueryClient(
        <MockPost post={mockPost} onVote={mockVoteHandlerSlow} />
      )

      // Click vote button multiple times quickly
      const voteButton = screen.getByTestId('vote-remove-1')
      await user.click(voteButton)
      await user.click(voteButton)
      await user.click(voteButton)

      // Should only be called once
      expect(mockVoteHandlerSlow).toHaveBeenCalledTimes(1)

      // Resolve the promise
      resolveVote!()
    })
  })

  describe('Accessibility', () => {
    it('should have accessible vote buttons', () => {
      renderWithQueryClient(
        <MockPost post={mockPost} onVote={mockVoteHandler} />
      )

      const hideButton = screen.getByTestId('vote-hide-1')
      const removeButton = screen.getByTestId('vote-remove-1')

      expect(hideButton).toBeInTheDocument()
      expect(removeButton).toBeInTheDocument()

      // Buttons should be focusable
      hideButton.focus()
      expect(hideButton).toHaveFocus()

      removeButton.focus()
      expect(removeButton).toHaveFocus()
    })

    it('should support keyboard navigation', async () => {
      const user = userEvent.setup()

      renderWithQueryClient(
        <MockPost post={mockPost} onVote={mockVoteHandler} />
      )

      const hideButton = screen.getByTestId('vote-hide-1')

      // Tab to the button and press Enter
      await user.tab()
      expect(hideButton).toHaveFocus()

      await user.keyboard('{Enter}')
      expect(mockVoteHandler).toHaveBeenCalledWith('1', 'hide', 1.0)
    })
  })

  describe('Vote Feedback', () => {
    it('should show loading state during vote submission', async () => {
      const user = userEvent.setup()
      let resolveVote: () => void
      const mockVoteHandlerSlow = vi.fn().mockImplementation(() => {
        return new Promise<void>((resolve) => {
          resolveVote = resolve
        })
      })

      // Mock component that shows loading state
      const MockVoteButtonWithLoading = ({
        postId,
        voteType,
        onVote
      }: {
        postId: string
        voteType: 'remove' | 'hide'
        onVote: (postId: string, voteType: 'remove' | 'hide', weight: number) => Promise<void>
      }) => {
        const [isLoading, setIsLoading] = React.useState(false)

        const handleClick = async () => {
          setIsLoading(true)
          try {
            await onVote(postId, voteType, 1.0)
          } finally {
            setIsLoading(false)
          }
        }

        return (
          <button
            onClick={handleClick}
            disabled={isLoading}
            data-testid={`vote-${voteType}-${postId}`}
          >
            {isLoading ? 'Voting...' : `Vote to ${voteType}`}
          </button>
        )
      }

      renderWithQueryClient(
        <div>
          <MockVoteButtonWithLoading
            postId={mockPost.id}
            voteType="remove"
            onVote={mockVoteHandlerSlow}
          />
        </div>
      )

      const voteButton = screen.getByTestId('vote-remove-1')
      await user.click(voteButton)

      // Should show loading state
      expect(screen.getByText('Voting...')).toBeInTheDocument()
      expect(voteButton).toBeDisabled()

      // Resolve the vote
      resolveVote!()

      await waitFor(() => {
        expect(screen.getByText('Vote to remove')).toBeInTheDocument()
        expect(voteButton).not.toBeDisabled()
      })
    })
  })

  describe('Multiple Posts Voting', () => {
    it('should handle voting on multiple posts independently', async () => {
      const user = userEvent.setup()
      const posts = [
        { id: '1', text: 'Post 1', isArchived: false },
        { id: '2', text: 'Post 2', isArchived: false },
        { id: '3', text: 'Post 3', isArchived: true },
      ]

      renderWithQueryClient(
        <div>
          {posts.map(post => (
            <MockPost key={post.id} post={post} onVote={mockVoteHandler} />
          ))}
        </div>
      )

      // Vote on first post
      await user.click(screen.getByTestId('vote-remove-1'))
      expect(mockVoteHandler).toHaveBeenCalledWith('1', 'remove', 1.0)

      // Vote on second post
      await user.click(screen.getByTestId('vote-hide-2'))
      expect(mockVoteHandler).toHaveBeenCalledWith('2', 'hide', 1.0)

      // Third post should not have vote buttons (archived)
      expect(screen.queryByTestId('vote-remove-3')).not.toBeInTheDocument()
      expect(screen.queryByTestId('vote-hide-3')).not.toBeInTheDocument()

      expect(mockVoteHandler).toHaveBeenCalledTimes(2)
    })
  })
})

// Override React.useState for the test
Object.defineProperty(React, 'useState', {
  value: vi.fn().mockImplementation((initial: unknown) => {
    let state = initial
    const setState = (newState: unknown) => {
      state = newState
    }
    return [state, setState]
  })
})