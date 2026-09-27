# AI Prompts Log — HW 4 (Campus Customs Storefront + Chatbot)

This file is the running log of the prompts I typed to Claude Code while building this
assignment. One section per problem. Prompts are recorded verbatim, in the order I sent
them — typos and all. The running website, the database writes, and the screenshots are
the evidence of the work itself.

**Project:** a real customer website for Campus Customs (Yale merch store) with a helpful
chatbot. Shoppers browse products, create an account, chat about merch, see matching items
appear on the page, and get honest answers about price and stock from the local database.

**Stack:** React + Vite + TypeScript front end, Python FastAPI backend, pydantic-ai agent.
OpenAI models via Portkey, model `gpt-5.6-terra`.

**Data:** `campus_customs.db` (catalogue, inventory by size, users with hashed passwords)
and the product images are **not committed to this repo** — see the README for setup.

---

## Problem 1 — Vibe Coder Prompts

Setting up the project, loading the data, and establishing this prompt log.

### Prompt 1 — where we're working

> aight we're working in the hw 4 folder

### Prompt 2 — the data

> just downloaded a zip file. move it to the hw 4 folder, and unzip it. let's have a look inside.

### Prompt 3 — the project brief

> here's the scenario. campus customs needs a real customer website with a helpful chatbot. you will build a react + vite typescript front end and a python fastapi backend whose brain is a pydanticai agent. shoppers should be able to browse products, create an accont, chat about merch, see matching items on the page, and get honest answers about price and stock from a lock database.
>
> you are given campus_customs.db with tables fo the product catalog, inventory by size, and users (with hashed passwords). product image file paths are in the catalog table. research yalebulldogblue.com to learn the style of campus customs' current webpage and information for your agent prompt.
>
> we're going to be using portkey_api_key from earlier projects. let's use model 5.6 terra for this one.
>
> we're going to be working one problem at a time, where i type each problem in my own words. in the end, i will push the project to a public github repo and submit the repo url as my assignment submission. as a flag for the future, we shold not commit the database or product images!

### Prompt 4 — follow-up: answering the open questions from the brief

*What was lacking after the brief:* three things needed a decision before any code — how
the repo handles the uncommitted images, the messy `garment_type` values in the catalogue,
and the bad encoding in the existing `chat_messages` rows.

> 1. i don't clearly understand what flag 1 means, but the graders will have access to the exact data set that i downloaded. plus, my earlier prompt on not committing the database and product images is paramount here. do with that what you will.
> 2. i bet subsequent instructions will prompt us here, but if not, please be on the lookout for this step so that at query time we can clean this up.
> 3. yes, let's clean that up eventually but not right now. don't be afraid to bring this up again if you think it's important to address before taking next steps.

### Prompt 5 — this log

> problem 1: vibe coder prompts
>
> create AI_prompts.md now and keep it updated as i work. this file is the log of what i type here. make sure you log every prompt. this is documentation for my graders.
>
> put one section for each problem. each section must include:
>
> * the problem number and title
> * at least one prompt i type
> * one follow-up prompt if i need it (which i most certainly will)
>
> my running website, database writes, and screenshots will be my evidence - i do not need an extra proof essay beyond these prompts, FYI.

---

## Problem 2 — Analyze the Database

Read `data/campus_customs.db`, understand every table's fields, and start `output/harness.md`
documenting each table, its fields, and why each field matters for the shop or the chatbot.

### Prompt 1 — the task

> problem 2: analyze the database
>
> look at the database data/campus_customs.db and understand the fields of each table. at a minimum, you should understand "catalogue" "inventory" and "users".
>
> then, start the file output/harness.md and write down each table and its fields, and one short line on why each field matters for the shop or the chatbot. we will keep growing this harness file in later problems (models, tools, safety, specs.)
>
> once this is done, please give me a human-friendly version of what you did.

---

## Problem 3 — Build the Campus Customs Website

Scaffold a React + Vite + TypeScript front end (nav: Home, Products, About Us, Log in,
Create account), pull Campus-Customs-style wording from yalebulldogblue.com in my own voice,
show the catalogue on a Products page with images from the DB, give each product a single-item
page, add a floating chat panel (stub for now), and start a simple FastAPI backend in
`backend/main.py` to serve products and images.

### Prompt 1 — the task

