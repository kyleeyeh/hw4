import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchProducts, money, type ProductCard } from '../api'
import './carousel.css'

// Curated, hand-picked spotlight items — iconic / visually strong pieces.
const FEATURED_IDS = [
  '2025-yale-vs-harvard-t-shirt',
  'basic-hoodie-big-yale',
  'champion-reverse-weave-crewneck',
  'brooks-brothers-bomber-jacket-yale',
  'hype-and-vice-yale-university-premium-crewneck',
  'big-yale-tri-blend-t-shirt',
]
const INTERVAL_MS = 4500

export default function FeaturedCarousel() {
  const [items, setItems] = useState<ProductCard[]>([])
  const [index, setIndex] = useState(0)
  const [paused, setPaused] = useState(false)

  useEffect(() => {
    fetchProducts()
      .then((all) => {
        const byId = new Map(all.map((p) => [p.product_id, p]))
        setItems(FEATURED_IDS.map((id) => byId.get(id)).filter((p): p is ProductCard => !!p))
      })
      .catch(() => setItems([]))
  }, [])

  useEffect(() => {
    if (paused || items.length <= 1) return
    const t = setInterval(() => setIndex((i) => (i + 1) % items.length), INTERVAL_MS)
    return () => clearInterval(t)
  }, [paused, items.length])

  if (items.length === 0) return null
  const item = items[index]

  return (
    <section
      className="carousel"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
    >
      <div className="container carousel-inner">
        <div className="carousel-copy">
          <span className="carousel-eyebrow">Featured · Officially Licensed</span>
          <h1>{item.name}</h1>
          <p className="carousel-type">{item.garment_type}</p>
          <p className="carousel-desc">{item.short_description}</p>
          <div className="carousel-cta">
            <span className="carousel-price">{money(item.price)}</span>
            <Link to={`/products/${item.product_id}`} className="btn">Shop this</Link>
            <Link to="/products" className="btn btn-outline">Shop all</Link>
          </div>
          <div className="carousel-dots">
            {items.map((p, i) => (
              <button
                key={p.product_id}
                className={i === index ? 'dot active' : 'dot'}
                onClick={() => setIndex(i)}
                aria-label={`Show ${p.name}`}
              />
            ))}
          </div>
        </div>

        <Link to={`/products/${item.product_id}`} className="carousel-image" key={item.product_id}>
          <img src={item.image_url} alt={item.name} />
        </Link>
      </div>
    </section>
  )
}
