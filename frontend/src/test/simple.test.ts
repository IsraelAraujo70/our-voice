import { describe, it, expect } from 'vitest'

describe('Simple Test', () => {
  it('should verify test setup works', () => {
    expect(1 + 1).toBe(2)
  })

  it('should verify environment setup', () => {
    expect(process.env.NEXT_PUBLIC_API_BASE_URL).toBe('http://localhost:8000/api')
  })
})