# Campus Customs — Yale Bulldog Blue storefront

A customer storefront for **Campus Customs** (officially-licensed Yale apparel) with a
shopping chatbot named **Handsome Dan**. React + Vite + TypeScript front end, Python
FastAPI back end, and a [pydantic-ai](https://ai.pydantic.dev/) agent whose answers about
price and stock come straight from the local database.

## What's here

```
hw4/
├── AI_prompts.md          # log of the prompts used to build this (one section per problem)
├── requirements.txt       # Python dependencies for the backend
├── .env.example           # copy to .env and add your Portkey key (placeholders only)
├── README.md
├── frontend/              # Vite React TypeScript app
├── backend/              # FastAPI app + the agent
│   ├── main.py           #   run with: uvicorn main:app --reload --port 8000
│   ├── agent.py          #   agent wiring (model + prompt + tools)
│   ├── tools.py          #   tools the agent can call (search / details / stock)
│   ├── models.py         #   pydantic types
│   ├── db.py             #   SQLite access + garment-type normalization
│   ├── auth.py           #   password hashing/verification
│   ├── audit.py          #   append-only agent audit trail
│   └── prompts/prompt.md #   system prompt (voice + safety rules)
└── output/               # build notes, design/usability write-ups, app check, audit trail
```

## Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.11+
- A **Portkey** API key (the agent calls OpenAI `gpt-5.6-terra` through Portkey)

## 1. Add the data pack (not in git)
The database and product images are **not** committed. Unzip the provided `data.zip` into
the **project root** so this layout exists:

```
hw4/
└── data/
    ├── campus_customs.db
    └── products/          # product images referenced by the catalogue
```

## 2. Back end (FastAPI, port 8000)
```bash
# from the project root
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt

# add your Portkey key
cp .env.example .env        # then edit .env and set PORTKEY_API_KEY

# run the API from the backend folder
cd backend
uvicorn main:app --reload --port 8000
```
The API serves the catalogue, product images, accounts, and the chat agent. Leave it running.

## 3. Front end (Vite, port 5173)
In a second terminal:
```bash
cd frontend
npm install
npm run dev
```
Open **http://localhost:5173**. The dev server proxies `/api` and `/media` to the backend
on port 8000, so no extra configuration is needed.

## Try it
- Browse **Products**, open a product for its detail page.
- **Create an account** or log in with the seeded test user
  (`test@campuscustoms.yale.edu` / `password`).
- Open the **Handsome Dan** chat (bottom-right) and ask things like
  *"what hoodies do you have?"* or *"is the Basic Hoodie Big Yale in stock in XL?"* —
  matching items appear on the page, and price/stock come live from the database.

## Notes
- **Model:** OpenAI `gpt-5.6-terra` via Portkey (configured in `.env`). Passwords are stored
  as salted PBKDF2-SHA256 hashes; the plaintext is never stored.
- **Not committed:** `data/` (database + images) and the real `.env` — see `.gitignore`.
- More detail on how the system works is in [`output/harness.md`](output/harness.md);
  design and usability write-ups are in `output/`.
