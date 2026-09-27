import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'

export interface User {
  id: number
  email: string
  first_name: string | null
  last_name: string | null
  name: string
}

interface AuthContextValue {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  signup: (
    first_name: string,
    last_name: string,
    email: string,
    password: string,
  ) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)
const STORAGE_KEY = 'cc_user'
const TOKEN_KEY = 'cc_token'

async function postJSON(url: string, body: unknown): Promise<{ user: User; token: string }> {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    // FastAPI: string detail (our errors) or array (422 validation)
    const detail = data?.detail
    const msg = Array.isArray(detail)
      ? detail.map((d: { msg: string }) => d.msg).join('; ')
      : detail || `Request failed (${res.status})`
    throw new Error(msg)
  }
  return data
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    const savedToken = localStorage.getItem(TOKEN_KEY)
    if (saved && savedToken) {
      try {
        setUser(JSON.parse(saved))
        setToken(savedToken)
      } catch {
        localStorage.removeItem(STORAGE_KEY)
        localStorage.removeItem(TOKEN_KEY)
      }
    }
  }, [])

  function persist(u: User, t: string) {
    setUser(u)
    setToken(t)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(u))
    localStorage.setItem(TOKEN_KEY, t)
  }

  async function login(email: string, password: string) {
    const { user, token } = await postJSON('/api/login', { email, password })
    persist(user, token)
  }

  async function signup(
    first_name: string,
    last_name: string,
    email: string,
    password: string,
  ) {
    const { user, token } = await postJSON('/api/signup', { first_name, last_name, email, password })
    persist(user, token)
  }

  function logout() {
    setUser(null)
    setToken(null)
    localStorage.removeItem(STORAGE_KEY)
    localStorage.removeItem(TOKEN_KEY)
  }

  return (
    <AuthContext.Provider value={{ user, token, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
