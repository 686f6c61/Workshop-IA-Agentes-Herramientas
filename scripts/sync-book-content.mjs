import { cp, mkdir, readdir, rm, stat } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';

const appRoot = process.cwd();
const workspaceRoot = path.resolve(appRoot, '..');
const sourceRoot = process.env.BOOK_SOURCE_ROOT
  ? path.resolve(process.env.BOOK_SOURCE_ROOT)
  : workspaceRoot;
const snapshotRoot = path.join(appRoot, 'content', 'book');

const contentEntries = [
  'bloque-00',
  'fasciculo-01-fundamentos',
  'fasciculo-02-ia-clasica',
  'fasciculo-03-arquitecturas-modelos',
  'fasciculo-04-caja-herramientas',
  'fasciculo-05-agentes-orquestacion',
  'fasciculo-06-construir-operar',
  'fasciculo-07-evaluar-calibrar-interpretar',
  'fasciculo-08-ciencia-datos',
  'fasciculo-09-seguridad-privacidad-gobernanza',
  'fasciculo-10-aprendizaje-refuerzo',
  'fasciculo-11-producto-ux-cierre',
  'fasciculo-12-multimodalidad-percepcion',
  'referencias.bib',
  'glosario.md',
];

async function exists(target) {
  try {
    await stat(target);
    return true;
  } catch {
    return false;
  }
}

async function hasSourceBook() {
  return exists(path.join(sourceRoot, 'fasciculo-01-fundamentos', 'indice.yaml'));
}

async function hasSnapshotBook() {
  return exists(path.join(snapshotRoot, 'fasciculo-01-fundamentos', 'indice.yaml'));
}

function shouldCopy(source) {
  const base = path.basename(source);
  if (base === '.DS_Store') return false;
  if (base === '__pycache__') return false;
  if (base.endsWith('.pyc')) return false;
  return true;
}

async function countMarkdownFiles(root) {
  let count = 0;
  const stack = [root];

  while (stack.length > 0) {
    const current = stack.pop();
    const entries = await readdir(current, { withFileTypes: true });
    for (const entry of entries) {
      const absolute = path.join(current, entry.name);
      if (entry.isDirectory()) {
        stack.push(absolute);
      } else if (entry.name.endsWith('.md')) {
        count += 1;
      }
    }
  }

  return count;
}

async function syncFromSource() {
  await rm(snapshotRoot, { recursive: true, force: true });
  await mkdir(snapshotRoot, { recursive: true });

  for (const entry of contentEntries) {
    const source = path.join(sourceRoot, entry);
    if (!(await exists(source))) continue;
    await cp(source, path.join(snapshotRoot, entry), {
      recursive: true,
      filter: shouldCopy,
    });
  }

  const markdownCount = await countMarkdownFiles(snapshotRoot);
  console.log(`Contenido del libro sincronizado: ${markdownCount} Markdown`);
}

async function main() {
  if (await hasSourceBook()) {
    await syncFromSource();
    return;
  }

  if (await hasSnapshotBook()) {
    const markdownCount = await countMarkdownFiles(snapshotRoot);
    console.log(`Contenido del libro ya disponible: ${markdownCount} Markdown`);
    return;
  }

  throw new Error(
    `No existe contenido fuente en ${sourceRoot} ni snapshot en ${snapshotRoot}`,
  );
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
