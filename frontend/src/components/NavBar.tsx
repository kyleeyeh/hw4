import { useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'
import CampusCustomsLogo from './CampusCustomsLogo'
import './navbar.css'

// Drawer taxonomy — grounded in what the catalogue actually contains.
const APPAREL = ['T-Shirt', 'Crewneck', 'Hoodie', 'Quarter-Zip', 'Jacket']
const COLLEGES = [
  'Benjamin Franklin', 'Berkeley', 'Branford', 'Davenport', 'Grace Hopper',
  'Jonathan Edwards', 'Morse', 'Pierson', 'Saybrook',
]
const TEAMS = ['Baseball', 'Diving', 'Fencing', 'Football', 'Ice Hockey', 'Lacrosse', 'Sailing', 'Tennis']
const SCHOOLS = ['Architecture', 'Art', 'Divinity', 'Management', 'Nursing']

interface SectionProps {
  title: string
  items: string[]
  hrefFor: (item: string) => string
}

function DrawerSection({ title, items, hrefFor, onNavigate }: SectionProps & { onNavigate: () => void }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="drawer-section">
      <button className="drawer-section-head" onClick={() => setOpen((o) => !o)} aria-expanded={open}>
        <span>{title}</span>
        <span className={`chev ${open ? 'up' : ''}`}>⌄</span>
      </button>
      {open && (
        <div className="drawer-sublinks">
          {items.map((item) => (
            <Link key={item} to={hrefFor(item)} className="drawer-sublink" onClick={onNavigate}>
              {item}
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

export default function NavBar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)

  const close = () => setOpen(false)
  function onLogout() {
    logout()
    close()
    navigate('/')
  }

  return (
    <>
      <header className="nav">
        <div className="container nav-inner">
          <button
            className="hamburger"
            onClick={() => setOpen(true)}
            aria-label="Open menu"
            aria-expanded={open}
          >
            <span /><span /><span />
          </button>

          <Link to="/" className="brand" onClick={close}>
            <CampusCustomsLogo size={44} />
            <span className="brand-text">
              Campus Customs
              <small>Yale Bulldog Blue</small>
            </span>
          </Link>

          {user && <span className="nav-hi">Hi, {user.first_name || user.name.split(' ')[0]}</span>}
        </div>
      </header>

      {/* Slide-out drawer */}
      <div className={`drawer-overlay ${open ? 'show' : ''}`} onClick={close} />
      <aside className={`drawer ${open ? 'open' : ''}`} aria-hidden={!open}>
        <div className="drawer-head">
          <span className="drawer-title">Menu</span>
          <button className="drawer-close" onClick={close} aria-label="Close menu">✕</button>
        </div>

        <nav className="drawer-body">
          <NavLink to="/" end className="drawer-link" onClick={close}>Home</NavLink>
          <NavLink to="/products" end className="drawer-link" onClick={close}>All Products</NavLink>
          <NavLink to="/about" className="drawer-link" onClick={close}>About Us</NavLink>

          <div className="drawer-divider" />

          <DrawerSection
            title="Apparel"
            items={APPAREL}
            hrefFor={(c) => `/products?category=${encodeURIComponent(c)}`}
            onNavigate={close}
          />
          <DrawerSection
            title="Residential Colleges"
            items={COLLEGES}
            hrefFor={(c) => `/products?q=${encodeURIComponent(c)}`}
            onNavigate={close}
          />
          <DrawerSection
            title="Teams"
            items={TEAMS}
            hrefFor={(t) => `/products?q=${encodeURIComponent(t)}`}
            onNavigate={close}
          />
          <DrawerSection
            title="Schools"
            items={SCHOOLS}
            hrefFor={(s) => `/products?q=${encodeURIComponent(s)}`}
            onNavigate={close}
          />

          <div className="drawer-divider" />

          {user ? (
            <>
              <span className="drawer-account">Signed in as {user.first_name || user.name}</span>
              <button className="drawer-link as-button" onClick={onLogout}>Log out</button>
            </>
          ) : (
            <>
              <NavLink to="/login" className="drawer-link" onClick={close}>Log in</NavLink>
              <NavLink to="/signup" className="drawer-link accent" onClick={close}>Create account</NavLink>
            </>
          )}
        </nav>

        <div className="drawer-foot">Officially licensed Yale merchandise</div>
      </aside>
    </>
  )
}
