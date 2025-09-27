/**
 * Regression tests for frontend voting functionality using real PostCard component
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import React from 'react'
import { PostCard, PostCardProps } from '@/components/feed/post-card'

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

describe('PostCard Voting Regression Tests', () => {
  let mockPost: PostCardProps

  beforeEach(() => {
    mockPost = {
      author: {
        handle: 'testuser',
        displayName: 'Test User',
        avatarUrl: 'https://example.com/avatar.jpg'
      },
      createdAt: '2h',
      text: 'Test post content for voting functionality',
      counts: {
        likes: 5,
        replies: 2,
        reposts: 1,
        votes: 3
      },
      archived: false
    }
  })

  describe('PostCard Rendering', () => {
    it('should render post card with author information', () => {
      renderWithQueryClient(<PostCard {...mockPost} />)

      expect(screen.getByText('Test User')).toBeInTheDocument()
      expect(screen.getByText('@testuser')).toBeInTheDocument()
      expect(screen.getByText('2h')).toBeInTheDocument()
      expect(screen.getByText('Test post content for voting functionality')).toBeInTheDocument()
    })

    it('should show voting button for non-archived posts', () => {
      renderWithQueryClient(<PostCard {...mockPost} />)

      const voteButton = screen.getByLabelText('Votar remover')
      expect(voteButton).toBeInTheDocument()
      expect(screen.getByText('3')).toBeInTheDocument() // vote count
    })

    it('should show archived badge for archived posts', () => {
      const archivedPost = { ...mockPost, archived: true }

      renderWithQueryClient(<PostCard {...archivedPost} />)

      expect(screen.getByText('Arquivado pela comunidade')).toBeInTheDocument()
    })

    it('should display interaction counts correctly', () => {
      renderWithQueryClient(<PostCard {...mockPost} />)

      expect(screen.getByText('5')).toBeInTheDocument() // likes count
      expect(screen.getByText('2')).toBeInTheDocument() // replies count
      expect(screen.getByText('1')).toBeInTheDocument() // reposts count
      expect(screen.getByText('3')).toBeInTheDocument() // votes count
    })

    it('should render all action buttons', () => {
      renderWithQueryClient(<PostCard {...mockPost} />)

      expect(screen.getByLabelText('Curtir')).toBeInTheDocument()
      expect(screen.getByLabelText('Debater')).toBeInTheDocument()
      expect(screen.getByLabelText('Repostar')).toBeInTheDocument()
      expect(screen.getByLabelText('Salvar')).toBeInTheDocument()
      expect(screen.getByLabelText('Votar remover')).toBeInTheDocument()
    })
  })

  describe('PostCard Content Display', () => {
    it('should render post with image when imageUrl is provided', () => {
      const postWithImage = {
        ...mockPost,
        imageUrl: 'https://example.com/image.jpg'
      }

      renderWithQueryClient(<PostCard {...postWithImage} />)

      const image = screen.getByAltText('Imagem do post')
      expect(image).toBeInTheDocument()
      expect(image).toHaveAttribute('src', expect.stringContaining('image.jpg'))
    })

    it('should render post without image when imageUrl is not provided', () => {
      renderWithQueryClient(<PostCard {...mockPost} />)

      expect(screen.queryByAltText('Imagem do post')).not.toBeInTheDocument()
    })

    it('should display multiline text content correctly', () => {
      const postWithMultilineText = {
        ...mockPost,
        text: 'First line\nSecond line\nThird line'
      }

      renderWithQueryClient(<PostCard {...postWithMultilineText} />)

      expect(screen.getByText('First line\nSecond line\nThird line')).toBeInTheDocument()
    })
  })

  describe('PostCard Accessibility', () => {
    it('should have accessible action buttons', () => {
      renderWithQueryClient(<PostCard {...mockPost} />)

      const voteButton = screen.getByLabelText('Votar remover')
      const likeButton = screen.getByLabelText('Curtir')
      const replyButton = screen.getByLabelText('Debater')
      const repostButton = screen.getByLabelText('Repostar')
      const saveButton = screen.getByLabelText('Salvar')

      expect(voteButton).toBeInTheDocument()
      expect(likeButton).toBeInTheDocument()
      expect(replyButton).toBeInTheDocument()
      expect(repostButton).toBeInTheDocument()
      expect(saveButton).toBeInTheDocument()
    })

    it('should support keyboard navigation for action buttons', () => {
      renderWithQueryClient(<PostCard {...mockPost} />)

      const historyButton = screen.getByText('Histórico')
      const voteButton = screen.getByLabelText('Votar remover')

      // Buttons should be focusable
      historyButton.focus()
      expect(historyButton).toHaveFocus()

      voteButton.focus()
      expect(voteButton).toHaveFocus()
    })
  })

  describe('PostCard Avatar Display', () => {
    it('should display avatar image when avatarUrl is provided', () => {
      renderWithQueryClient(<PostCard {...mockPost} />)

      const avatar = screen.getByAltText('Test User')
      expect(avatar).toBeInTheDocument()
      expect(avatar).toHaveAttribute('src', expect.stringContaining('avatar.jpg'))
    })

    it('should display fallback initials when avatarUrl is not provided', () => {
      const postWithoutAvatar = {
        ...mockPost,
        author: {
          ...mockPost.author,
          avatarUrl: undefined
        }
      }

      renderWithQueryClient(<PostCard {...postWithoutAvatar} />)

      expect(screen.getByText('TU')).toBeInTheDocument() // Test User initials
    })
  })

  describe('PostCard Edge Cases', () => {
    it('should handle zero counts correctly', () => {
      const postWithZeroCounts = {
        ...mockPost,
        counts: {
          likes: 0,
          replies: 0,
          reposts: 0,
          votes: 0
        }
      }

      renderWithQueryClient(<PostCard {...postWithZeroCounts} />)

      // All counts should show as 0
      const zeroElements = screen.getAllByText('0')
      expect(zeroElements).toHaveLength(5) // likes, replies, reposts, saves, votes
    })

    it('should handle long author names correctly', () => {
      const postWithLongName = {
        ...mockPost,
        author: {
          ...mockPost.author,
          displayName: 'Very Long Display Name That Might Wrap',
          handle: 'verylonghandlethatmightwraporsomething'
        }
      }

      renderWithQueryClient(<PostCard {...postWithLongName} />)

      expect(screen.getByText('Very Long Display Name That Might Wrap')).toBeInTheDocument()
      expect(screen.getByText('@verylonghandlethatmightwraporsomething')).toBeInTheDocument()
    })

    it('should handle empty post text', () => {
      const postWithEmptyText = {
        ...mockPost,
        text: ''
      }

      renderWithQueryClient(<PostCard {...postWithEmptyText} />)

      // Post should still render with empty content
      expect(screen.getByText('Test User')).toBeInTheDocument()
      expect(screen.getByText('@testuser')).toBeInTheDocument()
    })

    it('should render time correctly', () => {
      const postWithDifferentTime = {
        ...mockPost,
        createdAt: '5min'
      }

      renderWithQueryClient(<PostCard {...postWithDifferentTime} />)

      expect(screen.getByText('5min')).toBeInTheDocument()
    })
  })
})