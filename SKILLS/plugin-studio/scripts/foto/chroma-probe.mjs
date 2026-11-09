// CROMA por caixa, ref x render: a*/b* (Lab) dos 25% mais claros e dos 25% mais escuros + croma média por pixel (C).
// Detecta metal "sépia/marrom" (b* alto nos claros) que a luminância não mostra: o metal deve ficar neutro como a ref,
// com o calor só nas luzes. Use o mesmo caixas.json do tone-probe.
//   node chroma-probe.mjs <render DPR 1.png> <caixas.json>
import { readFileSync } from 'node:fs';
import { launch, jsonArg, dataUrl, refSize, REF, LAB_JS, cli, usageExit } from './_comum.mjs';
const USO = 'uso: node chroma-probe.mjs <render DPR 1.png> <caixas.json>';
const [img, boxArg] = cli(USO);
const boxes = jsonArg(boxArg, null); if (!img || !boxes) usageExit(USO);
const b = await launch(), p = await b.newPage(), { W } = refSize();
const stat = src => p.evaluate(async ({ src, boxes, W, LAB_JS }) => {
  const lab = new Function(LAB_JS + 'return lab;')();
  const im = new Image(); im.src = src; await im.decode();
  const c = document.createElement('canvas'); c.width = im.width; c.height = im.height; const g = c.getContext('2d'); g.drawImage(im, 0, 0);
  const k = im.width / W, r = {};
  for (const [n, [x, y, w, h]] of Object.entries(boxes)) {
    const d = g.getImageData(Math.round(x * k), Math.round(y * k), Math.max(1, Math.round(w * k)), Math.max(1, Math.round(h * k))).data, px = [];
    for (let i = 0; i < d.length; i += 4) px.push(lab(d[i], d[i + 1], d[i + 2]));
    px.sort((a, b) => a[0] - b[0]); const N = px.length, q = Math.max(1, Math.floor(N / 4));
    const avg = arr => { const s = [0, 0, 0, 0]; for (const v of arr) { s[0] += v[0]; s[1] += v[1]; s[2] += v[2]; s[3] += Math.hypot(v[1], v[2]); } return s.map(v => v / arr.length); };
    r[n] = { lo: avg(px.slice(0, q)), hi: avg(px.slice(N - q)), all: avg(px) };
  }
  return r;
}, { src, boxes, W, LAB_JS });
const R = await stat(dataUrl(REF)), Q = await stat('data:image/png;base64,' + readFileSync(img).toString('base64'));
const f = v => v.toFixed(1).padStart(5);
console.log('caixa        | ref  C   hiL  hi a/b       lo a/b      | rnd  C   hiL  hi a/b       lo a/b      | dC');
for (const k of Object.keys(boxes)) { const a = R[k], q = Q[k];
  console.log(`${k.padEnd(12)} | ${f(a.all[3])} ${f(a.hi[0])} ${f(a.hi[1])}/${f(a.hi[2])} ${f(a.lo[1])}/${f(a.lo[2])} | ${f(q.all[3])} ${f(q.hi[0])} ${f(q.hi[1])}/${f(q.hi[2])} ${f(q.lo[1])}/${f(q.lo[2])} | ${f(q.all[3] - a.all[3])}`); }
await b.close();
