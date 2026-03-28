# Great Pacific Cleanup

Welcome to **Great Pacific Cleanup**! This is a fun and fast-paced 2D ocean cleanup game where you drive a boat, collect trash, avoid dangerous hazards, and compete against other players worldwide. Clean up the ocean, learn some environmental trivia, and see if you can claim the top spot on the leaderboard!

## Features

- **User Accounts:** Sign up and log in to save your progress.
- **High Score Tracking:** Your personal best score is always saved to your profile.
- **Global Leaderboard:** Compete in real-time with players around the world to see who can clean up the most trash.

---

## How to Download & Play
### Windows
1. Download `GreatPacificCleanup-windows.zip` from the latest release.
2. Unzip the folder.
3. Double-click `GreatPacificCleanup.exe` to launch the game.

> **Note:** Windows SmartScreen may show a blue warning saying "Windows protected your PC". To get past it:
> 1. Click **"More info"**
> 2. Click **"Run anyway"**
> 
> This is a standard Windows warning for apps that are not from the Microsoft Store, and it is completely safe to dismiss.

### Mac
1. Download `GreatPacificCleanup-macos.zip` from the latest release.
2. Unzip the folder.
3. Open Terminal and run the following commands:
```bash
xattr -cr ~/Downloads/GreatPacificCleanup-macos
chmod +x ~/Downloads/GreatPacificCleanup-macos/GreatPacificCleanup
~/Downloads/GreatPacificCleanup-macos/GreatPacificCleanup
```

> **Note:** Please make sure to use the actual path on your machine if you moved the folder out of your Downloads! The first command (`xattr`) applies to the **entire unzipped folder**, while the second command (`chmod`) targets the **executable file inside it**.
> 
> These commands are required because macOS blocks apps that are not from the App Store. You only need to do this once. If your Mac still blocks the app, open **System Settings > Privacy & Security**, scroll down to the Security section, and click **"Open Anyway"** next to the prompt about GreatPacificCleanup.

### Linux
1. Download `GreatPacificCleanup-linux.zip` from the latest release.
2. Unzip the folder.
3. Open Terminal and run:
```bash
chmod +x ~/Downloads/GreatPacificCleanup-linux/GreatPacificCleanup
~/Downloads/GreatPacificCleanup-linux/GreatPacificCleanup
```

---

## Gameplay

- **Collect floating trash** to earn points and build up speed boosts.
- **Avoid** sharks, sea turtles, oil spills, and cargo containers!
- **Grab power-ups** for awesome temporary abilities:
  - **Eco Net** — Increases your collection radius for 8 seconds.
  - **Turbo** — 1.5× speed boost for 5 seconds.
  - **Shield** — Gain a protective bubble that blocks one hit.
  - **Magnetic Hyperdrive** — Grants invulnerability, auto-collection, and 3× speed for 8 seconds!
- **Second Chance Trivia** — Answer an environmental question correctly to revive yourself after losing all your lives.
- **Dynamic Difficulty** — The longer you survive, the faster and more challenging the hazards get!

## Unit Testing
1. Follow the Download and Play steps, listed above
2. In the bash terminal, run the following command:

PYTHONPATH=. pytest -v

## Controls

| Key | Action |
|---|---|
| **W / ↑** | Move up |
| **S / ↓** | Move down |
| **A / ←** | Move left |
| **D / →** | Move right |
| **Space** | Start game / Submit answers |
| **G** | Play as Guest (from the main menu) |
| **L** | View the global leaderboard |
| **O** | Log out |
| **Esc** | Pause the game / Go back |

## Credits
Audio files were sourced from https://epidemicsound.com and distributed in MP3 format. Credit is also given to Gemini 3.0 for assisting in identifying issues within the sequence diagrams and for contributing ideas for smaller features that aligned with our technical stack. All code was implemented by our team, guided by YouTube tutorials and official documentation. All additional assets including documentation, written content, and visual elements such as the sea turtle, fish, waves, sharks, oil spills, and cargo containers were created entirely by us.

Enjoy cleaning the ocean, and good luck!
