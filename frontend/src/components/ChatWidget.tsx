import { useState, useRef, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../auth'
import { useChatResults } from '../chatResults'
import { fetchChatHistory, money, type ChatMatch } from '../api'
import HandsomeDan from './HandsomeDan'
import './chat.css'

interface Msg {
  role: 'user' | 'assistant'
  content: string
  products?: ChatMatch[]
}

const GREETING: Msg = {
  role: 'assistant',
  content:
    "Woof! I'm Handsome Dan, your Campus Customs shopping pup. 🐾 Ask me about our Yale " +
    "gear — styles, colors, sizes, prices, or what's in stock — and I'll fetch it for you!",
}

// How many recent turns to send back to the agent as context each turn.
const HISTORY_WINDOW = 16

export default function ChatWidget() {
  const { user, token } = useAuth()
  const { setResults } = useChatResults()
  const location = useLocation()
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Msg[]>([GREETING])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const bodyRef = useRef<HTMLDivElement>(null)

  // The product the shopper is currently viewing, parsed from the URL. This is the
  // page context sent to the agent so "do you have this in pink?" resolves.
  const pageProductId = location.pathname.startsWith('/products/')
    ? location.pathname.split('/products/')[1] || null
    : null

  useEffect(() => {
    bodyRef.current?.scrollTo({ top: bodyRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, open])

  // Reload saved history when a shopper logs in; reset to a clean greeting on logout.
  useEffect(() => {
    let cancelled = false
    if (!user || !token) {
      setMessages([GREETING])
      return
    }
    fetchChatHistory(token)
      .then(({ history }) => {
        if (cancelled) return
        const restored: Msg[] = history.map((t) => ({
          role: t.role,
          content: t.content,
          products: t.products,
        }))
        setMessages(restored.length > 0 ? [GREETING, ...restored] : [GREETING])
      })
      .catch(() => {
        if (!cancelled) setMessages([GREETING])
      })
    return () => {
      cancelled = true
    }
  }, [user, token])

  async function send() {
    const text = input.trim()
    if (!text || sending) return

    // Add the user's message AND an empty assistant placeholder immediately, so the
    // dot-dot-dot thinking indicator shows the instant they hit send — before the
    // network even responds — and stays until the first streamed token arrives.
    setMessages((m) => [
      ...m,
      { role: 'user', content: text },
      { role: 'assistant', content: '' },
    ])
    setInput('')
    setSending(true)

    // Send a recent window of the conversation (minus the canned greeting) as history.
    const history = messages
      .filter((m) => m !== GREETING)
      .slice(-HISTORY_WINDOW)
      .map((m) => ({ role: m.role, content: m.content }))

    // Updates the assistant placeholder we just appended (the last message).
    let assistantText = ''
    const updateLast = (patch: Partial<Msg>) =>
      setMessages((m) => {
        const copy = [...m]
        copy[copy.length - 1] = { ...copy[copy.length - 1], ...patch }
        return copy
      })

    try {
      const res = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          message: text,
          history,
          page_product_id: pageProductId,
        }),
      })
      if (!res.ok || !res.body) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data?.detail || `Request failed (${res.status})`)
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buf = ''
      let done = false
      while (!done) {
        const { value, done: rdDone } = await reader.read()
        done = rdDone
        buf += decoder.decode(value ?? new Uint8Array(), { stream: true })
        const parts = buf.split('\n\n')
        buf = parts.pop() ?? ''
        for (const part of parts) {
          const line = part.split('\n').find((l) => l.startsWith('data:'))
          if (!line) continue
          const evt = JSON.parse(line.slice(5).trim())
          if (evt.type === 'delta') {
            assistantText += evt.text
            updateLast({ content: assistantText })
          } else if (evt.type === 'final') {
            const products: ChatMatch[] = evt.products ?? []
            updateLast({ content: evt.reply || assistantText, products })
            if (products.length > 0) {
              setResults(text, products)
              window.scrollTo({ top: 0, behavior: 'smooth' })
            }
          } else if (evt.type === 'error') {
            throw new Error(evt.detail || 'stream error')
          }
        }
      }
    } catch (err) {
      // Fill the placeholder bubble with the error instead of leaving it thinking.
      updateLast({
        content:
          'Woof — I had trouble reaching the store just now. ' +
          (err instanceof Error ? err.message : ''),
      })
    } finally {
      setSending(false)
    }
  }

  return (
    <>
      {!open && (
        <button className="chat-fab" onClick={() => setOpen(true)} aria-label="Chat with Handsome Dan">
          <span className="chat-fab-dan"><HandsomeDan size={52} /></span>
          <span className="chat-fab-bubble">Handsome Dan here to help you look chic af</span>
        </button>
      )}

      {open && (
        <div className="chat-panel" role="dialog" aria-label="Chat with Handsome Dan">
          <div className="chat-head">
            <span className="chat-head-dan"><HandsomeDan size={40} /></span>
            <div className="chat-head-text">
              <strong>Handsome Dan</strong>
              <small>{user ? `sniffing out gear for ${user.first_name || user.name} 🐾` : 'your Campus Customs shopping pup 🐾'}</small>
            </div>
            <button className="chat-close" onClick={() => setOpen(false)} aria-label="Close chat">
              ✕
            </button>
          </div>

          <div className="chat-body" ref={bodyRef}>
            {messages.map((m, i) => (
              <div key={i} className="chat-turn">
                <div className={`chat-msg ${m.role}${m.content ? '' : ' typing'}`}>
                  {m.content || (m.role === 'assistant'
                    ? <span className="dots"><i></i><i></i><i></i></span>
                    : '')}
                </div>
                {m.products && m.products.length > 0 && (
                  <div className="chat-products">
                    {m.products.map((p) => (
                      <Link
                        to={`/products/${p.product_id}`}
                        key={p.product_id}
                        className="chat-product"
                        onClick={() => setOpen(false)}
                      >
                        <img src={p.image_url} alt={p.name} loading="lazy" />
                        <div className="chat-product-info">
                          <span className="chat-product-name">{p.name}</span>
                          <span className="chat-product-price">{money(p.price)}</span>
                        </div>
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          <form
            className="chat-input"
            onSubmit={(e) => {
              e.preventDefault()
              send()
            }}
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about our Yale gear…"
              aria-label="Message"
            />
            <button type="submit" className="btn" disabled={sending || !input.trim()}>
              Send
            </button>
          </form>
        </div>
      )}
    </>
  )
}
