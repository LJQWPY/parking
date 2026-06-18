const TOKEN_KEY = 'auth_token'
const USER_KEY = 'auth_user'

const storage = {
  getToken: (): string | null => {
    return localStorage.getItem(TOKEN_KEY)
  },
  
  setToken: (token: string): void => {
    localStorage.setItem(TOKEN_KEY, token)
  },
  
  removeToken: (): void => {
    localStorage.removeItem(TOKEN_KEY)
  },
  
  getUser: (): any => {
    const userStr = localStorage.getItem(USER_KEY)
    return userStr ? JSON.parse(userStr) : null
  },
  
  setUser: (user: any): void => {
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  },
  
  removeUser: (): void => {
    localStorage.removeItem(USER_KEY)
  }
}

export default storage
