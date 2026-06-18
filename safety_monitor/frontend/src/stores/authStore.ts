import { create } from 'zustand'
import type { User } from '../api/types'
import storage from '../utils/storage'

interface AuthState {
  token: string | null
  user: User | null
  isAuthenticated: boolean
  login: (token: string, user: User) => void
  logout: () => void
  setUser: (user: User) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: storage.getToken(),
  user: storage.getUser(),
  isAuthenticated: !!storage.getToken(),
  
  login: (token: string, user: User) => {
    storage.setToken(token)
    storage.setUser(user)
    set({ token, user, isAuthenticated: true })
  },
  
  logout: () => {
    storage.removeToken()
    storage.removeUser()
    set({ token: null, user: null, isAuthenticated: false })
  },
  
  setUser: (user: User) => {
    storage.setUser(user)
    set({ user })
  }
}))
