# Great Pacific Cleanup

A 2D ocean cleanup game built with Python and Pygame. Drive a boat, collect trash, avoid hazards, and compete on the global leaderboard.

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

4. Add your Firebase config
```bash
# Create firebase_config.py with your Firebase project credentials
# (see firebase_config.py.example for the format)
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
| Auth | Firebase Authentication |
| Database | Cloud SQL PostgreSQL (via Firebase Data Connect) |
| API | Data Connect GraphQL REST API |

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
├── firebase_service.py     # Firebase Auth + Data Connect client
├── firebase_config.py      # Firebase project config (gitignored)
├── asset_loader.py         # Image loading with PyInstaller support
├── assets/                 # Sprite images (PNG)
├── sounds/                 # Music tracks (MP3)
├── dataconnect/            # Data Connect schema and connectors
│   ├── schema/schema.gql   # PostgreSQL table definitions
│   └── connector/          # GraphQL queries and mutations
├── great_pacific_cleanup.spec  # PyInstaller build config
├── .github/workflows/      # CI/CD for multi-platform builds
└── requirements.txt        # Python dependencies
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
