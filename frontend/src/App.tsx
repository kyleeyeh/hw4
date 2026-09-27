import { Outlet } from 'react-router-dom'
import NavBar from './components/NavBar'
import ChatWidget from './components/ChatWidget'
import ChatPicks from './components/ChatPicks'
import YaleSeal from './components/YaleSeal'
import './app-layout.css'

export default function App() {
  return (
    <div className="app-shell">
      <NavBar />
      {/* Products the chat agent surfaced render here, on the page, above the route. */}
      <ChatPicks />
      <main className="app-main">
        <Outlet />
      </main>
      <footer className="app-footer">
        <div className="container footer-inner">
          <div className="footer-left">
            <YaleSeal />
          </div>
          <div className="footer-right">
            <span>Campus Customs · 57 Broadway, New Haven, CT 06511</span>
            <span>Official Yale merchandise, apparel &amp; access</span>
          </div>
        </div>
      </footer>
      <ChatWidget />
    </div>
  )
}