> problem 3: build the campus customs website
>
> scafold a react + vite + typescript front end for campus customs. put a nav bar at the top that links to the main pages:
>
> * home
> * products
> * about us
> * log in
> * create account
>
> pull campus customs-style wording from the yalebulldogblue.com website for Home and About Us, but write these in your own voice (do not copy the original site text).
>
> on the products page, show product images from the catalog (use the image paths in the database) with basic product info (name, price, short description).
>
> make each product open a single-item page (large image on one side, full product text on the other - description, price, sizes/stock when you have them). click a card on products should take the shopper there.
>
> add a chat interface in the bottom right of the site (a floating chat panel is fine). it does not need to talk to an agent yet - a stub that will call the backend later is enough for this problem.
>
> you will need a small API soon to read the database. it is fine to start a simple fastapi app in backend/main.py just to serve products and images, then grow it into the agent backend which we will tackle in problem 5.

### Prompt 2 — follow-up: typography

> amazing. this is purely cosmetic but can we choose a less standard font? something that's still clean but not standard. something modern, or even a lil edgy. i'll let you use your discretion here.

Result: Space Grotesk (headings, brand, prices, labels) + Inter (body), loaded from Google Fonts.

---

## Problem 4 — Create Account and Login

Build a normal create-account / login flow writing to the `users` table, with securely
stored passwords; confirm the seeded test user and a brand-new account both log in.

### Prompt 1 — the task

> ok problem 4: create account and login
>
> build a normal create-account / login flow.
>
> * create account: first name, last name, email, password, and confirm password
> * log in: email and password
>
> you may have already done this for me, and if so, just confirm i'm matching the directions i'm laying out here.
>
> new accounts should go into the "users" table. make sure to store passwords securely so hackers (human or AI) cannot access them.
>
> the seed database already has a test user you can use while building:
> email: test@campuscustoms.yale.edu
> password: password
>
> confirm you can log in as that user, and that a brand-new account you create also works.
>
> update output/harness.md with how auth works (what you store for a user and how passwords are protected).

---

## Problem 5 — PydanticAI Agent Backend

Build the shop chatbot as a PydanticAI agent behind FastAPI, plugged into the chat widget.
Agent split across `backend/prompts/prompt.md`, `backend/agent.py`, `backend/tools.py`,
`backend/models.py`; `backend/main.py` is the uvicorn app and exposes the chat route.

### Prompt 1 — the task

> problem 5: pydanticai agent backend
>
> build the shop chatbot as a pydanticai agent behind fastapi, plugged into the front-end chat widget. put the api app in backend/main.py - that is the file you run with uvicorn. keep the agent as these four files next to it:
>
> * backend/prompts/prompt.md - system prompt (grow this same file later)
> * backend/agent.py - agent entry / wiring
> * backend/tools.py - tools the agent can call
> * backend/models.py - pydantic / pydanticai structured types
>
> in main.py, expose a chat route so a message from the website returns a reply from the agent (and whatever else you need for products/auth). you will need your ai model api key for the agent, which i provided earlier.
>
> put campus customs voice and safety basics into prompts/prompt.md (we will expand tools and safety later). start or update types in models.py for chat replies / product cards as needed.
>
> in output/harness.md, note how the front end talks to fastapi and how the agent is loaded (prompt file + model).
>
> make sure the backend runs from the backend/ folder like this: uvicorn main:app --reload --port 8000

---

## Problem 6 — Tools: Product Info and Stock

Give the agent tools that read real product description, price, and per-size stock from
the database; ensure it never invents prices/quantities and says clearly when a size is
out of stock. Expand the prompt and update return types; document each tool in the harness.

### Prompt 1 — the task

> problem 6: tools: product info and stock
>
> give the agent tools that look up real information from campus_customs.db: product description, price, and how many are in stock (by size when the customer asks).
>
> again, i think you already did this but check to make sure you complied. the agent must use teh database - it should not invent prices or quantities. if a size is out of stock, say so clearly.
>
> expand prompts/prompt.md so the agent knows to call these tools for price and stock questions. add or update return types in models.py.
>
> in output/harness.md, list ecah tool and explain which model fields you chose for lookup results and why.

---

## Problem 7 — Chat Search That Updates the Page

When a shopper asks about a type of item, the agent searches the catalogue and the website
dynamically renders the matches as product cards on the page (not just in the chat), and
those cards still open the single-item detail view when clicked.

### Prompt 1 — the task

> problem 7: chat search that updates the page
>
> now we will add a neat feature to the site. when a customer asks about a type of item - for example "what hoodies do you have?" - the agent should search the catalog and the website should dynamically show those matching items as product cards (image, name, price, short info). this is an api contract: the agent returns structured product matches and then the front end renders them on the website. it looks really cool, says my professor.
>
> after the dynamic product cards are loaded by the new feature, make sure the same single-item page behavior you built in problem 3 still works: each product card - including the ones the chat just put on the page - should still open that detail view (large image + full info) when clicked.
>
> update prompts/prompt.md and output/harness.md so it is clear how search results reach the page.

