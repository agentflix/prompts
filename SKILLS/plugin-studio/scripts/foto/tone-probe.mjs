// Tabela de TONS ref x render por caixa: média RGB, desvio de luminância (sd = contraste local/textura), Δlum, ΔE76, Δa*/Δb*.
//   node tone-probe.mjs <render.png> <caixas.json> [--shoot]
//   caixas: {"nome":[x,y,w,h], "aluClaro":[x,y,w,h,"hi",80], "fita":[x,y,w,h,"lo",80]}  (ref px; 'hi'/'lo' = só pixels com lum >= / < t)
//   <render.png> existente: mede esse arquivo, sem tocar nele (nunca sobrescreve sem --shoot).
//   <render.png> inexistente: faz o shot DPR 1 nesse caminho e mede.
//   --shoot: faz um shot novo e GRAVA POR CIMA de <render.png> (único jeito de sobrescrever). SKIP=1: nunca fotografa.
// Meta da rodada de tons: |Δlum| <= 6 na maioria das caixas, ΔE 1-4, sdx (sd render / sd ref) perto de 1. Δb* > 0 = mais amarelo.
import { writeFileSync, readFileSync, existsSync, mkdirSync } from 'node:fs';
import { dirname } from 'node:path';
import { launch, openUi, shootStage, reportErrors, jsonArg, dataUrl, refSize, REF, LAB_JS, cli, usageExit } from './_comum.mjs';
const USO = `uso: node tone-probe.mjs <render.png> <caixas.json> [--shoot]
  <render.png> existe: só mede (não sobrescreve). Não existe: fotografa nele e mede.
  --shoot: fotografa de novo e sobrescreve <render.png>. SKIP=1: nunca fotografa.`;
const argv = cli(USO), SHOOT = argv.includes('--shoot'), [img, boxArg] = argv.filter(a => a !== '--shoot');
if (!img || !boxArg) usageExit(USO);
const boxes = jsonArg(boxArg, null), has = existsSync(img), shoot = !process.env.SKIP && (SHOOT || !has);
if (!has && !shoot) { console.error(`ERRO: ${img} não existe e SKIP=1 impede o shot.`); process.exit(1); }
const b = await launch(), errors = [];
if (shoot) { const p = await openUi(b, 1, errors); mkdirSync(dirname(img), { recursive: true }); writeFileSync(img, await shootStage(p)); await p.close(); console.log((has ? 'sobrescrito (--shoot): ' : 'shot novo: ') + img); }
else console.log('medindo render existente: ' + img);
const { W } = refSize(), p = await b.newPage();
const stat = src => p.evaluate(async ({ src, boxes, W }) => {
  const im = new Image(); im.src = src; await im.decode();
  const c = document.createElement('canvas'); c.width = im.width; c.height = im.height; const g = c.getContext('2d'); g.drawImage(im, 0, 0);
  const k = im.width / W, r = {}, Y = (d, i) => .2126 * d[i] + .7152 * d[i + 1] + .0722 * d[i + 2];
  for (const [n, [x, y, w, h, mode, th]] of Object.entries(boxes)) {
    const d = g.getImageData(Math.round(x * k), Math.round(y * k), Math.max(1, Math.round(w * k)), Math.max(1, Math.round(h * k))).data;
    let s = [0, 0, 0], l2 = 0, cnt = 0;
    for (let i = 0; i < d.length; i += 4) { const l = Y(d, i); if (mode && (mode === 'hi' ? l < th : l >= th)) continue; s[0] += d[i]; s[1] += d[i + 1]; s[2] += d[i + 2]; l2 += l * l; cnt++; }
    cnt = Math.max(1, cnt); const m = s.map(v => v / cnt), L = .2126 * m[0] + .7152 * m[1] + .0722 * m[2];
    r[n] = { m, L, sd: Math.sqrt(Math.max(0, l2 / cnt - L * L)) };
  }
  return r;
}, { src, boxes, W });
const R = await stat(dataUrl(REF)), Q = await stat('data:image/png;base64,' + readFileSync(img).toString('base64'));
const lab = new Function(LAB_JS + 'return lab;')();
const hex = m => m.map(v => Math.round(v).toString(16).padStart(2, '0')).join('');
let ok = 0; const rows = [];
for (const k of Object.keys(boxes)) {
  const a = R[k], q = Q[k], la = lab(...a.m), lq = lab(...q.m), dE = Math.hypot(la[0] - lq[0], la[1] - lq[1], la[2] - lq[2]), dL = q.L - a.L;
  if (Math.abs(dL) <= 6) ok++;
  rows.push(`${k.padEnd(12)} ref ${hex(a.m)} L${a.L.toFixed(0).padStart(4)} sd${a.sd.toFixed(1).padStart(5)} | rnd ${hex(q.m)} L${q.L.toFixed(0).padStart(4)} sd${q.sd.toFixed(1).padStart(5)} | dL ${dL.toFixed(1).padStart(6)} dE ${dE.toFixed(1).padStart(5)} da ${(lq[1] - la[1]).toFixed(1).padStart(5)} db ${(lq[2] - la[2]).toFixed(1).padStart(5)} sdx ${(q.sd / Math.max(.5, a.sd)).toFixed(2)}`);
}
console.log(rows.join('\n')); console.log(`dentro de |dL| <= 6: ${ok}/${rows.length}`);
if (errors.length) reportErrors(errors); await b.close();
