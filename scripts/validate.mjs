#!/usr/bin/env node
/**
 * Validates `lib/*.json`: strict JSON parse, UTF-8, root shapes expected by PTA app consumers.
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)))
const libDir = path.join(root, 'lib')

const ROOT_FILES = [
  'afflictions.json',
  'moves.json',
  'pokemon.json',
  'pokemon-mega.json',
  'trainer-class-move-pools.json',
  'type-chart.json',
  'weapons.json',
]
const itemsDir = path.join(libDir, 'items')

function itemBundleFiles() {
  if (!fs.existsSync(itemsDir)) fail(`Missing required directory: ${itemsDir}`)
  const files = fs
    .readdirSync(itemsDir, { withFileTypes: true })
    .filter((d) => d.isFile() && d.name.endsWith('.json'))
    .map((d) => d.name)
    .sort()
  if (files.length === 0) fail(`No item bundle JSON files found in: ${itemsDir}`)
  return files
}

function fail(msg) {
  console.error(msg)
  process.exit(1)
}

for (const name of ROOT_FILES) {
  const fp = path.join(libDir, name)
  if (!fs.existsSync(fp)) {
    fail(`Missing required file: ${fp}`)
  }
}

for (const name of ROOT_FILES) {
  const fp = path.join(libDir, name)
  let raw
  try {
    raw = fs.readFileSync(fp)
  } catch (e) {
    fail(`Cannot read ${fp}: ${e}`)
  }
  if (raw.length >= 3 && raw[0] === 0xef && raw[1] === 0xbb && raw[2] === 0xbf) {
    console.warn(`[warn] UTF-8 BOM present (allowed but discouraged): ${name}`)
  }

  let data
  try {
    data = JSON.parse(raw.toString('utf8'))
  } catch (e) {
    fail(`Invalid JSON in ${name}: ${e}`)
  }

  switch (name) {
    case 'pokemon.json':
    case 'moves.json':
    case 'weapons.json':
    case 'pokemon-mega.json':
      if (!Array.isArray(data) || data.length === 0) {
        fail(`${name}: expected non-empty root array`)
      }
      break
    case 'afflictions.json':
      if (
        typeof data !== 'object' ||
        data === null ||
        !Array.isArray(data.entries) ||
        data.entries.length === 0
      ) {
        fail(`${name}: expected object with non-empty entries array`)
      }
      break
    case 'trainer-class-move-pools.json':
      if (typeof data !== 'object' || data === null || Object.keys(data).length === 0) {
        fail(`${name}: expected non-empty object`)
      }
      break
    case 'type-chart.json':
      if (
        typeof data !== 'object' ||
        data === null ||
        !Array.isArray(data.defendingTypes) ||
        !Array.isArray(data.matrixRows)
      ) {
        fail(`${name}: expected object with defendingTypes and matrixRows arrays`)
      }
      break
    default:
      fail(`Unhandled file in validator: ${name}`)
  }
}

for (const name of itemBundleFiles()) {
  const fp = path.join(itemsDir, name)
  let raw
  try {
    raw = fs.readFileSync(fp)
  } catch (e) {
    fail(`Cannot read ${fp}: ${e}`)
  }
  let data
  try {
    data = JSON.parse(raw.toString('utf8'))
  } catch (e) {
    fail(`Invalid JSON in items/${name}: ${e}`)
  }
  if (!Array.isArray(data) || data.length === 0) {
    fail(`items/${name}: expected non-empty root array`)
  }
}

const itemCount = itemBundleFiles().length
console.log(`OK: validated ${ROOT_FILES.length + itemCount} JSON files under lib/`)
