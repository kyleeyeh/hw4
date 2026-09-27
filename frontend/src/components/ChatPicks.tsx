import { Link } from 'react-router-dom'
import { useChatResults } from '../chatResults'
import { money, shortInfo } from '../api'
import './chatpicks.css'

/**
 * The "chat search updates the page" feature: when the agent returns product
 * matches, they render here as full product cards on the page. Each card links to
 * the same single-item detail view from Problem 3.
 */
export default function ChatPicks() {
  const { matches, query, clear } = useChatResults()
  if (matches.length === 0) return null

  return (
    <section className="chat-picks">
      <div className="container">
        <div className="picks-head">
          <div>
            <span className="picks-eyebrow">From your chat</span>
            <h2>{query ? `Matches for "${query}"` : 'Matches from your chat'}</h2>
          </div>
          <button className="picks-clear" onClick={clear}>Clear ✕</button>
        </div>

        <div className="picks-grid">
          {matches.map((p) => (
            <Link to={`/products/${p.product_id}`} key={p.product_id} className="card">
              <div className="card-img">
                <img src={p.image_url} alt={p.name} loading="lazy" />
              </div>
              <div className="card-body">
                <span className="card-type">{p.garment_type}</span>
                <h3 className="card-name">{p.name}</h3>
                <p className="card-desc">{shortInfo(p.description)}</p>
                <div className="card-foot">
                  <span className="price">{money(p.price)}</span>
                  <span className="view">View →</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  )
}
