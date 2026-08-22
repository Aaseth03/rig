#!/usr/bin/env node
'use strict';

/**
 * rig installer
 *
 * Copies this repo's agent/skill/hook/rule assets into a target project,
 * laid out per-platform according to manifest.json (e.g. .claude/, .github/).
 *
 * Usage (from inside the target project):
 *   npx github:<user>/rig [options]
 *   node /path/to/rig/install.js [options]
 *
 * Options:
 *   --targets=claude,cursor   Which platforms to install (default: all in manifest)
 *   --only=agents,skills      Which asset categories to copy (default: all)
 *   --target-dir=<path>       Project root to install into (default: cwd)
 *   --force                   Overwrite files that already exist at the destination
 *   --dry-run                 Print what would happen without touching disk
 */

const fs = require('fs');
const path = require('path');

const REPO_ROOT = __dirname;

function parseArgs(argv) {
  const args = { targets: null, only: null, targetDir: process.cwd(), force: false, dryRun: false };
  for (const raw of argv) {
    const [key, value] = raw.replace(/^--/, '').split(/=(.*)/s);
    switch (key) {
      case 'targets':
        args.targets = value.split(',').map((s) => s.trim()).filter(Boolean);
        break;
      case 'only':
        args.only = value.split(',').map((s) => s.trim()).filter(Boolean);
        break;
      case 'target-dir':
        args.targetDir = path.resolve(value);
        break;
      case 'force':
        args.force = true;
        break;
      case 'dry-run':
        args.dryRun = true;
        break;
      case 'help':
      case 'h':
        args.help = true;
        break;
      default:
        console.error(`Unknown option: --${key}`);
        process.exit(1);
    }
  }
  return args;
}

function loadManifest() {
  const manifestPath = path.join(REPO_ROOT, 'manifest.json');
  if (!fs.existsSync(manifestPath)) {
    console.error(`manifest.json not found at ${manifestPath}`);
    process.exit(1);
  }
  return JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
}

function copyDir(src, dest, { force, dryRun }) {
  if (!fs.existsSync(src)) return { copied: 0, skipped: 0 };
  const stats = { copied: 0, skipped: 0 };

  fs.mkdirSync(dest, { recursive: true });

  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      const sub = copyDir(srcPath, destPath, { force, dryRun });
      stats.copied += sub.copied;
      stats.skipped += sub.skipped;
      continue;
    }

    const exists = fs.existsSync(destPath);
    if (exists && !force) {
      stats.skipped += 1;
      console.log(`  skip (exists): ${path.relative(process.cwd(), destPath)}`);
      continue;
    }

    if (dryRun) {
      console.log(`  would copy: ${path.relative(process.cwd(), destPath)}`);
    } else {
      fs.copyFileSync(srcPath, destPath);
      console.log(`  copied: ${path.relative(process.cwd(), destPath)}`);
    }
    stats.copied += 1;
  }

  return stats;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const manifest = loadManifest();
  const targetNames = Object.keys(manifest.targets);

  if (args.help) {
    console.log(`rig installer

Usage: node install.js [options]

Options:
  --targets=${targetNames.join(',')}   comma-separated platforms to install (default: all)
  --only=<category,...>          restrict to specific asset categories
  --target-dir=<path>            project root to install into (default: cwd)
  --force                        overwrite existing files
  --dry-run                      show what would happen, change nothing
`);
    return;
  }

  const selectedTargets = args.targets && args.targets.length ? args.targets : targetNames;

  for (const name of selectedTargets) {
    const target = manifest.targets[name];
    if (!target) {
      console.error(`Unknown target "${name}". Known targets: ${targetNames.join(', ')}`);
      process.exitCode = 1;
      continue;
    }

    const targetRootDir = path.join(args.targetDir, target.dir);
    console.log(`\n== ${name} -> ${path.relative(process.cwd(), targetRootDir) || target.dir} ==`);

    if (!args.dryRun) {
      fs.mkdirSync(targetRootDir, { recursive: true });
    }

    let categories = Object.keys(target.mappings);
    if (args.only && args.only.length) {
      categories = categories.filter((c) => args.only.includes(c));
    }

    let totalCopied = 0;
    let totalSkipped = 0;

    for (const category of categories) {
      const srcDir = path.join(REPO_ROOT, category);
      const destSubdir = target.mappings[category];
      const destDir = path.join(targetRootDir, destSubdir);

      if (!fs.existsSync(srcDir)) {
        console.log(`  (no source dir "${category}", skipping)`);
        continue;
      }

      const { copied, skipped } = copyDir(srcDir, destDir, args);
      totalCopied += copied;
      totalSkipped += skipped;
    }

    console.log(`  -> ${totalCopied} file(s) ${args.dryRun ? 'would be copied' : 'copied'}, ${totalSkipped} skipped`);
  }

  if (!args.force) {
    console.log('\nTip: pass --force to overwrite files that already exist at the destination.');
  }
}

main();
