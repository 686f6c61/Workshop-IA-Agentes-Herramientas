import { existsSync, readdirSync } from 'node:fs';
import { access, readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import remarkRehype from 'remark-rehype';
import rehypeRaw from 'rehype-raw';
import rehypeKatex from 'rehype-katex';
import rehypeStringify from 'rehype-stringify';
import YAML from 'yaml';

const appRoot = process.cwd();

function firstExistingRoot(candidates: string[], requiredPath: string) {
  const found = candidates.find((candidate) => existsSync(path.join(candidate, requiredPath)));
  if (!found) {
    return candidates[0];
  }
  return found;
}

const projectRoot = firstExistingRoot(
  [
    process.env.BOOK_CONTENT_ROOT ? path.resolve(process.env.BOOK_CONTENT_ROOT) : '',
    path.join(appRoot, 'content', 'book'),
    path.basename(appRoot) === 'workshop-ia-2026' ? path.resolve(appRoot, '..') : appRoot,
  ].filter(Boolean),
  'fasciculo-01-fundamentos/indice.yaml',
);
const labAssetsRoot = firstExistingRoot(
  [projectRoot, path.join(appRoot, 'public')],
  'labs',
);
const labKitPathPattern = /labs\/f\d+\/[A-Za-z0-9._-]+\/?/g;
const labRelativeFilePattern =
  /^(?:(?:contracts|data|ops|output|solutions|configs|templates|runbooks|guides|tests|sql|evals)\/[A-Za-z0-9._/-]+|\.github\/workflows\/[A-Za-z0-9._/-]+|(?:Makefile|requirements\.txt|compose\.yaml|compose\.yml|docker-compose\.yaml|docker-compose\.yml)|[A-Za-z0-9._-]+\.(?:py|json|yaml|yml|md|jsonl|csv|txt|toml|sql|sh))$/u;
const labFileTokenPattern =
  /(?:labs\/f\d+\/[A-Za-z0-9._/-]+\.(?:py|json|yaml|yml|md|jsonl|csv|txt|toml|sql|sh)|(?:(?:contracts|data|ops|output|solutions|configs|templates|runbooks|guides|tests|sql|evals)\/[A-Za-z0-9._/-]+|\.github\/workflows\/[A-Za-z0-9._/-]+|(?:Makefile|requirements\.txt|compose\.yaml|compose\.yml|docker-compose\.yaml|docker-compose\.yml)|[A-Za-z0-9._-]+\.(?:py|json|yaml|yml|md|jsonl|csv|txt|toml|sql|sh)))(?![A-Za-z0-9_])/gu;

export interface FascicleConfig {
  slug: string;
  number: number;
  directory: string;
  shortTitle: string;
  title: string;
  description: string;
}

export interface FascicleOverview extends FascicleConfig {
  status: string;
  totalChapters: number;
  availableChapters: number;
  chapters: ChapterIndexEntry[];
  laboratory: FascicleLaboratorySummary;
}

export interface ChapterIndexEntry {
  numero: number;
  archivo: string;
  titulo: string;
  slides?: number[];
  estado?: string;
}

export interface Chapter {
  number: number;
  slug: string;
  fileName: string;
  title: string;
  status: string;
  slides: number[];
  laboratory?: ChapterLaboratorySummary;
  labKits: ChapterLabKit[];
  metadata: Record<string, unknown>;
  html: string;
}

export interface ChapterLabKit {
  path: string;
  label: string;
  zipHref: string;
  readmeHref: string;
  fileCount: number;
  contentSummary: string;
}

export interface Fascicle extends FascicleOverview {
  chapters: Chapter[];
  pendingChapters: ChapterIndexEntry[];
}

export interface ChapterLaboratorySummary {
  anchorId: string;
  challengeCount: number;
}

export interface FascicleLaboratorySummary {
  count: number;
  challengeCount: number;
}

export interface BookDocumentConfig {
  slug: string;
  file: string;
  title: string;
  eyebrow: string;
  description: string;
}

export interface BookDocument extends BookDocumentConfig {
  metadata: Record<string, unknown>;
  html: string;
}

export const FASCICLES: FascicleConfig[] = [
  {
    slug: 'fasciculo-01',
    number: 1,
    directory: 'fasciculo-01-fundamentos',
    shortTitle: 'Los cimientos',
    title: 'Facsímil 01: Los cimientos',
    description:
      'El punto de partida: qué es la IA, cómo aprenden las redes, qué son los tokens y cómo leer los modelos clásicos sin perderse.',
  },
  {
    slug: 'fasciculo-02',
    number: 2,
    directory: 'fasciculo-02-ia-clasica',
    shortTitle: 'Inteligencia clásica',
    title: 'Facsímil 02: Inteligencia clásica',
    description:
      'Búsqueda, heurísticas, restricciones, planificación, juegos y conocimiento simbólico: la IA antes del deep learning, explicada desde problemas concretos.',
  },
  {
    slug: 'fasciculo-03',
    number: 3,
    directory: 'fasciculo-03-arquitecturas-modelos',
    shortTitle: 'Arquitecturas y modelos',
    title: 'Facsímil 03: Arquitecturas y modelos',
    description:
      'Cómo leer un LLM por dentro: Transformer, atención, arquitecturas modernas, modelos abiertos, inferencia y hardware sin perder el criterio de elección.',
  },
  {
    slug: 'fasciculo-04',
    number: 4,
    directory: 'fasciculo-04-caja-herramientas',
    shortTitle: 'La caja de herramientas',
    title: 'Facsímil 04: La caja de herramientas',
    description:
      'APIs, modelos locales, RAG, laboratorios, despliegue y herramientas de trabajo para convertir modelos en soluciones utilizables.',
  },
  {
    slug: 'fasciculo-05',
    number: 5,
    directory: 'fasciculo-05-agentes-orquestacion',
    shortTitle: 'Agentes y orquestación',
    title: 'Facsímil 05: Agentes y orquestación',
    description:
      'Agentes, herramientas, memoria, SDKs, permisos, evaluación y límites operativos explicados como sistemas que toman decisiones alrededor del modelo.',
  },
  {
    slug: 'fasciculo-06',
    number: 6,
    directory: 'fasciculo-06-construir-operar',
    shortTitle: 'Construir y operar',
    title: 'Facsímil 06: Construir y operar',
    description:
      'Ingeniería de sistemas de IA, observabilidad, operación, handoffs y flujos reproducibles para que una solución viva bien fuera del ejemplo.',
  },
  {
    slug: 'fasciculo-07',
    number: 7,
    directory: 'fasciculo-07-evaluar-calibrar-interpretar',
    shortTitle: 'Evaluar, calibrar e interpretar',
    title: 'Facsímil 07: Evaluar, calibrar e interpretar',
    description:
      'Métricas, evaluación, calibración, interpretabilidad y lectura crítica de resultados para no confundir una buena demo con un buen sistema.',
  },
  {
    slug: 'fasciculo-08',
    number: 8,
    directory: 'fasciculo-08-ciencia-datos',
    shortTitle: 'La ciencia de los datos',
    title: 'Facsímil 08: La ciencia de los datos',
    description:
      'Datos, decisión algorítmica, sesgos, pipelines y análisis aplicado como la materia prima que condiciona cualquier sistema de IA.',
  },
  {
    slug: 'fasciculo-09',
    number: 9,
    directory: 'fasciculo-09-seguridad-privacidad-gobernanza',
    shortTitle: 'Seguridad, privacidad y gobernanza',
    title: 'Facsímil 09: Seguridad, privacidad y gobernanza',
    description:
      'Riesgos, privacidad, cumplimiento, gobernanza y controles prácticos para trabajar con IA de forma consciente y trazable.',
  },
  {
    slug: 'fasciculo-10',
    number: 10,
    directory: 'fasciculo-10-aprendizaje-refuerzo',
    shortTitle: 'Aprendizaje por refuerzo',
    title: 'Facsímil 10: Aprendizaje por refuerzo',
    description:
      'Estados, acciones, recompensas, políticas y aplicaciones modernas para entender cómo se aprende a decidir por interacción.',
  },
  {
    slug: 'fasciculo-11',
    number: 11,
    directory: 'fasciculo-11-producto-ux-cierre',
    shortTitle: 'Producto, UX y cierre',
    title: 'Facsímil 11: Producto, UX y cierre',
    description:
      'Decisiones de producto, experiencia de usuario, apéndices y cierre del volumen para llevar el criterio técnico a decisiones reales.',
  },
  {
    slug: 'fasciculo-12',
    number: 12,
    directory: 'fasciculo-12-multimodalidad-percepcion',
    shortTitle: 'IA multimodal',
    title: 'Facsímil 12: IA multimodal y sistemas que perciben',
    description:
      'Imagen, audio, vídeo, documentos, RAG multimodal, evaluación, privacidad y computer use tratados como sistemas de ingeniería.',
  },
];

export const BOOK_DOCUMENTS: BookDocumentConfig[] = [
  {
    slug: 'nota-del-autor',
    file: 'bloque-00/01-nota-del-autor.md',
    title: 'Nota del autor',
    eyebrow: 'Bloque 00',
    description: 'Por qué existe este libro, a quién va dirigido y cómo está pensado para leerse.',
  },
  {
    slug: 'licencia',
    file: 'bloque-00/02-licencia.md',
    title: 'Licencia MIT',
    eyebrow: 'Licencia MIT',
    description: 'Condiciones de uso, atribución y reutilización del material.',
  },
];

export async function getFasciclesOverview(): Promise<FascicleOverview[]> {
  return Promise.all(
    FASCICLES.map(async (config) => {
      const index = await readFascicleIndex(config);
      const availableFiles = await listMarkdownFiles(config);
      const laboratory = await summarizeFascicleLaboratory(config, availableFiles);
      return {
        ...config,
        status: String(index.estado ?? 'en_progreso'),
        totalChapters: Number(index.total_capitulos ?? index.capitulos?.length ?? 0),
        availableChapters: availableFiles.length,
        chapters: normalizeIndexChapters(index.capitulos ?? []),
        laboratory,
      };
    }),
  );
}

export async function getFascicle(slug: string): Promise<Fascicle> {
  const config = FASCICLES.find((item) => item.slug === slug);
  if (!config) {
    throw new Error(`Fascicle not found: ${slug}`);
  }

  const index = await readFascicleIndex(config);
  const indexChapters = normalizeIndexChapters(index.capitulos ?? []);
  const markdownFiles = await listMarkdownFiles(config);
  const fileSet = new Set(markdownFiles);
  const indexedAvailable = indexChapters.filter((chapter) => fileSet.has(chapter.archivo));
  const indexedFileSet = new Set(indexedAvailable.map((chapter) => chapter.archivo));
  const unindexedFiles = markdownFiles
    .filter((fileName) => !indexedFileSet.has(fileName))
    .map((fileName) => ({
      numero: numberFromFileName(fileName),
      archivo: fileName,
      titulo: titleFromFileName(fileName),
      estado: 'revision',
    }));

  const availableEntries = [...indexedAvailable, ...unindexedFiles].sort((a, b) => a.numero - b.numero);
  const chapters = await Promise.all(availableEntries.map((entry) => readChapter(config, entry)));
  const pendingChapters = indexChapters.filter((chapter) => !fileSet.has(chapter.archivo));
  const laboratory = summarizeChaptersLaboratory(chapters);

  return {
    ...config,
    status: String(index.estado ?? 'en_progreso'),
    totalChapters: Number(index.total_capitulos ?? indexChapters.length),
    availableChapters: chapters.length,
    chapters,
    pendingChapters,
    laboratory,
  };
}

export function getBookDocuments(): BookDocumentConfig[] {
  return BOOK_DOCUMENTS;
}

export async function getBookDocument(slug: string): Promise<BookDocument> {
  const config = BOOK_DOCUMENTS.find((item) => item.slug === slug);
  if (!config) {
    throw new Error(`Book document not found: ${slug}`);
  }

  const source = await readFile(path.join(projectRoot, config.file), 'utf8');
  const { metadata, body } = extractFrontmatter(source);
  const bodyWithoutBacklink = body.replace(/\n\[← Volver al facsímil de IA\]\([^)]+\)\s*$/u, '');
  const documentBody = stripDocumentHeadings(bodyWithoutBacklink, [
    config.title,
    config.eyebrow,
    String(metadata.title ?? ''),
  ]);
  const prepared = prepareMarkdown(documentBody, `doc-${slug}`);
  const html = await renderMarkdown(prepared);

  return {
    ...config,
    metadata,
    html: postProcessHtml(html, `doc-${slug}`),
  };
}

