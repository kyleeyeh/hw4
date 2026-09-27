// Typed client for the Campus Customs backend.

export interface ProductCard {
  product_id: string
  name: string
  garment_type: string
  price: number
  colors: string[]
  short_description: string
  image_url: string
}

export interface SizeStock {
  size: string
  quantity: number
}

export interface ProductDetail {
  product_id: string
  name: string
  garment_type: string
  description: string
  colors: string[]
  search_tags: string[]
  price: number
  image_url: string
  inventory: SizeStock[]
  total_stock: number
}

async function getJSON<T>(url: string): Promise<T> {
  const res = await fetch(url)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json() as Promise<T>
}

export const fetchProducts = () => getJSON<ProductCard[]>('/api/products')
export const fetchProduct = (id: string) =>
  getJSON<ProductDetail>(`/api/products/${id}`)

export const money = (n: number) => `$${n.toFixed(0)}`

// Full product match returned by the chat agent (backend ProductCard shape).
// Distinct from the grid's ProductCard, which carries a precomputed short_description.
export interface ChatMatch {
  product_id: string
  name: string
  garment_type: string
  description: string
  colors: string[]
  price: number
  image_url: string
  total_stock: number
}

// A grid-card-length blurb from a full description.
export const shortInfo = (text: string, limit = 90): string => {
  const t = (text || '').trim()
  if (t.length <= limit) return t
  return t.slice(0, limit).replace(/\s+\S*$/, '') + '…'
}

// Saved chat turn returned by GET /api/chat/history.
export interface HistoryTurn {
  role: 'user' | 'assistant'
  content: string
  products: ChatMatch[]
  created_at: string
}

// History is scoped to the caller's own token — the server ignores any id in the URL.
export async function fetchChatHistory(token: string): Promise<{ history: HistoryTurn[] }> {
  const res = await fetch('/api/chat/history', {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json() as Promise<{ history: HistoryTurn[] }>
}
