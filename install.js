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

function copyDir(src, dest, { force, dryRun, transformFilename }) {
  if (!fs.existsSync(src)) return { copied: 0, skipped: 0 };
  const stats = { copied: 0, skipped: 0 };
  const transform = transformFilename || ((name) => name);

  fs.mkdirSync(dest, { recursive: true });

  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const srcPath = path.join(src, entry.name);

    if (entry.isDirectory()) {
      const destPath = path.join(dest, entry.name);
      const sub = copyDir(srcPath, destPath, { force, dryRun, transformFilename });
      stats.copied += sub.copied;
      stats.skipped += sub.skipped;
      continue;
    }

    if (entry.name.endsWith('.hook.json')) {
      // Descriptor only — install.js reads it directly from the repo to merge/emit
      // hook config, so it has no reason to also live in the target folder.
      continue;
    }

    const destPath = path.join(dest, transform(entry.name));
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

function findHookDescriptors(dir, baseDir) {
  let results = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const entryPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results = results.concat(findHookDescriptors(entryPath, baseDir));
    } else if (entry.name.endsWith('.hook.json')) {
      results.push(entryPath);
    }
  }
  return results;
}

// Reads every *.hook.json under hooksSrcDir once, warning-and-skipping any
// descriptor missing a non-empty `targets` array (no fallback to "claude").
function loadHookDescriptors(hooksSrcDir) {
  if (!fs.existsSync(hooksSrcDir)) return [];

  const descriptors = [];
  for (const descriptorPath of findHookDescriptors(hooksSrcDir, hooksSrcDir)) {
    const descriptor = JSON.parse(fs.readFileSync(descriptorPath, 'utf8'));
    if (!Array.isArray(descriptor.targets) || descriptor.targets.length === 0) {
      console.warn(`  warning: no target for ${path.basename(descriptorPath)}, skipping`);
      continue;
    }
    descriptors.push({ descriptor, descriptorPath });
  }
  return descriptors;
}

function mergeHookDescriptors(hookDescriptors, hooksSrcDir, targetRootDir, { dryRun }) {
  const relevant = hookDescriptors.filter(({ descriptor }) => descriptor.targets.includes('claude'));
  if (relevant.length === 0) return { merged: 0 };

  const settingsPath = path.join(targetRootDir, 'settings.json');
  let settings = {};
  if (fs.existsSync(settingsPath)) {
    settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
  }
  settings.hooks = settings.hooks || {};

  let merged = 0;
  for (const { descriptor, descriptorPath } of relevant) {
    const { event, matcher, runtime } = descriptor;
    const scriptRelPath = path
      .join(path.relative(hooksSrcDir, path.dirname(descriptorPath)), descriptor.script)
      .split(path.sep)
      .join('/');
    const command = `${runtime || 'python3'} "$CLAUDE_PROJECT_DIR/.claude/hooks/${scriptRelPath}"`;
    settings.hooks[event] = settings.hooks[event] || [];

    const alreadyPresent = settings.hooks[event].some(
      (entry) => entry.matcher === matcher && (entry.hooks || []).some((h) => h.command === command)
    );
    if (alreadyPresent) continue;

    let group = settings.hooks[event].find((entry) => entry.matcher === matcher);
    if (!group) {
      group = { matcher, hooks: [] };
      settings.hooks[event].push(group);
    }
    group.hooks.push({ type: 'command', command });
    merged += 1;
  }

  if (merged > 0) {
    if (dryRun) {
      console.log(`  would merge ${merged} hook descriptor(s) into ${path.relative(process.cwd(), settingsPath)}`);
    } else {
      fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2) + '\n');
      console.log(`  merged ${merged} hook descriptor(s) into ${path.relative(process.cwd(), settingsPath)}`);
    }
  }
  return { merged };
}

// Writes one self-contained .github/hooks/<name>.json per descriptor opting
// into the "github-copilot" target — Copilot has no central settings file to
// merge into, unlike Claude. `cwd` points at the script's own directory
// (mirroring GitHub's own documented scripts/ + cwd convention) since the
// raw script is copied alongside every other hook asset regardless of target.
function emitHooks(hookDescriptors, hooksSrcDir, targetRootDir, { dryRun }) {
  const relevant = hookDescriptors.filter(({ descriptor }) => descriptor.targets.includes('github-copilot'));
  if (relevant.length === 0) return { emitted: 0 };

  const destDir = path.join(targetRootDir, 'hooks');
  let emitted = 0;
  for (const { descriptor, descriptorPath } of relevant) {
    const { event, matcher, runtime, script } = descriptor;
    const scriptRelDir = path.relative(hooksSrcDir, path.dirname(descriptorPath)).split(path.sep).join('/');
    const hookName = path.basename(descriptorPath, '.hook.json');
    const destPath = path.join(destDir, `${hookName}.json`);

    const config = {
      version: 1,
      hooks: {
        [event]: [
          {
            type: 'command',
            cwd: scriptRelDir ? `.github/hooks/${scriptRelDir}` : '.github/hooks',
            bash: `${runtime || 'python3'} ./${script}`,
            matcher,
          },
        ],
      },
    };

    if (dryRun) {
      console.log(`  would write: ${path.relative(process.cwd(), destPath)}`);
    } else {
      fs.mkdirSync(destDir, { recursive: true });
      fs.writeFileSync(destPath, JSON.stringify(config, null, 2) + '\n');
      console.log(`  wrote: ${path.relative(process.cwd(), destPath)}`);
    }
    emitted += 1;
  }
  return { emitted };
}

// Per-target divergence lives here: everything else in main() runs the same
// shared copy/manifest loop for every target.
const targetAdapters = {
  claude: {
    transformAgentFilename: (name) => name,
    postCategory(category, hookDescriptors, srcDir, targetRootDir, args) {
      if (category === 'hooks') mergeHookDescriptors(hookDescriptors, srcDir, targetRootDir, args);
    },
  },
  'github-copilot': {
    transformAgentFilename: (name) => name.replace(/\.md$/, '.agent.md'),
    postCategory(category, hookDescriptors, srcDir, targetRootDir, args) {
      if (category === 'hooks') emitHooks(hookDescriptors, srcDir, targetRootDir, args);
    },
  },
};
const defaultAdapter = { transformAgentFilename: (name) => name, postCategory() {} };

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

  let hookDescriptors = null;

  for (const name of selectedTargets) {
    const target = manifest.targets[name];
    if (!target) {
      console.error(`Unknown target "${name}". Known targets: ${targetNames.join(', ')}`);
      process.exitCode = 1;
      continue;
    }

    const adapter = targetAdapters[name] || defaultAdapter;
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

      const transformFilename = category === 'agents' ? adapter.transformAgentFilename : undefined;
      const { copied, skipped } = copyDir(srcDir, destDir, { ...args, transformFilename });
      totalCopied += copied;
      totalSkipped += skipped;

      if (category === 'hooks') {
        if (hookDescriptors === null) hookDescriptors = loadHookDescriptors(srcDir);
        adapter.postCategory(category, hookDescriptors, srcDir, targetRootDir, args);
      }
    }

    console.log(`  -> ${totalCopied} file(s) ${args.dryRun ? 'would be copied' : 'copied'}, ${totalSkipped} skipped`);
  }

  if (!args.force) {
    console.log('\nTip: pass --force to overwrite files that already exist at the destination.');
  }
}

main();
