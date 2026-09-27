import { createContext, useContext, useState, type ReactNode } from 'react'
import type { ChatMatch } from './api'

interface ChatResultsValue {
  matches: ChatMatch[]
  query: string
  setResults: (query: string, matches: ChatMatch[]) => void
  clear: () => void
}

const ChatResultsContext = createContext<ChatResultsValue | null>(null)

export function ChatResultsProvider({ children }: { children: ReactNode }) {
  const [matches, setMatches] = useState<ChatMatch[]>([])
  const [query, setQuery] = useState('')

  function setResults(q: string, m: ChatMatch[]) {
    setQuery(q)
    setMatches(m)
  }
  function clear() {
    setQuery('')
    setMatches([])
  }

  return (
    <ChatResultsContext.Provider value={{ matches, query, setResults, clear }}>
      {children}
    </ChatResultsContext.Provider>
  )
}

export function useChatResults(): ChatResultsValue {
  const ctx = useContext(ChatResultsContext)
  if (!ctx) throw new Error('useChatResults must be used within ChatResultsProvider')
  return ctx
}
