import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { fetchProducts, money, type ProductCard } from '../api'
import './pages.css'

export default function Products() {
  const [products, setProducts] = useState<ProductCard[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchParams, setSearchParams] = useSearchParams()

  const category = searchParams.get('category') || 'All'
  const q = searchParams.get('q') || ''

  useEffect(() => {
    fetchProducts()
      .then(setProducts)
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false))
  }, [])

  const categories = useMemo(
    () => ['All', ...Array.from(new Set(products.map((p) => p.garment_type))).sort()],
    [products],
  )

  const shown = useMemo(() => {
    let list = products
    if (category !== 'All') list = list.filter((p) => p.garment_type === category)
    if (q) {
      // Word-boundary match so "Art" (School of Art) doesn't also match "quARTer-zip".
      const escaped = q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
      const re = new RegExp(`\\b${escaped}\\b`, 'i')
      list = list.filter((p) =>
        re.test(`${p.name} ${p.garment_type} ${p.short_description} ${p.colors.join(' ')}`),
      )
    }
    return list
  }, [products, category, q])

  function setCategory(c: string) {
    const next = new URLSearchParams(searchParams)
    if (c === 'All') next.delete('category')
    else next.set('category', c)
    setSearchParams(next)
  }

  function clearQuery() {
    const next = new URLSearchParams(searchParams)
    next.delete('q')
    setSearchParams(next)
  }

  return (
    <div className="container products-page">
      <header className="page-head">
        <h1>{q ? `"${q}"` : category !== 'All' ? category : 'Shop All Products'}</h1>
        <p>
          {shown.length} {shown.length === 1 ? 'style' : 'styles'}
          {q && (
            <>
              {' '}matching your search ·{' '}
              <button className="linklike" onClick={clearQuery}>clear</button>
            </>
          )}
        </p>
      </header>

      {!loading && !error && (
        <div className="filters">
          {categories.map((c) => (
            <button
              key={c}
              className={c === category ? 'chip active' : 'chip'}
              onClick={() => setCategory(c)}
            >
              {c}
            </button>
          ))}
        </div>
      )}

      {loading && <p className="muted">Loading products…</p>}
      {error && (
        <p className="error">
          Couldn't load products ({error}). Is the backend running on port 8000?
        </p>
      )}
      {!loading && !error && shown.length === 0 && (
        <p className="muted">No products match. Try another category or search.</p>
      )}

      <div className="grid">
        {shown.map((p) => (
          <Link to={`/products/${p.product_id}`} key={p.product_id} className="card">
            <div className="card-img">
              <img src={p.image_url} alt={p.name} loading="lazy" />
            </div>
            <div className="card-body">
              <span className="card-type">{p.garment_type}</span>
              <h3 className="card-name">{p.name}</h3>
              <p className="card-desc">{p.short_description}</p>
              <div className="card-foot">
                <span className="price">{money(p.price)}</span>
                <span className="view">View →</span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
