import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

export const useAuth = () => {
  const navigate = useNavigate()
  const { token, user, isAuthenticated, login, logout } = useAuthStore()
  
  const checkAuth = () => {
    if (!isAuthenticated) {
      navigate('/login')
      return false
    }
    return true
  }
  
  return {
    token,
    user,
    isAuthenticated,
    login,
    logout,
    checkAuth
  }
}
