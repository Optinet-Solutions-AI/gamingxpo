import sharp from 'sharp';
import { readdir, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';

const SRC  = '.tmp/cleaned';
const DEST = 'public/images/portfolio';
const WIDTHS = [640, 960, 1440, 1920];

const all = await readdir(SRC, { withFileTypes: true });
const files = all.filter(f => f.isFile() && /\.(jpe?g|png|webp)$/i.test(f.name));

for (const f of files) {
  const slug = path.parse(f.name).name.toLowerCase().replace(/[^a-z0-9-]+/g, '-').replace(/^-+|-+$/g, '');
  const outDir = path.join(DEST, slug);
  if (!existsSync(outDir)) await mkdir(outDir, { recursive: true });
  const input = path.join(SRC, f.name);
  for (const w of WIDTHS) {
    const base = sharp(input).resize({ width: w, withoutEnlargement: true });
    await base.clone().avif({ quality: 60 }).toFile(path.join(outDir, `${w}.avif`));
    await base.clone().webp({ quality: 78 }).toFile(path.join(outDir, `${w}.webp`));
  }
  console.log(`${slug} -> ${WIDTHS.length} sizes x 2 formats`);
}

console.log(`Done. Processed ${files.length} images.`);
