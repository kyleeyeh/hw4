# Campus Customs — Usability Improvements

Four usability improvements were made to the Campus Customs site: two on the front end and
two on the back end. Each is described below with what changed and why it helps a Campus
Customs shopper or the business.

---

## Front-end improvement 1 — Auto-scrolling featured carousel on the home page

**What we added/changed.** The home page now opens with a full-width, auto-rotating spotlight
of curated, hand-picked products (e.g. the 2025 Harvard–Yale tee, the Big Yale hoodie, a
Champion reverse-weave crewneck, the Brooks Brothers bomber). It advances to the next item
every ~4.5 seconds, pauses when the shopper hovers over it, has clickable dots to jump between
items, shows each item's name, category, short description and price, and has "Shop this"
(→ that product's detail page) and "Shop all" buttons.
Files: `frontend/src/components/FeaturedCarousel.tsx`, `frontend/src/components/carousel.css`,
used in `frontend/src/pages/Home.tsx`.

**Why it helps.** Before this, the landing page showed no products at all — a shopper had to go
looking. Now real merchandise is on screen the instant the page loads, which is exactly what a
store's front window is for. It gives first-time visitors an immediate sense of the catalogue,
puts the store's best/most iconic items in front of everyone, and gives the business a
merchandising surface to promote seasonal or high-margin pieces. Every slide is one click from
buying.

---

## Front-end improvement 2 — Hamburger navigation drawer (replacing the top tabs)

**What we added/changed.** The row of tabs across the top was replaced with a single hamburger
button on the top-left that opens a full-height slide-out drawer. The drawer contains Home /
All Products / About, plus expandable sections that match the real catalogue:
- **Apparel** → Tees, Crewnecks, Hoodies, Quarter-Zips, Jackets (each opens the Products page
  filtered to that category, via `/products?category=...`).
- **Residential Colleges**, **Teams**, and **Schools** → each expands to the specific Yale
  colleges/teams/schools we carry and opens a filtered Products search (`/products?q=...`).

Log in / Create account (or "Log out" when signed in) also live inside the drawer, so the top
bar stays clean — just the menu button, the brand, and a "Hi, {name}" greeting when logged in.
The Products page reads the `category` and `q` filters from the URL.
Files: `frontend/src/components/NavBar.tsx`, `frontend/src/components/navbar.css`,
`frontend/src/pages/Products.tsx`.

**Why it helps.** A handful of flat top tabs can't express how people actually shop Yale gear —
by their residential college, their team, or their school. The drawer organizes 100+ products
into browsable categories without cluttering the page, and collapses back to nothing when
closed, so the storefront looks cleaner and the product imagery gets the attention. Shoppers
reach "Davenport" or "Hoodies" in two clicks; the business gets a scalable menu that can grow
as the catalogue does.

---

## Back-end improvement 1 — Much faster chat (reasoning effort turned off)

**What we added/changed.** The chat agent runs on `gpt-5.6-terra`, a reasoning model that, by
default, spends several seconds "thinking" before every answer — one price question was
measured at **27 seconds**. We set the model's reasoning effort to `"none"` for the agent, so
it answers directly using its database tools instead of deliberating first. Measured after the
change: replies come back in **a few seconds** (a direct price lookup ~3s; a question that also
runs a catalogue search ~5–8s) — down from the 27-second worst case.
File: `backend/agent.py` (`OpenAIChatModelSettings(openai_reasoning_effort="none")`).

**Why it helps.** A shopper asking "how much is this?" or "do you have it in medium?" expects a
near-instant answer, the way they would from a store associate. A 27-second wait feels broken
and drives people away from the chat — the site's most useful feature. Cutting replies to a few
seconds makes the assistant actually usable, which is what turns chat questions into sales for
the business.

---

## Back-end improvement 2 — Streaming chat replies

**What we added/changed.** Added a streaming chat endpoint (`POST /api/chat/stream`) using
Server-Sent Events. Instead of the browser waiting for the entire answer and then dumping it on
screen, the reply now streams into the chat panel word-by-word as it's generated, with a typing
indicator shown until the first words arrive. The final message still carries the matching
product cards (filled from the database, never the model's memory) so they appear on the page.
Files: `backend/main.py` (`/api/chat/stream`), `backend/agent.py` (`run_chat_stream`),
`frontend/src/components/ChatWidget.tsx` (reads the stream).

**Why it helps.** Streaming makes the assistant feel alive and responsive — the shopper sees it
"typing back" immediately rather than staring at a frozen box wondering if it's working. That
perceived responsiveness keeps people engaged with the chat instead of abandoning it, and it's
the standard behavior shoppers now expect from any modern chat interface.

---

## Verification

Each claim above was re-checked against the running site and source (see the recheck notes
accompanying this file); all four features are present and working.
