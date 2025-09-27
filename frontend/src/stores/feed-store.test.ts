import { describe, it, expect, beforeEach } from 'vitest'
import { useFeedStore } from './feed-store'

describe('FeedStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useFeedStore.setState({ activeTab: 'following' })
  })

  it('should have initial state', () => {
    const state = useFeedStore.getState()

    expect(state.activeTab).toBe('following')
    expect(typeof state.setActiveTab).toBe('function')
  })

  it('should update active tab to popular', () => {
    const { setActiveTab } = useFeedStore.getState()

    setActiveTab('popular')

    const state = useFeedStore.getState()
    expect(state.activeTab).toBe('popular')
  })

  it('should update active tab to archived', () => {
    const { setActiveTab } = useFeedStore.getState()

    setActiveTab('archived')

    const state = useFeedStore.getState()
    expect(state.activeTab).toBe('archived')
  })

  it('should update active tab back to following', () => {
    const { setActiveTab } = useFeedStore.getState()

    // Change to different tab first
    setActiveTab('popular')
    expect(useFeedStore.getState().activeTab).toBe('popular')

    // Change back to following
    setActiveTab('following')
    expect(useFeedStore.getState().activeTab).toBe('following')
  })

  it('should handle multiple state changes', () => {
    const { setActiveTab } = useFeedStore.getState()

    setActiveTab('popular')
    expect(useFeedStore.getState().activeTab).toBe('popular')

    setActiveTab('archived')
    expect(useFeedStore.getState().activeTab).toBe('archived')

    setActiveTab('following')
    expect(useFeedStore.getState().activeTab).toBe('following')
  })

  it('should maintain function reference stability', () => {
    const initialSetActiveTab = useFeedStore.getState().setActiveTab

    // Call setActiveTab to trigger state change
    initialSetActiveTab('popular')

    const newSetActiveTab = useFeedStore.getState().setActiveTab

    // Function reference should remain the same
    expect(initialSetActiveTab).toBe(newSetActiveTab)
  })

  it('should work with subscriptions', () => {
    let currentTab = useFeedStore.getState().activeTab

    // Subscribe to store changes
    const unsubscribe = useFeedStore.subscribe((state) => {
      currentTab = state.activeTab
    })

    // Change tab
    useFeedStore.getState().setActiveTab('archived')

    expect(currentTab).toBe('archived')

    // Cleanup
    unsubscribe()
  })
})