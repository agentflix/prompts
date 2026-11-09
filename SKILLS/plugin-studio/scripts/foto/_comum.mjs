// Base comum dos scripts de medição da UI fotorrealista (ref x render). Rode os scripts a partir da pasta da UI
// (ex.: <projeto>/ui-pro), onde ficam ref/ e dist/. Tudo configurável por variáveis de ambiente:
//   REF=ref/ref.png        foto de referência (PNG ou JPG)
//   REF_W, REF_H           tamanho de projeto em "ref px" (padrão = tamanho da imagem REF). Coordenadas de caixas/recortes
//                          são sempre em ref px; imagens maiores (render DPR 3, foto em 2x) são escaladas por largura/REF_W.
//   PAGE=dist/index.html   página da UI (arquivo local ou URL http)
//   Q=?freeze              query da página (padrão ?freeze: animações paradas; Q= desliga)
//   SEL=#stage             seletor do palco para o shot (vazio = viewport inteiro)
//   WAIT=4500              espera (ms) depois de abrir a página
//   UI_DIR=<pasta da UI>   projeto da UI quando o script não roda de dentro dela: de lá vêm o playwright e os padrões de REF/PAGE
// Todo script aceita -h/--help: imprime o uso e sai sem abrir navegador nem criar pastas.
import { readFileSync, existsSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { createRequire } from 'node:module';

export const UI_DIR = resolve(process.env.UI_DIR || '.');
export const REF = process.env.REF || join(UI_DIR, 'ref/ref.png');
export const PAGE = process.env.PAGE || join(UI_DIR, 'dist/index.html');

/* -h/--help: imprime o uso e sai (código 0). Chame ANTES de qualquer efeito colateral. Devolve os argumentos. */
export function cli(usage) {
  const args = process.argv.slice(2);
  if (args.some(a => a === '-h' || a === '--help')) { console.log(usage); process.exit(0); }
  return args;
}
/* argumentos insuficientes: imprime o uso e sai (código 1) */
export function usageExit(usage) { console.log(usage); process.exit(1); }

/* playwright vem do node_modules do projeto da UI (UI_DIR ou cwd), nunca é exigido só para mostrar o uso */
function loadPlaywright() {
  const bases = [...new Set([join(UI_DIR, 'package.json'), resolve('package.json'), import.meta.url])];
  for (const base of bases) { try { return createRequire(base)('playwright'); } catch { /* tenta o próximo */ } }
  console.error(`ERRO: playwright não encontrado a partir de ${UI_DIR}${UI_DIR !== process.cwd() ? ' nem de ' + process.cwd() : ''}.
  Rode \`npm i -D playwright\` na pasta da UI (ex.: <projeto>/ui-pro) e rode o script de dentro dela,
  ou aponte o projeto: UI_DIR=<projeto>/ui-pro node <script> ...
  (um playwright só global não é visto pelo Node a partir do projeto.)`);
  process.exit(2);
}
export const QUERY = process.env.Q ?? '?freeze';
export const SEL = process.env.SEL ?? '#stage';
export const WAIT = +(process.env.WAIT || 4500);

/* tamanho de PNG/JPEG lendo só o cabeçalho */
export function imgSize(f) {
  const b = readFileSync(f);
  if (b.readUInt32BE(0) === 0x89504e47) return [b.readUInt32BE(16), b.readUInt32BE(20)];
  for (let i = 2; i < b.length;) {   // JPEG: procura o marcador SOFn
    if (b[i] !== 0xff) { i++; continue; }
    const m = b[i + 1], len = b.readUInt16BE(i + 2);
    if (m >= 0xc0 && m <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(m)) return [b.readUInt16BE(i + 7), b.readUInt16BE(i + 5)];
    i += 2 + len;
  }
  throw new Error('tamanho da imagem não encontrado: ' + f);
}
export function refSize() {
  if (!existsSync(REF)) { console.error(`ERRO: referência não encontrada: ${REF} (rode de dentro da pasta da UI, ou use REF=caminho / UI_DIR=pasta)`); process.exit(1); }
  const [w, h] = imgSize(REF);
  return { W: +process.env.REF_W || w, H: +process.env.REF_H || h };
}
export const dataUrl = f => `data:image/${/\.jpe?g$/i.test(f) ? 'jpeg' : 'png'};base64,` + readFileSync(f).toString('base64');
export const pageUrl = () => (/^https?:/.test(PAGE) ? PAGE : 'file://' + resolve(PAGE)) + QUERY;

export async function launch() {
  const { chromium } = loadPlaywright();
  return chromium.launch({ channel: 'chrome', headless: true, args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'] });
}
/* abre a UI no tamanho de projeto com o DPR pedido; coleta erros/avisos do console */
export async function openUi(browser, dpr = 1, errors = []) {
  const { W, H } = refSize();
  const p = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: dpr });
  p.on('pageerror', e => errors.push('pageerror: ' + e.message));
  p.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') errors.push(m.text()); });
  await p.goto(pageUrl()); await p.waitForTimeout(WAIT);
  return p;
}
/* shot do palco inteiro (Buffer PNG) */
export async function shootStage(p) {
  if (SEL) { const l = p.locator(SEL); if (await l.count()) return l.first().screenshot(); }
  return p.screenshot();
}
export const reportErrors = errors => console.log(errors.length ? 'ERROS/AVISOS:\n' + [...new Set(errors)].join('\n') : 'console limpo');
/* lê JSON de um argumento: caminho de arquivo ou texto JSON */
export const jsonArg = (s, def) => {
  if (s == null) return def;
  try { return existsSync(s) ? JSON.parse(readFileSync(s, 'utf8')) : JSON.parse(s); }
  catch (e) { console.error(`ERRO: JSON inválido em ${s.length > 60 ? s.slice(0, 60) + '…' : s}: ${e.message}`); process.exit(1); }
};
/* caixa do palco (SEL) na página, em px de CSS; {x:0,y:0} sem SEL ou se o seletor não existir */
export async function stageBox(p) {
  if (SEL) { const l = p.locator(SEL); if (await l.count()) { const bb = await l.first().boundingBox(); if (bb) return bb; } }
  return { x: 0, y: 0 };
}

/* código injetado no navegador (string) para Lab: lab(r,g,b) -> [L,a,b] */
export const LAB_JS = `const lin = v => (v /= 255) <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4;
const lab = (R, G, B) => { [R, G, B] = [R, G, B].map(lin); const X = (R * .4124 + G * .3576 + B * .1805) / .95047, Y = R * .2126 + G * .7152 + B * .0722, Z = (R * .0193 + G * .1192 + B * .9505) / 1.08883;
  const f = t => t > .008856 ? Math.cbrt(t) : 7.787 * t + 16 / 116; const [fx, fy, fz] = [X, Y, Z].map(f); return [116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)]; };`;