function fascicleDir(config: FascicleConfig) {
  return path.join(projectRoot, config.directory);
}

async function readFascicleIndex(config: FascicleConfig): Promise<Record<string, any>> {
  const source = await readFile(path.join(fascicleDir(config), 'indice.yaml'), 'utf8');
  return YAML.parse(source) ?? {};
}

async function listMarkdownFiles(config: FascicleConfig): Promise<string[]> {
  const entries = await readdir(fascicleDir(config));
  return entries.filter((entry) => entry.endsWith('.md')).sort();
}

async function readChapter(config: FascicleConfig, entry: ChapterIndexEntry): Promise<Chapter> {
  const filePath = path.join(fascicleDir(config), entry.archivo);
  await access(filePath);
  const source = await readFile(filePath, 'utf8');
  const { metadata, body } = extractFrontmatter(source);
  const number = Number(metadata.capitulo ?? entry.numero ?? numberFromFileName(entry.archivo));
  const title = String(metadata.title ?? entry.titulo ?? titleFromFileName(entry.archivo));
  const laboratory = summarizeChapterLaboratory(body, config.number, number);
  const labKits = summarizeChapterLabKits(body);
  const processed = prepareMarkdown(body, `f${config.number}-c${number}`);
  const html = await renderMarkdown(processed);

  return {
    number,
    slug: `capitulo-${number}`,
    fileName: entry.archivo,
    title,
    status: String(metadata.estado ?? entry.estado ?? 'revision'),
    slides: Array.isArray(metadata.slides_origen) ? (metadata.slides_origen as number[]) : entry.slides ?? [],
    laboratory,
    labKits,
    metadata,
    html: postProcessHtml(html, `f${config.number}-c${number}`),
  };
}