---

## Problem 8 — Customer Memory

Persist logged-in shoppers' chat history and reload it on return; give the agent the
shopper's identity (name, email) via deps; pass page context so "do you have this in pink?"
on a product page resolves to that product. Guests can chat without persistence.

### Prompt 1 — the task

> problem 8: customer memory
>
> when a shopper is logged in, save their chat history in the database in an appropriate table and reload it when they return. the agent should know *who* is chatting (name, email) - put that in agent deps (or an equivalent clear pattern) and / or tools the agent can call.
>
> also pass enough page context that if someone is on  a product page and asks "do you have this in pink?" the agent knows which item they mean. hint: you can put code into the agent context. i tested this out already with quarter zips and i asked for no residential college stuff, and it worked, but i'm repeating this since it's in the directions and i wanna make sure i'm complying.
>
> guests can still chat, but history only needs to persist for logged-in users.
>
> document in output/harness.md how user chat history is stored, what customer fields the agent sees, and how page context is passed.

---

## Problem 9 — Usability Improvements

Two front-end and two agent/backend usability improvements. Discussion first.

### Prompt 1 — the task (discussion)

> problem 9: usability improvements
>
> now that the core shop works, i need to improve it. i need to implement 2 front-end usability improvements and 2 agent/backend usability improvements.
>
> before implementing, let's talk.
>
> i've noticed that the front end doesn't immediately display any product. the front page should have one of those things that displays one cool item, maybe it's new or popular, that auto-scrolls to another one every few seconds. let's also add a yale logo at the bottom to signify that we're legit. also, instead of tabs at the top, let's do a cute hamburger icon thing on the top left that expands a menu down to the bottom for the diff options, and it can expand diff sections like Apparel into Tops and Bottoms etc. ok that's two front-end things. since there's no more tabs at the top, it should look cleaner i think.
>
> on the back end, the chat feature needs to be faster. idk what's going on under the hood so you tell me what two fixes can be done to implement faster chat and search.

### Prompt 2 — follow-up: decisions (answered in the app's question UI)

*Recorded from the pre-implementation discussion.*

- **Backend speed fixes (2):** lower the model's reasoning effort (kills the ~27s spikes)
  **and** stream the reply to the widget (perceived speed). Diagnosis: DB/search were already
  fast (~1.7ms/search); the model was the bottleneck.
- **Hamburger drawer:** organize as **both** an Apparel section (Tees, Crewnecks, Hoodies,
  Quarter-Zips, Jackets) and Yale sections (Residential Colleges, Teams, Schools). Noted that
  the catalogue has no bottoms.
- **Homepage carousel:** curated hand-picked featured items, auto-scrolling.
- **Auth controls:** move everything (browse + login/account) into the hamburger drawer for a
  minimal top bar.

### Prompt 3 — follow-up: usability write-up

> oh hell yeah. now, write: output/usability.md and make sure you make the four improvements that we made explicit, 2 front end, 2 back end.
>
> for each improvement, say:
>
> * what we added/changed
> * why is helps a campus customs shopper or the business
>
> once you've done that, recheck to make sure the changes you articulate are indeed on the website. graders are going to read this write up and check for the features.

---

## Problem 10 — Style the Website

Creative design so the site feels like a real Campus Customs storefront: fonts, color,
hierarchy, motion, product presentation, chat feel. Better logos (custom-crafted, not
trademarked), serif copy font, and a Handsome Dan bulldog chat persona.

### Prompt 1 — the task

> problem 10: style the website
>
> here are my prof's instructoins: add creative design so the site feels like a real campus customs storefront - fonts, color, hierarchy, motion, product presentation, chat feel. i will get more points for imaginative and innovative design.
>
> eventually, once you and i have decided on changes, you will write output/design.md listing what we changed and why it should help customers stick around and buy. keep it concrete and short.
>
> i got a few things. one, real logos aren't used. Use a real 'Y' yale logo at the bottom. if its proprietary, rip one off somewhere else, idk. same with the "CC" campus customs logo. it looks like.....ai made it. make it cuter. collegiate but indie.
>
> the font still feels too ai-made. maybe try having a serif font be the copy text?
>
> also let's have handsome dan, the bulldog mascot of yale university, to be the chat. like replace the boring Chat with us bullet with an icon of Handsome Dan, and make it cute!!!!! give the chat a dog personality, with woofs and maybe dog puns here and there. and maybe on the icon, have a quote that says "handsome dan here to help you look chic af".
>
> also add a dot dot dot thingy while the agent is thinking in the chat box.
>
> but seriously, the logos for campus customs and yale are terrible.

