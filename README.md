# Stormbladed

Stormbladed is a small 2D tree-chopping, fishing, crafting, and multiplayer browser game.

## Run the browser game

The browser version is in `index.html`.

1. Open the repository folder in a modern browser, or serve it locally:
   ```bash
   python -m http.server 8000
   ```
2. Visit [http://localhost:8000](http://localhost:8000).

Multiplayer requires internet access because PeerJS is loaded from a CDN and peer connections use public STUN servers. Save data is stored locally in the browser, so progress is specific to that browser/profile.

## Controls

- **WASD / arrow keys:** Move.
- **Hold Space near a tree:** Chop the tree.
- **Hold Space near a pond:** Fish.
- **Hold the on-screen action button:** Chop or fish on touch devices or when Space is inconvenient.
- **E:** Interact with nearby merchants, crafting stations, the IGA, or the plane.
- **Enter:** Open chat while playing.
- **O:** Open the configured quick link.

Chopping and fishing take time: keep holding the action key/button while the progress bar fills. Move closer if the game shows the proximity hint.

## Optional Pygame version

`main.py` is a separate, simpler Pygame prototype, not the implementation of the browser game.

Install Pygame, then run:

```bash
python -m pip install pygame
python main.py
```

## Regression smoke checks

With Node.js installed, run:

```bash
node tests/smoke-check.js
```

These checks verify that the browser script parses, important interaction/multiplayer safeguards remain present, and literal DOM IDs referenced by the game exist. They are static smoke checks, not a replacement for manually testing gameplay in a browser—especially multiplayer, which needs two browser sessions and network access.