function summarizeChapterLabKits(body: string): ChapterLabKit[] {
  return extractLabKitPaths(body).map((kitPath) => {
    const files = listLabKitFiles(kitPath);
    return {
      path: kitPath,
      label: labKitLabel(kitPath),
      zipHref: `/lab-zips/${labKitZipName(kitPath)}`,
      readmeHref: `/${kitPath}/README.md`,
      fileCount: files.length,
      contentSummary: labKitContentSummary(files, kitPath),
    };
  });
}

async function summarizeFascicleLaboratory(config: FascicleConfig, markdownFiles: string[]): Promise<FascicleLaboratorySummary> {
  const chapters = await Promise.all(
    markdownFiles.map(async (fileName) => {
      const source = await readFile(path.join(fascicleDir(config), fileName), 'utf8');
      const { metadata, body } = extractFrontmatter(source);
      const chapterNumber = Number(metadata.capitulo ?? numberFromFileName(fileName));
      return summarizeChapterLaboratory(body, config.number, chapterNumber);
    }),
  );

  return summarizeChaptersLaboratory(chapters);
}

function summarizeChaptersLaboratory(
  chapters: Array<Pick<Chapter, 'laboratory'> | ChapterLaboratorySummary | undefined>,
): FascicleLaboratorySummary {
  return chapters.reduce(
    (summary, item) => {
      const laboratory = isChapterLaboratorySummary(item) ? item : item?.laboratory;
      if (!laboratory) return summary;
      return {
        count: summary.count + 1,
        challengeCount: summary.challengeCount + laboratory.challengeCount,
      };
    },
    { count: 0, challengeCount: 0 },
  );
}

