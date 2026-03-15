# Great_Pacific_Cleanup

# 🌊 Great Pacific Cleanup

An arcade-style 2D vertical scrolling ocean cleanup game built with **Pygame-CE**. Steer your cleanup boat, collect floating garbage, avoid hazards and marine life, grab power-ups, and rack up points as the ocean gets increasingly chaotic!

## 🎮 Gameplay

- **Collect** floating trash clusters to earn points (+10 each)
- **Avoid** sharks, oil spills, cargo containers, and rogue waves — they cost you a life!
- **Grab power-ups** for temporary boosts:
  - ⚡ **Turbo** — 1.5× speed for 5 seconds
  - 🛡 **Shield** — absorbs one hit
  - 🌐 **Eco Net** — wider collection radius for 8 seconds
  - 📡 **Sonar** — reveals nearby entities for 6 seconds
- **Survive** as long as you can — the game speeds up and spawns more hazards every 8 seconds!

## 🛠 Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/Manmohit-24-Singh/Great_Pacific_Cleanup.git
cd Great_Pacific_Cleanup
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

### 3. Activate it

**macOS / Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install pygame-ce pygbag
```

### 5. Run the game

```bash
python3 main.py
```

## 🕹 Controls

| Key | Action |
|-----|--------|
| `W` / `↑` | Move up |
| `S` / `↓` | Move down |
| `A` / `←` | Move left |
| `D` / `→` | Move right |

## 📁 Project Structure

```
Great_Pacific_Cleanup/
├── assets/              # Sprite images (boat, trash, animals, hazards, powerups)
├── main.py              # Game loop, rendering, collision detection
├── player.py            # Player boat class
├── entities.py          # Scrolling entities (trash, marine life, hazards, powerups)
├── spawner.py           # Entity spawning with difficulty scaling
├── particles.py         # Particle effects & floating score text
├── ui.py                # HUD (score, lives, active powerups, menus)
├── asset_loader.py      # Image loading, scaling, and caching
├── settings.py          # All game constants and configuration
└── README.md
```

## 🌐 Building for Web (Pygbag)

```bash
pygbag .
```

Navigate to `http://localhost:8000/` to play in the browser.

## 📋 Notes

- **No database** — high score is stored locally in `high_score.txt`
- Requires **Python 3.10+**
- Tested with **pygame-ce 2.5.7**

## Running on Mobile

This branch includes mobile support via a virtual joystick

### Prerequisites
- Python 3.x
- pygame: `pip install pygame`
- pygbag: `pip install pygbag`

### Steps

**1. Build the web version:**
```
python -m pygbag --build main.py
```

**2. Serve it on your local network:**
```
cd build/web && python3 -m http.server 8000 --bind 0.0.0.0
```

**3. Find your computer's local IP address:**
- Mac: `ipconfig getifaddr en0`
- Windows: run `ipconfig` and look for IPv4 Address

**4. Open on your phone:**
- Make sure your phone is on the same WiFi as your computer
- Open Safari or Chrome and go to `http://YOUR_IP:8000`

### Controls
- **Desktop** — WASD or arrow keys
- **Mobile** — Virtual joystick in the bottom-right corner

### Notes
- The game may take 10-20 seconds to load in the browser on first run
- If `en0` gives no result on Mac, try `ipconfig getifaddr en1`
```

