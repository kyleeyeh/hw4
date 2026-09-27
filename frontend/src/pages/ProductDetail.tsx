import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { fetchProduct, money, type ProductDetail as Detail } from '../api'
import './pages.css'

function stockLabel(qty: number): { text: string; cls: string } {
  if (qty === 0) return { text: 'Sold out', cls: 'out' }
  if (qty < 5) return { text: `Only ${qty} left`, cls: 'low' }
  return { text: 'In stock', cls: 'ok' }
}

export default function ProductDetail() {
  const { id } = useParams<{ id: string }>()
  const [product, setProduct] = useState<Detail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedSize, setSelectedSize] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    setLoading(true)
    fetchProduct(id)
      .then(setProduct)
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <p className="container muted pad">Loading…</p>
  if (error || !product)
    return (
      <div className="container pad">
        <p className="error">Product not found.</p>
        <Link to="/products" className="btn btn-outline">← Back to products</Link>
      </div>
    )

  return (
    <div className="container detail">
      <Link to="/products" className="back-link">← All products</Link>

      <div className="detail-grid">
        <div className="detail-img">
          <img src={product.image_url} alt={product.name} />
        </div>

        <div className="detail-info">
          <span className="card-type">{product.garment_type}</span>
          <h1>{product.name}</h1>
          <p className="detail-price">{money(product.price)}</p>
          <p className="detail-desc">{product.description}</p>

          <div className="detail-meta">
            <span className="meta-label">Colors</span>
            <div className="chips-row">
              {product.colors.map((c) => (
                <span key={c} className="color-chip">{c}</span>
              ))}
            </div>
          </div>

          <div className="detail-meta">
            <span className="meta-label">Sizes &amp; availability</span>
            <div className="sizes">
              {product.inventory.map((s) => {
                const label = stockLabel(s.quantity)
                const disabled = s.quantity === 0
                return (
                  <button
                    key={s.size}
                    className={`size-btn ${selectedSize === s.size ? 'selected' : ''} ${label.cls}`}
                    disabled={disabled}
                    onClick={() => setSelectedSize(s.size)}
                    title={label.text}
                  >
                    <span className="size-name">{s.size}</span>
                    <span className={`size-stock ${label.cls}`}>{label.text}</span>
                  </button>
                )
              })}
            </div>
          </div>

          <button className="btn add-btn" disabled={!selectedSize}>
            {selectedSize ? `Add ${selectedSize} to bag` : 'Select a size'}
          </button>

          {product.search_tags.length > 0 && (
            <div className="tags">
              {product.search_tags.map((t) => (
                <span key={t} className="tag">#{t}</span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
