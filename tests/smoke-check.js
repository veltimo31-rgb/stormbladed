'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const scripts = [...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)]
  .map(match => match[1])
  .filter(source => source.trim().length > 0);

assert.ok(scripts.length > 0, 'index.html should contain an inline game script');
for (const [index, source] of scripts.entries()) {
  assert.doesNotThrow(() => new Function(source), 'inline script ' + (index + 1) + ' should parse');
}

// Guard against accidentally removing key fixes when the game is edited later.
const requiredSnippets = [
  ['touch action button', 'HOLD TO CHOP / FISH'],
  ['touch input is fed into the action state', "keys['Space'] || keys['space'] || touchActionHeld"],
  ['nearest tree gets priority', '.sort((a, b) => a.distance - b.distance)'],
  ['out-of-range action feedback', 'Move closer to a tree or pond'],
  ['admin packet has an id', "Object.assign(getMyPacket('admin_grant'), payload)"],
  ['disco packet has an id', "getMyPacket('trigger_disco')"],
  ['admin commands only come from the host on guests', 'conn !== hostConn'],
  ['movement updates are throttled', 'POSITION_BROADCAST_INTERVAL = 50'],
  ['flight prevents repeated movement', "if (!inMenu && !flightInProgress && nameModal.style.display === 'none')"],
  ['chat uses text nodes', 'document.createTextNode(safeText)'],
  ['game-loop errors are logged', "console.error('[Stormbladed] Game loop error:'"],
  ['storage reads have a fallback', "readSetting('stormblade_custom_url', 'https://google.com')"],
  ['hardreset command is detected before normal chat broadcast', "if (txt.toLowerCase() === 'hardreset')"],
  ['hardreset clears the saved progress key', "localStorage.removeItem('stormblade_save')"],
  ['hardreset reloads the game', 'window.location.reload()']
];

for (const [name, snippet] of requiredSnippets) {
  assert.ok(html.includes(snippet), 'required safeguard missing: ' + name);
}

// Literal getElementById references should point to HTML ids, apart from IDs
// created dynamically in JavaScript.
const declaredIds = new Set([...html.matchAll(/\bid=["']([^"']+)["']/g)].map(match => match[1]));
const dynamicIds = new Set(['mobile-action-button']);
const referencedIds = new Set([...html.matchAll(/getElementById\(["']([^"']+)["']\)/g)].map(match => match[1]));
const missingIds = [...referencedIds].filter(id => !declaredIds.has(id) && !dynamicIds.has(id));
assert.deepEqual(missingIds, [], 'missing HTML IDs: ' + missingIds.join(', '));

console.log(
  'Stormbladed smoke checks passed (' + scripts.length + ' inline script(s), ' +
  requiredSnippets.length + ' safeguards, DOM IDs verified).'
);
