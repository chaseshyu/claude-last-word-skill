#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

// get __dirname in ES module context
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const skillPath = path.join(__dirname, 'SKILL.md');
const scriptsPath = path.join(__dirname, 'scripts');

console.log("\n🚀 @chaseshyu/claude-last-word-skill 已啟動\n");

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

// 2. 顯示 SKILL.md 內容
if (fs.existsSync(skillPath)) {
  const content = fs.readFileSync(skillPath, 'utf8');
  console.log("--- SKILL Guide Content ---");
  console.log(content);
  console.log("----------------------");
} else {
  console.error("❌ Error: SKILL.md file not found.");
}

console.log("\n✅ Installation/Confirmation complete!");
console.log("Please input '/last-word' in Claude or refer to the above guide to get started.\n");