### Prompt 2 — follow-up: design decisions (answered in the app's question UI)

- **Copy font:** Fraunces (serif), replacing Space Grotesk which felt AI-made. Inter kept for
  small UI labels only.
- **Color/vibe:** vintage collegiate — navy + warm cream + gold, heritage feel.
- **Handsome Dan icon:** cute cartoon bulldog.
- **Chat launcher tagline:** "Handsome Dan here to help you look chic af" (verbatim).
- **Logos:** custom-crafted collegiate marks (serif Yale-style Y, varsity CC monogram) drawn as
  SVG — Yale's actual trademarked logo is intentionally NOT embedded.

---

## Problem 11 — Site Testing (App Check)

Test the live site and document it in `output/app_check.html` with real screenshots +
captions for: chat checking inventory (honest stock/price from DB), dynamic search-result
cards after a category question (hoodies), and one Problem 9 usability feature.

### Prompt 1 — the task

> problem 11: site testing (app check)
>
> test the live site and document it in output/app_check.html (a page you can double-click open). include clear screenshots and short captions for:
>
> * chat checking the inventory level of an item (honest stock/price from the DB)
> * the dynamic search-result cards appearing after a category question (e.g. hoodies)
> * one of the usability features we added up in problem 9
>
> this html should be easy for a human or AI to grade: heading for each check, screenshot beneath, and one or two sentence on what the screenshot proves. put the screenshot image files in output/app_check_images/ and link them from app_check.html with relative paths (for example app_check_images/inventory.png)

---

## Problem 12 — Audit Trail, Safety, Finish Harness

Keep an append-only `output/audit_trail.json` of agent-loop activity (time, tool, short
args/result, stop reason; never wiped). Add safety rules to `prompts/prompt.md`. Finish
`output/harness.md` (model fields + why, tools/abilities, safety rules, specs: loop limits,
result caps, models, how to run front + back).

### Prompt 1 — the task

> problem 12: audit trail, safety, finish harness
>
> keep an append-only output/audit_trail.json of agent-loop activity (time, tool name, short args/result, stop reason). do not wipe it between runs.
>
> also, think of some safety rules to give the agent and put them in prompts/prompt.md
>
> finish output/harness.md so it is clear how the system works.
>
> * model fields in models.py and why you chose them
> * tools and abilities
> * safety rules
> * specs (loop limits, result caps, models, how to run front + back)

---

## Problem 13 — Push to GitHub and Submit the URL

Package the project into an `hw4` layout and push to a public GitHub repo (openable and
cloneable by graders). Never commit the real `.env`, the database, or product images —
use `.gitignore` and ship `.env.example` with placeholders. Add a `README.md` explaining
how to run the front end and back end after placing the local data pack.

### Prompt 1 — the task

> problem 13: push to github and submit the URL
>
> okay now it's time to wrap up. put the code in a folder named hw4 and push it to a public github repository. i'm going to be submitting the repo url on canvas as my submission (the link should be openable and cloneable by graders).
>
> do not put the real .env, campus_customs.db, or product images in the github repo. use .gitignore. include .env.example with placeholders only.
>
> i've attached the expected file layout for the github repo, as well as the local-only data pack (not in git).
>
> the agent itself is four files under backend/: prompts/prompt.md, agent.py, tools.py and models.py
>
> README.md should explain how to run the front end and back end after placing the data pack.

Result: pushed to **https://github.com/kyleeyeh/hw4** (public). Verified against the remote
tree that no `.env`, `*.db`, `data/`, product images, or virtualenv are committed.

### Prompt 2 — follow-up: review fixes (Codex findings)

> [Codex flagged: (1) chat history exposed by client-supplied user_id with no auth check;
> (2) AI_prompts.md missing a Problem 13 section.]
> since this is a literal homework assignment to make a pretend website, idk how important
> point 1 is, but to be safe, maybe address it without sacrificing any other requirement.
> point 2 should probably be addressed just to be safe.

Result: (1) Added server-verified session tokens — login/signup now issue an HMAC-signed
token; chat and history routes derive identity **only** from the verified token (via the
`Authorization: Bearer` header), never from a client-supplied id, so a client can't read or
impersonate another customer. Guests (no token) still chat; history requires a valid token.
(2) This section added.
