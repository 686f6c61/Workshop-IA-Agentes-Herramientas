import { cp, mkdir, readdir, rm, stat } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import process from 'node:process';

const workspaceRoot = path.resolve(process.cwd(), '..');
const labsRoot = process.env.LABS_ROOT
  ? path.resolve(process.env.LABS_ROOT)
  : path.join(workspaceRoot, 'labs');
const publicRoot = path.join(process.cwd(), 'public');
const publicLabsRoot = path.join(publicRoot, 'labs');
const zipRoot = path.join(publicRoot, 'lab-zips');

async function exists(target) {
  try {
    await stat(target);
    return true;
  } catch {
    return false;
  }
}

function zipNameForKit(fascicleDir, kitDir) {
  return `${fascicleDir}-${kitDir}.zip`;
}

async function listKitRoots() {
  const kits = [];
  const fascicleDirs = await readdir(labsRoot);
  for (const fascicleDir of fascicleDirs.sort()) {
    const fasciclePath = path.join(labsRoot, fascicleDir);
    if (!(await stat(fasciclePath)).isDirectory()) continue;

    const kitDirs = await readdir(fasciclePath);
    for (const kitDir of kitDirs.sort()) {
      const kitPath = path.join(fasciclePath, kitDir);
      if ((await stat(kitPath)).isDirectory()) {
        kits.push({ fascicleDir, kitDir, kitPath });
      }
    }
  }
  return kits;
}

async function zipKit({ fascicleDir, kitDir, kitPath }) {
  const output = path.join(zipRoot, zipNameForKit(fascicleDir, kitDir));
  const result = spawnSync('zip', ['-qr', output, '.', '-x', '*/__pycache__/*', '*.pyc', '*.gitkeep', '.DS_Store'], {
    cwd: kitPath,
    stdio: 'inherit',
  });

  if (result.status !== 0) {
    throw new Error(`No se pudo generar ${output}`);
  }
}

async function main() {
  if (!(await exists(labsRoot))) {
    const hasPublicLabs = await exists(publicLabsRoot);
    const hasZipRoot = await exists(zipRoot);
    const zipFiles = hasZipRoot ? (await readdir(zipRoot)).filter((file) => file.endsWith('.zip')) : [];

    if (hasPublicLabs && zipFiles.length > 0) {
      console.log(`Kits ya disponibles en public/: ${zipFiles.length}`);
      return;
    }

    throw new Error(
      `No existe la carpeta labs en ${labsRoot} y tampoco hay kits public/labs + public/lab-zips listos`,
    );
  }

  await rm(publicLabsRoot, { recursive: true, force: true });
  await rm(zipRoot, { recursive: true, force: true });
  await mkdir(publicRoot, { recursive: true });
  await mkdir(zipRoot, { recursive: true });
  await cp(labsRoot, publicLabsRoot, {
    recursive: true,
    filter: (source) => {
      const base = path.basename(source);
      return base !== '__pycache__' && !base.endsWith('.pyc') && base !== '.gitkeep' && base !== '.DS_Store';
    },
  });

  const kits = await listKitRoots();
  for (const kit of kits) {
    await zipKit(kit);
  }

  console.log(`Kits sincronizados: ${kits.length}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
