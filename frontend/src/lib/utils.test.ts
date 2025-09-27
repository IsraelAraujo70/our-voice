import { describe, it, expect } from 'vitest'
import { cn } from './utils'

describe('Utils', () => {
  describe('cn function', () => {
    it('should combine class names correctly', () => {
      const result = cn('class1', 'class2')
      expect(result).toBe('class1 class2')
    })

    it('should handle conditional class names', () => {
      const isActive = true
      const isDisabled = false

      const result = cn(
        'base-class',
        isActive && 'active-class',
        isDisabled && 'disabled-class'
      )

      expect(result).toBe('base-class active-class')
    })

    it('should merge conflicting Tailwind classes', () => {
      // twMerge should prioritize the last class when there are conflicts
      const result = cn('px-2', 'px-4')
      expect(result).toBe('px-4')
    })

    it('should handle arrays of class names', () => {
      const result = cn(['class1', 'class2'], 'class3')
      expect(result).toBe('class1 class2 class3')
    })

    it('should handle objects with conditional classes', () => {
      const result = cn({
        'always-present': true,
        'conditional-true': true,
        'conditional-false': false
      })

      expect(result).toBe('always-present conditional-true')
    })

    it('should handle undefined and null values', () => {
      const result = cn('valid-class', undefined, null, 'another-class')
      expect(result).toBe('valid-class another-class')
    })

    it('should handle empty strings', () => {
      const result = cn('', 'valid-class', '')
      expect(result).toBe('valid-class')
    })

    it('should handle complex Tailwind class merging', () => {
      // Test common patterns in the codebase
      const result = cn(
        'bg-primary text-white px-4 py-2',
        'bg-secondary', // Should override bg-primary
        'text-black'    // Should override text-white
      )

      expect(result).toBe('px-4 py-2 bg-secondary text-black')
    })

    it('should work with real button variant classes', () => {
      // Test with actual classes from Button component
      const result = cn(
        'inline-flex items-center justify-center rounded-md text-sm font-medium',
        'bg-primary text-primary-foreground hover:bg-primary/90',
        'h-10 px-4 py-2'
      )

      expect(result).toContain('inline-flex')
      expect(result).toContain('bg-primary')
      expect(result).toContain('h-10')
    })

    it('should handle responsive classes', () => {
      const result = cn('w-full', 'md:w-auto', 'lg:w-1/2')
      expect(result).toBe('w-full md:w-auto lg:w-1/2')
    })
  })
})