// Recortes ref x render LADO A LADO (ref à esquerda), ampliados. O instrumento principal de cada rodada.
//   node compare.mjs <outDir> <prefixo> <recortes.json | '{"nome":[x,y,w,h,esc],...}'>
//   FULL=1   também grava <prefixo>-full.png (tela cheia ref | render)
//   STACK=1  empilha (ref em cima) em vez de lado a lado
//   DPR=3    resolução do render (recortes nítidos até esc 3-4; parafusos/LEDs: DPR=4 e esc 6-8)
// Coordenadas em ref px. Ex. de recortes por família: knobs, vu, faixa, parafusos, carretel, deck, topo.
import { mkdirSync, writeFileSync } from 'node:fs';
import { launch, openUi, shootStage, reportErrors, jsonArg, dataUrl, refSize, REF, cli } from './_comum.mjs';
const USO = `uso: node compare.mjs <outDir> <prefixo> <recortes.json | '{"nome":[x,y,w,h,esc]}'>   (FULL=1, STACK=1, DPR=3)`;
const [outDir = 'shots/cmp', pre = 'c', cropsArg] = cli(USO);
const crops = jsonArg(cropsArg, {}), DPR = +(process.env.DPR || 3), V = !!process.env.STACK;
mkdirSync(outDir, { recursive: true });
const b = await launch(), errors = [];
const p = await openUi(b, DPR, errors);
const r = 'data:image/png;base64,' + (await shootStage(p)).toString('base64'); await p.close();
const q = await b.newPage();
const imgs = await q.evaluate(async ({ ref, r, crops, V, full, W, H }) => {
  const load = async s => { const i = new Image(); i.src = s; await i.decode(); return i; };
  const A = await load(ref), B = await load(r), ka = A.width / W, kb = B.width / W, out = {};
  for (const [k, [x, y, w, h, s = 3]] of Object.entries(crops)) {
    const c = document.createElement('canvas'); c.width = V ? w * s : w * s * 2 + 12; c.height = V ? h * s * 2 + 12 : h * s;
    const g = c.getContext('2d'); g.fillStyle = '#f0f'; g.fillRect(0, 0, c.width, c.height); g.imageSmoothingQuality = 'high';
    g.drawImage(A, x * ka, y * ka, w * ka, h * ka, 0, 0, w * s, h * s);
    g.drawImage(B, x * kb, y * kb, w * kb, h * kb, V ? 0 : w * s + 12, V ? h * s + 12 : 0, w * s, h * s);
    out[k] = c.toDataURL('image/png');
  }
  if (full) { const c = document.createElement('canvas'); c.width = W * 2 + 12; c.height = H + 40; const g = c.getContext('2d'); g.fillStyle = '#111'; g.fillRect(0, 0, c.width, c.height);
    g.drawImage(A, 0, 40, W, H); g.drawImage(B, W + 12, 40, W, H); g.fillStyle = '#ddd'; g.font = '24px sans-serif'; g.fillText('REF', 12, 28); g.fillText('RENDER', W + 24, 28); out.full = c.toDataURL('image/png'); }
  return out;
}, { ref: dataUrl(REF), r, crops, V, full: !!process.env.FULL, ...refSize() });
for (const [k, v] of Object.entries(imgs)) writeFileSync(`${outDir}/${pre}-${k}.png`, Buffer.from(v.split(',')[1], 'base64'));
console.log(Object.keys(imgs).map(k => `${outDir}/${pre}-${k}.png`).join('\n'));
reportErrors(errors); await b.close();
