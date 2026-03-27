# Great Pacific Cleanup

A simple 2D game made in Python using Pygame where you drive a boat to clean up the ocean and learn about the environment.

## Gameplay

- Collect floating trash to earn points and get speed boosts.
- Avoid sharks, turtles, oil spills, and cargo containers, or you will lose a life.
- Grab power-ups for temporary boosts:
  - Turbo: Makes you go 1.5x faster for 5 seconds.
  - Shield: Protects you from one hit.
  - Eco Net: Increases your collection radius for 8 seconds.
- Second Chance Trivia: If you lose all your lives, you can answer an environmental trivia question to get an extra life.
- The game speeds up and spawns more hazards the longer you survive.

## Setup & Installation

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
pip install pygame pyrebase4 requests
```

4. Run the game
```bash
python3 main.py
```

## Controls

- W / Up Arrow: Move up
- S / Down Arrow: Move down
- A / Left Arrow: Move left
- D / Right Arrow: Move right
- Space: Start game / Submit
- L: View world leaderboard
- O: Logout

## Project Structure

- assets/: Sprite images 
- main.py: Main game loop and engine
- player.py: Player boat class
- entities.py: Scrolling entities (trash, animals, hazards, powerups)
- spawner.py: Handles spawning and game difficulty
- particles.py: Visual effects and trails
- ui.py: HUD, menus, and interface screens
- settings.py: Game constants and colors
- trivia.py: Questions for the second chance minigame
- firebase_service.py: Connects to Firebase for leaderboards and auth
- asset_loader.py: Handles image loading
