import { Link } from 'react-router-dom'
import FeaturedCarousel from '../components/FeaturedCarousel'
import './pages.css'

export default function Home() {
  return (
    <div className="home">
      <FeaturedCarousel />

      <section className="container features">
        <div className="feature">
          <h3>Every College, Every Team</h3>
          <p>
            Rep your residential college or your varsity squad. We carry gear across
            all 14 colleges and Yale's athletic programs.
          </p>
        </div>
        <div className="feature">
          <h3>Licensed &amp; Legit</h3>
          <p>
            Everything we sell is officially licensed Yale merchandise — the real
            marks, the real blue, none of the knockoffs.
          </p>
        </div>
        <div className="feature">
          <h3>Built for the Long Haul</h3>
          <p>
            Heavyweight cotton, reverse-weave classics, and fleece that holds up
            season after season on Old Campus.
          </p>
        </div>
      </section>

      <section className="container home-band">
        <div className="band-inner">
          <div>
            <h2>Not sure where to start?</h2>
            <p>
              Ask our shopping assistant in the corner — it knows the catalog, the
              colors, the sizes, and what's in stock right now.
            </p>
          </div>
          <Link to="/products" className="btn">Browse Products</Link>
        </div>
      </section>
    </div>
  )
}
