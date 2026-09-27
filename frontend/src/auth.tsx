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

async function postJSON(url: string, body: unknown): Promise<{ user: User }> {
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

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      try {
        setUser(JSON.parse(saved))
      } catch {
        localStorage.removeItem(STORAGE_KEY)
      }
    }
  }, [])

  function persist(u: User) {
    setUser(u)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(u))
  }

  async function login(email: string, password: string) {
    const { user } = await postJSON('/api/login', { email, password })
    persist(user)
  }

  async function signup(
    first_name: string,
    last_name: string,
    email: string,
    password: string,
  ) {
    await postJSON('/api/signup', { first_name, last_name, email, password })
    // Auto-login straight after a successful signup.
    await login(email, password)
  }

  function logout() {
    setUser(null)
    localStorage.removeItem(STORAGE_KEY)
  }

  return (
    <AuthContext.Provider value={{ user, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
