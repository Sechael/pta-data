#!/usr/bin/env node
/**
 * Split `lib/items.json` into per-category files under `lib/items/`.
 *
 * Notes:
 * - This is intentionally a 1:1 copy of the current item rows (no shape migration).
 * - Output is sorted by `id` for stable diffs.
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)))
const libDir = path.join(root, 'lib')
const srcPath = path.join(libDir, 'items.json')
const outDir = path.join(libDir, 'items')

function fail(msg) {
  console.error(msg)
  process.exit(1)
}

function slugCategory(category) {
  return String(category || 'other')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '')
}

if (!fs.existsSync(srcPath)) fail(`Missing source file: ${srcPath}`)

let itemsRaw
try {
  itemsRaw = fs.readFileSync(srcPath, 'utf8')
} catch (e) {
  fail(`Cannot read ${srcPath}: ${e}`)
}

let items
try {
  items = JSON.parse(itemsRaw)
} catch (e) {
  fail(`Invalid JSON in lib/items.json: ${e}`)
}

if (!Array.isArray(items)) fail('lib/items.json: expected root array')

fs.mkdirSync(outDir, { recursive: true })

/** @type {Map<string, any[]>} */
const byCategory = new Map()

for (const row of items) {
  const category = row?.category ?? 'Other'
  const key = String(category)
  const arr = byCategory.get(key) ?? []
  arr.push(row)
  byCategory.set(key, arr)
}

/** Stable output order by category filename. */
const outputs = Array.from(byCategory.entries()).map(([category, rows]) => {
  const filename = `${slugCategory(category)}.json`
  return { category, filename, rows }
})

outputs.sort((a, b) => a.filename.localeCompare(b.filename))

for (const { category, filename, rows } of outputs) {
  rows.sort((a, b) => String(a?.id ?? '').localeCompare(String(b?.id ?? '')))
  const outPath = path.join(outDir, filename)
  const outJson = `${JSON.stringify(rows, null, 2)}\n`
  try {
    fs.writeFileSync(outPath, outJson, 'utf8')
  } catch (e) {
    fail(`Cannot write ${outPath}: ${e}`)
  }
  process.stdout.write(`Wrote ${path.relative(root, outPath)} (${rows.length}) from category "${category}"\n`)
}

