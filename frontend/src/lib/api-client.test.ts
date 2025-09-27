import { describe, it, expect, vi, beforeEach } from 'vitest'
import { apiFetch, resolveMediaUrl, computeApiBaseOrigin, API_BASE_URL } from './api-client'

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

describe('API Client', () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  describe('computeApiBaseOrigin', () => {
    it('should compute origin from API URL with /api path', () => {
      const result = computeApiBaseOrigin('http://localhost:8000/api')
      expect(result).toBe('http://localhost:8000')
    })

    it('should compute origin from API URL without /api path', () => {
      const result = computeApiBaseOrigin('http://localhost:8000')
      expect(result).toBe('http://localhost:8000')
    })

    it('should handle URLs with trailing slash', () => {
      const result = computeApiBaseOrigin('http://localhost:8000/api/')
      expect(result).toBe('http://localhost:8000')
    })

    it('should handle URLs with path segments', () => {
      const result = computeApiBaseOrigin('https://api.example.com/v1/api')
      expect(result).toBe('https://api.example.com/v1')
    })

    it('should handle invalid URLs gracefully', () => {
      const result = computeApiBaseOrigin('not-a-url')
      expect(result).toBe('not-a-url')
    })

    it('should remove trailing slash from fallback', () => {
      const result = computeApiBaseOrigin('invalid-url/')
      expect(result).toBe('invalid-url')
    })
  })

  describe('resolveMediaUrl', () => {
    it('should return undefined for null or undefined path', () => {
      expect(resolveMediaUrl(null)).toBeUndefined()
      expect(resolveMediaUrl(undefined)).toBeUndefined()
    })

    it('should return absolute URLs unchanged', () => {
      const httpsUrl = 'https://example.com/image.jpg'
      const httpUrl = 'http://example.com/image.jpg'

      expect(resolveMediaUrl(httpsUrl)).toBe(httpsUrl)
      expect(resolveMediaUrl(httpUrl)).toBe(httpUrl)
    })

    it('should resolve relative paths with leading slash', () => {
      const result = resolveMediaUrl('/media/image.jpg')
      expect(result).toContain('/media/image.jpg')
    })

    it('should resolve relative paths without leading slash', () => {
      const result = resolveMediaUrl('media/image.jpg')
      expect(result).toContain('/media/image.jpg')
    })

    it('should handle empty string path', () => {
      expect(resolveMediaUrl('')).toBeUndefined()
    })
  })

  describe('apiFetch', () => {
    it('should make successful API call', async () => {
      const mockData = { message: 'success' }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: vi.fn().mockResolvedValueOnce(mockData),
      })

      const result = await apiFetch('/test')

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_BASE_URL}/test`,
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      )
      expect(result).toEqual(mockData)
    })

    it('should handle custom headers', async () => {
      const mockData = { data: 'test' }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: vi.fn().mockResolvedValueOnce(mockData),
      })

      await apiFetch('/test', {
        headers: {
          'Authorization': 'Bearer token',
          'Custom-Header': 'value',
        },
      })

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer token',
            'Custom-Header': 'value',
          }),
        })
      )
    })

    it('should handle custom request options', async () => {
      const mockData = { success: true }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: vi.fn().mockResolvedValueOnce(mockData),
      })

      await apiFetch('/test', {
        method: 'POST',
        body: JSON.stringify({ test: 'data' }),
      })

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          method: 'POST',
          body: '{"test":"data"}',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      )
    })

    it('should throw error for unsuccessful response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: vi.fn().mockResolvedValueOnce('Resource not found'),
      })

      await expect(apiFetch('/nonexistent')).rejects.toThrow('Resource not found')
    })

    it('should throw error with status text when response body is empty', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: vi.fn().mockResolvedValueOnce(''),
      })

      await expect(apiFetch('/error')).rejects.toThrow('Internal Server Error')
    })

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'))

      await expect(apiFetch('/test')).rejects.toThrow('Network error')
    })

    it('should handle JSON parsing errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: vi.fn().mockRejectedValueOnce(new Error('Invalid JSON')),
      })

      await expect(apiFetch('/test')).rejects.toThrow('Invalid JSON')
    })

    it('should accept Request object as input', async () => {
      const mockData = { result: 'success' }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: vi.fn().mockResolvedValueOnce(mockData),
      })

      const request = new Request('/test')
      await apiFetch(request)

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_BASE_URL}/test`,
        expect.any(Object)
      )
    })
  })
})