function isChapterLaboratorySummary(value: unknown): value is ChapterLaboratorySummary {
  return Boolean(
    value &&
      typeof value === 'object' &&
      'anchorId' in value &&
      'challengeCount' in value,
  );
}

function summarizeChapterLaboratory(
  body: string,
  fascicleNumber: number,
  chapterNumber: number,
): ChapterLaboratorySummary | undefined {
  if (!/^##\s+Laboratorio\s*$/mu.test(body)) {
    return undefined;
  }

  return {
    anchorId: laboratoryAnchorId(fascicleNumber, chapterNumber),
    challengeCount: (body.match(/^###\s+Reto\b.*$/gmu) ?? []).length,
  };
}

function normalizeIndexChapters(chapters: any[]): ChapterIndexEntry[] {
  const seen = new Set<string>();
  return chapters
    .map((chapter) => ({
      numero: Number(chapter.numero),
      archivo: String(chapter.archivo),
      titulo: String(chapter.titulo),
      slides: Array.isArray(chapter.slides) ? chapter.slides.map(Number) : [],
      estado: chapter.estado ? String(chapter.estado) : undefined,
    }))
    .filter((chapter) => {
      const key = `${chapter.numero}:${chapter.archivo}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
}

function extractFrontmatter(source: string) {
  if (!source.startsWith('---')) {
    return { metadata: {}, body: source };
  }

  const end = source.indexOf('\n---', 3);
  if (end === -1) {
    return { metadata: {}, body: source };
  }

  const rawFrontmatter = source.slice(3, end).trim();
  const body = source.slice(end + 4).replace(/^\s+/, '');

  try {
    return {
      metadata: YAML.parse(rawFrontmatter) ?? {},
      body,
    };
  } catch {
    return {
      metadata: {},
      body,
    };
  }
}

function stripDocumentHeadings(source: string, titles: string[]) {
  let output = source.replace(/^#\s+.+\s*\n+/, '');
  const normalizedTitles = titles.filter(Boolean).map(escapeRegExp).join('|');
  if (!normalizedTitles) return output;
  return output.replace(new RegExp(`^##\\s+(?:${normalizedTitles})\\s*\\n+`, 'u'), '');
}

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function prepareMarkdown(source: string, footnotePrefix: string) {
  const withDivs = convertPandocDivs(source);
  const withFootnotes = convertInlineFootnotes(withDivs, footnotePrefix);
  const withLabKitCards = injectLabKitCards(withFootnotes);
  return transformOutsideCodeFences(withLabKitCards, normalizeMathSyntax);
}

function injectLabKitCards(source: string) {
  const lines = source.split('\n');
  const seen = new Set<string>();
  const output: string[] = [];
  let index = 0;

  while (index < lines.length) {
    const line = lines[index];
    const heading = line.trim();

    if (isLabKitSectionHeading(heading)) {
      const sectionStart = index;
      index += 1;
      while (index < lines.length && !lines[index].startsWith('## ')) {
        index += 1;
      }

      const sectionLines = lines.slice(sectionStart, index);
      const sectionText = sectionLines.join('\n');
      const sectionKitPaths = extractLabKitPaths(sectionText).filter((kitPath) => !seen.has(kitPath));

      output.push(sectionLines[0]);
      for (const kitPath of sectionKitPaths) {
        seen.add(kitPath);
        output.push('', labKitCalloutMarkdown(kitPath), '');
      }
      output.push(...sectionLines.slice(1));
      continue;
    }

    output.push(line);
    index += 1;
  }

  return output.join('\n');
}

function isLabKitSectionHeading(heading: string) {
  return heading === '## Manos a la obra' || heading === '## Laboratorio' || heading === '## Vamos a programarlo' || heading === '## Tu turno';
}

function extractLabKitPaths(text: string) {
  const paths: string[] = [];
  const seen = new Set<string>();

  for (const match of text.matchAll(labKitPathPattern)) {
    const kitPath = normalizeLabKitPath(match[0]);
    if (!kitPath || seen.has(kitPath)) continue;
    seen.add(kitPath);
    paths.push(kitPath);
  }

  return paths;
}

function normalizeLabKitPath(value: string) {
  return value.replace(/\/+$/u, '');
}

function labKitZipName(kitPath: string) {
  return `${kitPath.replace(/^labs\//u, '').replace(/\//gu, '-')}.zip`;
}

function labKitLabel(kitPath: string) {
  const [, fascicle, kit] = kitPath.split('/');
  if (kit === 'capitulo-practicas') {
    return `${fascicle.toUpperCase()} · Prácticas del capítulo`;
  }
  const chapterMatch = kit.match(/^c(\d+)-(.+)$/u);
  if (chapterMatch) {
    return `${fascicle.toUpperCase()} · Capítulo ${chapterMatch[1]} · ${humanizeSlug(chapterMatch[2])}`;
  }
  return `${fascicle.toUpperCase()} · ${humanizeSlug(kit)}`;
}

function humanizeSlug(value: string) {
  return value
    .split('-')
    .map((part) => {
      const acronym = {
        ai: 'IA',
        api: 'API',
        csp: 'CSP',
        sat: 'SAT',
        sdk: 'SDK',
        rag: 'RAG',
        llm: 'LLM',
        ml: 'ML',
        json: 'JSON',
        csv: 'CSV',
      }[part.toLowerCase()];
      if (acronym) return acronym;
      const word = {
        accion: 'Acción',
        adaptacion: 'Adaptación',
        algoritmica: 'Algorítmica',
        anatomia: 'Anatomía',
        arquitectonicas: 'Arquitectónicas',
        calibracion: 'Calibración',
        capitulo: 'Capítulo',
        cuantizacion: 'Cuantización',
        decision: 'Decisión',
        diagnostico: 'Diagnóstico',
        evaluacion: 'Evaluación',
        gobernanza: 'Gobernanza',
        heuristica: 'Heurística',
        interpretabilidad: 'Interpretabilidad',
        operacion: 'Operación',
        practicas: 'Prácticas',
        privacidad: 'Privacidad',
        produccion: 'Producción',
        recapitulacion: 'Recapitulación',
        refuerzo: 'Refuerzo',
        simbolico: 'Simbólico',
        validacion: 'Validación',
      }[part.toLowerCase()];
      if (word) return word;
      return part.replace(/^\p{L}/u, (letter) => letter.toUpperCase());
    })
    .join(' ');
}

function labKitCalloutMarkdown(kitPath: string) {
  const readmeHref = `/${kitPath}/README.md`;
  const zipHref = `/lab-zips/${labKitZipName(kitPath)}`;
  const files = listLabKitFiles(kitPath);
  return [
    `<aside class="lab-kit-callout" data-lab-kit="${kitPath}">`,
    `<p class="lab-kit-eyebrow">Kit práctico disponible</p>`,
    `<h3>${labKitLabel(kitPath)}</h3>`,
    `<p>Este material está publicado con la web del facsímil: puedes descargarlo como ZIP o abrir el README para ver archivos, comandos, salidas esperadas y criterio de entrega.</p>`,
    `<p class="lab-kit-contents">${labKitContentSummary(files, kitPath)}</p>`,
    `<div class="lab-kit-actions">`,
    `<a class="lab-kit-download" href="${zipHref}" download>Descargar kit</a>`,
    `<a class="lab-kit-readme" href="${readmeHref}" target="_blank" rel="noopener">Ver README</a>`,
    `</div>`,
    `</aside>`,
  ].join('\n');
}

function labKitContentSummary(files: string[], kitPath: string) {
  const labels = files.map((file) => file.replace(`${kitPath}/`, ''));
  const sections: string[] = [];

  if (labels.includes('README.md')) sections.push('README');
  if (labels.includes('Makefile')) sections.push('Makefile');
  if (labels.includes('requirements.txt')) sections.push('dependencias');
  if (labels.some((label) => label.startsWith('contracts/'))) sections.push('contratos');
  if (labels.some((label) => label.startsWith('data/'))) sections.push('datos');
  if (labels.some((label) => label.startsWith('ops/'))) sections.push('código ejecutable');
  if (labels.some((label) => label.startsWith('tests/'))) sections.push('tests');
  if (labels.some((label) => label.startsWith('output/'))) sections.push('salidas generadas');
  if (labels.some((label) => label.startsWith('solutions/'))) sections.push('solución de referencia');
  if (labels.some((label) => label.startsWith('evidence/'))) sections.push('evidencias');

  const summary = sections.length > 0 ? sections.join(', ') : 'archivos del ejercicio';
  return `El ZIP incluye ${files.length} archivos: ${summary}.`;
}

function convertPandocDivs(source: string) {
  return source.replace(
    /^:::\s*\{\.([A-Za-z0-9_-]+)\}\s*\n([\s\S]*?)\n:::\s*$/gm,
    '<div class="$1">\n\n$2\n\n</div>\n\n',
  );
}

function convertInlineFootnotes(source: string, prefix: string) {
  let output = '';
  const definitions: string[] = [];
  let index = 0;

  for (let i = 0; i < source.length; i += 1) {
    if (source[i] !== '^' || source[i + 1] !== '[') {
      output += source[i];
      continue;
    }

    let depth = 1;
    let cursor = i + 2;

    while (cursor < source.length && depth > 0) {
      if (source[cursor] === '[') depth += 1;
      if (source[cursor] === ']') depth -= 1;
      cursor += 1;
    }

    if (depth !== 0) {
      output += source[i];
      continue;
    }

    index += 1;
    const label = `${prefix}-fn-${index}`;
    const body = source.slice(i + 2, cursor - 1).trim();
    output += `[^${label}]`;
    definitions.push(`[^${label}]: ${body}`);
    i = cursor - 1;
  }

  if (definitions.length === 0) return output;
  return `${output.trimEnd()}\n\n${definitions.join('\n\n')}\n`;
}

function transformOutsideCodeFences(source: string, transform: (segment: string) => string) {
  const segments = source.split(/(^```[\s\S]*?^```\s*$)/gm);
  return segments
    .map((segment) => (segment.startsWith('```') ? segment : transform(segment)))
    .join('');
}

function normalizeMathSyntax(source: string) {
  return source
    .replace(/^[ \t]*\$\$[ \t]*\n([\s\S]*?)\n[ \t]*\$\$[ \t]*$/gm, (_match, tex) => `$$\n${normalizeTex(tex)}\n$$`)
    .replace(/^[ \t]*\$\$([^\n]*?)\$\$[ \t]*$/gm, (_match, tex) => `$$\n${normalizeTex(tex)}\n$$`)
    .replace(/\\\\\[([\s\S]*?)\\\\\]/g, (_match, tex) => `$$\n${normalizeTex(tex)}\n$$`)
    .replace(/\\\[([\s\S]*?)\\\]/g, (_match, tex) => `$$\n${normalizeTex(tex)}\n$$`)
    .replace(/\\\\\(([\s\S]*?)\\\\\)/g, (_match, tex) => `$${normalizeTex(tex)}$`)
    .replace(/\\\(([\s\S]*?)\\\)/g, (_match, tex) => `$${normalizeTex(tex)}$`);
}

function normalizeTex(tex: string) {
  return tex.replace(/\\\\/g, '\\').trim();
}

function normalizeSvgBlocks(source: string) {
  return source.replace(/<svg\b[\s\S]*?<\/svg>/g, (block) =>
    block
      .split('\n')
      .filter((line) => line.trim().length > 0)
      .join('\n'),
  );
}

async function renderMarkdown(source: string) {
  const result = await unified()
    .use(remarkParse)
    .use(remarkGfm)
    .use(remarkMath, { singleDollarTextMath: true })
    .use(remarkRehype, { allowDangerousHtml: true })
    .use(rehypeRaw)
    .use(rehypeKatex, { throwOnError: false, strict: false })
    .use(rehypeStringify, { allowDangerousHtml: true })
    .process(normalizeSvgBlocks(source));

  return String(result);
}

function postProcessHtml(html: string, prefix: string) {
  const processed = html
    .replace(/aria-describedby="footnote-label"/g, `aria-describedby="${prefix}-footnote-label"`)
    .replace(/id="footnote-label"/g, `id="${prefix}-footnote-label"`)
    .replace(/<h2 class="sr-only" id="([^"]+)">Footnotes<\/h2>/g, '<h2 id="$1">Notas</h2>')
    .replace(/<h2>Laboratorio<\/h2>/g, `<h2 id="${prefix}-laboratorio">Laboratorio</h2>`)
    .replace(/<section data-footnotes="" class="footnotes">/g, '<section data-footnotes class="book-footnotes">');

  const labPathSafeHtml = rewriteVisibleLabPathsInCodeBlocks(processed);
  const linkedReferences = linkInlineLabReferences(labPathSafeHtml);
  return enhanceLaboratoryHtml(appendLabFileDownloads(linkedReferences), prefix);
}

function rewriteVisibleLabPathsInCodeBlocks(html: string) {
  return html.replace(/<pre><code([^>]*)>([\s\S]*?)<\/code><\/pre>/g, (match, attributes, body) => {
    if (String(attributes).includes('language-mermaid')) return match;

    const rewritten = String(body)
      .replace(
        /^cd labs\/f\d+\/[A-Za-z0-9._-]+\/?\s*$/gmu,
        '# Descomprime el ZIP del capítulo y ejecuta estos comandos dentro de esa carpeta',
      )
      .replace(/labs\/f\d+\/[A-Za-z0-9._-]+\//gu, 'kit/')
      .replace(/labs\/f\d+\/[A-Za-z0-9._-]+/gu, 'kit');

    return `<pre><code${attributes}>${rewritten}</code></pre>`;
  });
}

function linkInlineLabReferences(html: string) {
  const labRoots = extractRenderedLabRoots(html);

  return html.replace(/<code>([^<]+)<\/code>/g, (match, rawValue) => {
    const value = String(rawValue).trim();
    const href = resolveLabReferenceHref(value, labRoots);
    if (!href) return match;

    if (value.startsWith('labs/') && !path.extname(value)) {
      const kitPath = normalizeLabKitPath(value);
      return `<a class="lab-kit-inline" href="${escapeHtmlAttribute(href)}" target="_blank" rel="noopener" aria-label="${escapeHtmlAttribute(`Abrir README del kit ${labKitLabel(kitPath)}`)}">kit descargable</a>`;
    }

    const displayValue = value.startsWith('labs/') ? labFileDisplayName(value, labRoots) : value;
    return `<a class="lab-file-inline" href="${escapeHtmlAttribute(href)}" target="_blank" rel="noopener"><code>${escapeHtmlText(displayValue)}</code></a>`;
  });
}

function labFileDisplayName(value: string, labRoots: string[]) {
  const stripped = normalizeLabKitPath(value);
  const labRoot = labRoots.find((root) => stripped.startsWith(`${root}/`));
  if (!labRoot) return path.basename(stripped);
  return stripped.replace(`${labRoot}/`, '');
}

function extractRenderedLabRoots(html: string) {
  return Array.from(html.matchAll(/data-lab-kit="([^"]+)"/g), (match) => normalizeLabKitPath(match[1]));
}

function resolveLabReferenceHref(value: string, labRoots: string[]) {
  const stripped = normalizeLabKitPath(value);

  if (stripped.startsWith('labs/')) {
    const absolute = path.join(labAssetsRoot, stripped);
    if (existsSync(absolute)) {
      return path.extname(stripped) ? `/${stripped}` : `/${stripped}/README.md`;
    }
    return undefined;
  }

  if (!labRelativeFilePattern.test(stripped)) {
    return undefined;
  }

  for (const labRoot of labRoots) {
    const direct = path.join(labAssetsRoot, labRoot, stripped);
    if (existsSync(direct)) {
      return `/${labRoot}/${stripped}`;
    }

    if (!stripped.includes('/')) {
      const found = findUniqueFileByName(path.join(labAssetsRoot, labRoot), stripped);
      if (found) {
        return `/${path.relative(labAssetsRoot, found).replace(/\\/gu, '/')}`;
      }
    }
  }

  return undefined;
}

function appendLabFileDownloads(html: string) {
  const labRoots = extractRenderedLabRoots(html);
  if (labRoots.length === 0) return html;

  const linksByLabRoot = collectLabFileDownloadLinks(html, labRoots);
  if (linksByLabRoot.size === 0) return html;

  return html.replace(
    /<aside class="lab-kit-callout" data-lab-kit="([^"]+)">([\s\S]*?)<\/aside>/g,
    (match, labRoot, body) => {
      const links = linksByLabRoot.get(normalizeLabKitPath(labRoot));
      if (!links || links.length === 0 || body.includes('lab-file-downloads')) return match;

      const list = [
        '<div class="lab-file-downloads">',
        '<p>Archivos descargables</p>',
        '<div>',
        ...links.map(
          (link) =>
            `<a class="lab-file-download" href="${escapeHtmlAttribute(link.href)}" download><code>${escapeHtmlText(link.label)}</code></a>`,
        ),
        '</div>',
        '</div>',
      ].join('\n');

      return `<aside class="lab-kit-callout" data-lab-kit="${labRoot}">${body}\n${list}\n</aside>`;
    },
  );
}

function collectLabFileDownloadLinks(html: string, labRoots: string[]) {
  const linksByLabRoot = new Map<string, Array<{ href: string; label: string }>>();
  const seenHrefs = new Set<string>();

  for (const labRoot of labRoots) {
    const links = linksByLabRoot.get(labRoot) ?? [];
    for (const filePath of listLabKitFiles(labRoot)) {
      const href = `/${filePath}`;
      if (seenHrefs.has(href)) continue;
      seenHrefs.add(href);
      links.push({ href, label: filePath.replace(`${labRoot}/`, '') });
    }
    if (links.length > 0) {
      linksByLabRoot.set(labRoot, links);
    }
  }

  for (const codeMatch of html.matchAll(/<code(?:\s[^>]*)?>([\s\S]*?)<\/code>/g)) {
    const text = stripHtml(htmlDecode(codeMatch[1]));
    for (const token of extractLabFileTokens(text)) {
      const href = resolveLabReferenceHref(token, labRoots);
      if (!href || !isDownloadableLabHref(href)) continue;
      const labRoot = labRoots.find((root) => href === `/${root}` || href.startsWith(`/${root}/`));
      if (!labRoot || seenHrefs.has(href)) continue;
      seenHrefs.add(href);
      const label = href.replace(`/${labRoot}/`, '');
      const links = linksByLabRoot.get(labRoot) ?? [];
      links.push({ href, label });
      linksByLabRoot.set(labRoot, links);
    }
  }

  return linksByLabRoot;
}

function listLabKitFiles(labRoot: string) {
  const root = path.join(labAssetsRoot, labRoot);
  if (!existsSync(root)) return [];

  const files: string[] = [];
  const stack = [root];

  while (stack.length > 0) {
    const current = stack.pop();
    if (!current) continue;

    for (const entry of readdirSync(current, { withFileTypes: true })) {
      if (entry.name === '__pycache__') continue;
      const absolute = path.join(current, entry.name);
      const relative = path.relative(root, absolute).replace(/\\/gu, '/');
      if (entry.isDirectory()) {
        stack.push(absolute);
        continue;
      }
      if (entry.name === '.DS_Store' || entry.name === '.gitkeep' || entry.name.endsWith('.pyc')) continue;
      files.push(`${labRoot}/${relative}`);
    }
  }

  return files.sort(compareLabKitFilePaths);
}

function compareLabKitFilePaths(a: string, b: string) {
  const rank = (value: string) => {
    const label = value.split('/').slice(3).join('/');
    if (label === 'README.md') return 0;
    if (label === 'Makefile') return 1;
    if (label === 'requirements.txt') return 2;
    if (label.startsWith('contracts/')) return 3;
    if (label.startsWith('data/')) return 4;
    if (label.startsWith('ops/')) return 5;
    if (label.startsWith('tests/')) return 6;
    if (label.startsWith('sql/')) return 7;
    if (label.startsWith('evals/')) return 8;
    if (label.startsWith('.github/')) return 9;
    if (label.startsWith('output/')) return 10;
    if (label.startsWith('solutions/')) return 11;
    return 12;
  };

  return rank(a) - rank(b) || a.localeCompare(b);
}

function isDownloadableLabHref(href: string) {
  if (href.includes('/__pycache__/') || href.endsWith('.pyc')) return false;
  return path.extname(href) || path.basename(href) === 'Makefile';
}

function extractLabFileTokens(text: string) {
  return Array.from(text.matchAll(labFileTokenPattern), (match) => match[0].trim()).filter(Boolean);
}

function stripHtml(value: string) {
  return value.replace(/<[^>]+>/gu, '');
}

function htmlDecode(value: string) {
  return value
    .replace(/&lt;/gu, '<')
    .replace(/&gt;/gu, '>')
    .replace(/&amp;/gu, '&')
    .replace(/&quot;/gu, '"')
    .replace(/&#x27;/gu, "'");
}

function findUniqueFileByName(root: string, fileName: string) {
  if (!existsSync(root)) return undefined;

  const matches: string[] = [];
  const stack = [root];

  while (stack.length > 0 && matches.length < 2) {
    const current = stack.pop()!;
    for (const entry of readdirSync(current, { withFileTypes: true })) {
      if (entry.name === '__pycache__') continue;
      const absolute = path.join(current, entry.name);
      if (entry.isDirectory()) {
        stack.push(absolute);
      } else if (entry.name === fileName || entry.name.toLowerCase() === fileName.toLowerCase()) {
        matches.push(absolute);
      }
    }
  }

  return matches.length === 1 ? matches[0] : undefined;
}

function escapeHtmlAttribute(value: string) {
  return value.replace(/&/gu, '&amp;').replace(/"/gu, '&quot;').replace(/</gu, '&lt;').replace(/>/gu, '&gt;');
}

function escapeHtmlText(value: string) {
  return value.replace(/&/gu, '&amp;').replace(/</gu, '&lt;').replace(/>/gu, '&gt;');
}

function laboratoryAnchorId(fascicleNumber: number, chapterNumber: number) {
  return `f${fascicleNumber}-c${chapterNumber}-laboratorio`;
}

function enhanceLaboratoryHtml(html: string, prefix: string) {
  const laboratoryHeading = `<h2 id="${prefix}-laboratorio">Laboratorio</h2>`;
  const laboratoryStart = html.indexOf(laboratoryHeading);
  if (laboratoryStart === -1) return html;

  const beforeLaboratory = html.slice(0, laboratoryStart + laboratoryHeading.length);
  const afterHeading = html.slice(laboratoryStart + laboratoryHeading.length);
  const footnotesStart = afterHeading.indexOf('<section data-footnotes');
  const laboratoryBody = footnotesStart === -1 ? afterHeading : afterHeading.slice(0, footnotesStart);
  const afterLaboratory = footnotesStart === -1 ? '' : afterHeading.slice(footnotesStart);

  return `${beforeLaboratory}${wrapLaboratorySections(laboratoryBody)}${afterLaboratory}`;
}

function wrapLaboratorySections(html: string) {
  const challengeHeadingPattern = /<h3>Reto\s+\d+:[\s\S]*?<\/h3>/g;
  const matches = [...html.matchAll(challengeHeadingPattern)];
  if (matches.length === 0) {
    return html;
  }

  let output = '';
  const firstChallengeStart = matches[0].index ?? 0;
  const intro = html.slice(0, firstChallengeStart).trim();
  if (intro) {
    output += `<section class="laboratory-intro">${intro}</section>`;
  }

  for (let index = 0; index < matches.length; index += 1) {
    const heading = matches[index][0];
    const start = matches[index].index ?? 0;
    const bodyStart = start + heading.length;
    const bodyEnd = matches[index + 1]?.index ?? html.length;
    const rawBody = html.slice(bodyStart, bodyEnd).trim();
    const closeHeadingMatch = rawBody.match(/<h3>Cierre del laboratorio<\/h3>/);

    if (!closeHeadingMatch) {
      output += `<section class="laboratory-challenge">${heading}${rawBody}</section>`;
      continue;
    }

    const closeStart = closeHeadingMatch.index ?? rawBody.length;
    const challengeBody = rawBody.slice(0, closeStart).trim();
    const closeBody = rawBody.slice(closeStart).trim();

    output += `<section class="laboratory-challenge">${heading}${challengeBody}</section>`;
    output += `<section class="laboratory-close">${closeBody}</section>`;
  }

  return output;
}

function numberFromFileName(fileName: string) {
  const match = fileName.match(/^(\d+)/);
  return match ? Number(match[1]) : 999;
}

function titleFromFileName(fileName: string) {
  return fileName
    .replace(/^\d+-/, '')
    .replace(/\.md$/, '')
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}
