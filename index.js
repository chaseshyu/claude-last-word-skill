#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';
import os from 'os';

// get __dirname in ES module context
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const skillPath = path.join(__dirname, 'SKILL.md');
const scriptsPath = path.join(__dirname, 'scripts');

console.log("\n🚀 @chaseshyu/claude-last-word-skill activated\n");

// 1. auto-set scripts/ as executable (if it exists)
if (fs.existsSync(scriptsPath)) {
  try {
    if (process.platform !== 'win32') {
      execSync(`chmod -R +x "${scriptsPath}"`);
    }
  } catch (err) {
    console.warn("⚠️  Could not set scripts/ as executable. Please check permissions.");
  }
}

// 2. auto-install to ~/.claude/skills/last-word
const targetDir = path.join(os.homedir(), '.claude', 'skills', 'last-word');
console.log(`\n📦 Installing skill to: ${targetDir}`);

try {
  // create target directory if it doesn't exist
  if (!fs.existsSync(targetDir)) {
    fs.mkdirSync(targetDir, { recursive: true });
  }

  // copy SKILL.md, scripts/, and references/ to target directory
  fs.cpSync(skillPath, path.join(targetDir, 'SKILL.md'), { force: true });
  if (fs.existsSync(scriptsPath)) {
    fs.cpSync(scriptsPath, path.join(targetDir, 'scripts'), { recursive: true, force: true });
  }
  const referencesPath = path.join(__dirname, 'references');
  if (fs.existsSync(referencesPath)) {
    fs.cpSync(referencesPath, path.join(targetDir, 'references'), { recursive: true, force: true });
  }

  console.log("✅ Installation into Claude Code successful!");
  console.log("You can now trigger this skill in Claude Code by typing: /last-word");
} catch (err) {
  console.error("❌ Failed to install skill into ~/.claude/skills/last-word");
  console.error(err);
}

// 3. show SKILL.md content in terminal for quick reference
if (fs.existsSync(skillPath)) {
  const content = fs.readFileSync(skillPath, 'utf8');
  console.log("\n--- SKILL Guide Content ---");
  console.log(content);
  console.log("----------------------\n");
} else {
  console.error("❌ Error: SKILL.md file not found.");
}