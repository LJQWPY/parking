import { create } from 'zustand'

interface AppState {
  collapsed: boolean
  loading: boolean
  setCollapsed: (collapsed: boolean) => void
  toggleCollapsed: () => void
  setLoading: (loading: boolean) => void
}

export const useAppStore = create<AppState>((set) => ({
  collapsed: false,
  loading: false,
  
  setCollapsed: (collapsed: boolean) => set({ collapsed }),
  
  toggleCollapsed: () => set((state) => ({ collapsed: !state.collapsed })),
  
  setLoading: (loading: boolean) => set({ loading })
}))
