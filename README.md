# Great Pacific Cleanup

A 2D ocean cleanup game built with Python and Pygame. Drive a boat, collect trash, avoid hazards, and compete on the global leaderboard.

## 🌊 Play Now

[▶ Play in Browser](https://manmohit-24-singh.github.io/Great_Pacific_Cleanup/) — no download required!

> *Web demo includes full gameplay but no login or leaderboard. Download the desktop version for the full experience.*

## Download & Play

### Pre-built Binaries (No Python Required)
Download the latest release for your platform from the [GitHub Releases](https://github.com/Manmohit-24-Singh/Great_Pacific_Cleanup/releases) page.

| Platform | Instructions |
|---|---|
| **Windows** | Extract the zip, run `GreatPacificCleanup.exe` |
| **macOS** | Extract the zip, run `GreatPacificCleanup`. If blocked by Gatekeeper: `xattr -d com.apple.quarantine GreatPacificCleanup` |
| **Linux** | Extract the zip, run `./GreatPacificCleanup`. May need: `chmod +x GreatPacificCleanup` |

### Run from Source

1. Clone the repository
```bash
git clone https://github.com/Manmohit-24-Singh/Great_Pacific_Cleanup.git
cd Great_Pacific_Cleanup
```

2. Create and activate a virtual environment
```bash
# Mac/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

3. Install requirements
```bash
pip install -r requirements.txt
```

4. Add your Supabase credentials
```bash
cp .env.example .env
# Edit .env and add your SUPABASE_URL and SUPABASE_ANON_KEY
```

5. Run the game
```bash
python3 main.py
```

## Gameplay

- **Collect** floating trash to earn points and speed boosts
- **Avoid** sharks, turtles, oil spills, and cargo containers
- **Grab power-ups** for temporary abilities:
  - 🌊 **Eco Net** — increases collection radius for 8 seconds
  - 🚀 **Turbo** — 1.5× speed for 5 seconds
  - 🛡️ **Shield** — blocks one hit
  - ⚡ **Magnetic Hyperdrive** — invulnerability, auto-collection, and 3× speed for 8 seconds
- **Second Chance Trivia** — answer an environmental question to revive after losing all lives
- **Dynamic difficulty** — speed and hazards increase as you progress through levels

## Controls

| Key | Action |
|---|---|
| W / ↑ | Move up |
| S / ↓ | Move down |
| A / ← | Move left |
| D / → | Move right |
| Space | Start game / Submit |
| G | Play as Guest (from menu) |
| L | View leaderboard |
| O | Logout |
| Esc | Pause / Back |

## Architecture

| Component | Technology |
|---|---|
| Game engine | Python + Pygame |
| Auth | Supabase Authentication (email/password) |
| Database | Supabase (PostgreSQL) |
| API | Supabase REST API (supabase-py) |

## Project Structure

```
├── main.py                 # Game loop and engine
├── player.py               # Player boat class
├── entities.py             # Scrolling entities (trash, animals, hazards, powerups)
├── spawner.py              # Spawn logic and difficulty scaling
├── particles.py            # Visual effects and particle trails
├── ui.py                   # HUD, menus, and screens
├── settings.py             # Constants and color palettes
├── trivia.py               # Second-chance trivia questions
├── supabase_service.py     # Supabase Auth + Database client
├── firebase_stub.py        # No-op stub for web/WASM builds
├── asset_loader.py         # Image loading with PyInstaller support
├── assets/                 # Sprite images (PNG)
├── sounds/                 # Music tracks (MP3)
├── .env.example            # Supabase credentials template
├── great_pacific_cleanup.spec  # PyInstaller build config
├── .github/workflows/      # CI/CD for multi-platform builds
└── requirements.txt        # Python dependencies
```

## Deployment

### Supabase Setup (Backend)

This game connects directly to Supabase — there is no middleman server. Supabase handles both authentication and the database.

1. Create a project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** and run the following:

```sql
CREATE TABLE IF NOT EXISTS scores (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    username   TEXT NOT NULL,
    high_score INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id)
);

ALTER TABLE scores ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view scores"
    ON scores FOR SELECT USING (true);

CREATE POLICY "Users can insert own score"
    ON scores FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own score"
    ON scores FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);
```

3. Go to **Settings → API** and copy your **Project URL** and **anon/public key**

### Environment Variables

Create a `.env` file in the project root:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
```

### Railway

Railway deployment is **not required** for this project. The game is a Pygame desktop client that calls Supabase's hosted API directly. Supabase handles all server-side concerns (auth, database, RLS).

If you add a FastAPI or Flask server component in the future, you can deploy it to Railway by:
1. Adding a `Procfile` (e.g., `web: gunicorn app:app`)
2. Setting `SUPABASE_URL` and `SUPABASE_ANON_KEY` as Railway environment variables
3. Connecting your GitHub repo to Railway for auto-deploy

### Running Locally

```bash
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env      # then edit with your credentials
python3 main.py
```

## Building from Source

```bash
pip install pyinstaller
pyinstaller great_pacific_cleanup.spec
# Output: dist/GreatPacificCleanup/
```

## CI/CD

Pushing a version tag triggers automatic builds for all platforms:

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions will build for Windows, macOS, and Linux, then attach the builds to a GitHub Release.
