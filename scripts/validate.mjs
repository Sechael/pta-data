#!/usr/bin/env node
/**
 * Validates `lib/*.json`: strict JSON parse, UTF-8, root shapes expected by PTA app consumers.
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)))
const libDir = path.join(root, 'lib')

const FILES = [
  'afflictions.json',
  'items.json',
  'moves.json',
  'pokemon.json',
  'pokemon-gmax.json',
  'pokemon-mega.json',
  'trainer-class-move-pools.json',
  'type-chart.json',
  'weapons.json',
]

function fail(msg) {
  console.error(msg)
  process.exit(1)
}

for (const name of FILES) {
  const fp = path.join(libDir, name)
  if (!fs.existsSync(fp)) {
    fail(`Missing required file: ${fp}`)
  }
}

for (const name of FILES) {
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
    case 'items.json':
    case 'weapons.json':
    case 'pokemon-mega.json':
    case 'pokemon-gmax.json':
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

console.log(`OK: validated ${FILES.length} JSON files under lib/`)
