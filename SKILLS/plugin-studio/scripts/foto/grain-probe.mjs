// TEXTURA por caixa, ref x render: grão (desvio de lum - blur 4 px = textura fina) e dx/dy (energia de gradiente:
// dx/dy < 1 = escovado HORIZONTAL, > 1 = fibras verticais). Diz se o escovado/grão está grosso demais ou na direção errada.
//   node grain-probe.mjs <render DPR 1.png> <caixas.json>
import { readFileSync } from 'node:fs';
import { launch, jsonArg, dataUrl, refSize, REF, cli, usageExit } from './_comum.mjs';
const USO = 'uso: node grain-probe.mjs <render DPR 1.png> <caixas.json>';
const [img, boxArg] = cli(USO);
const boxes = jsonArg(boxArg, null); if (!img || !boxes) usageExit(USO);
const b = await launch(), p = await b.newPage(), { W, H } = refSize();
const stat = src => p.evaluate(async ({ src, boxes, W, H }) => {
  const im = new Image(); im.src = src; await im.decode();
  const c = document.createElement('canvas'); c.width = W; c.height = H; const g = c.getContext('2d'); g.drawImage(im, 0, 0, W, H);
  const bl = document.createElement('canvas'); bl.width = W; bl.height = H; const gb = bl.getContext('2d'); gb.filter = 'blur(4px)'; gb.drawImage(c, 0, 0);
  const L = (a, i) => a[i] * .2126 + a[i + 1] * .7152 + a[i + 2] * .0722, out = {};
  for (const [k, [x, y, w, h]] of Object.entries(boxes)) {
    const d = g.getImageData(x, y, w, h).data, e = gb.getImageData(x, y, w, h).data; let s = 0, s2 = 0, n = 0, gx = 0, gy = 0;
    for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) { const o = (j * w + i) * 4, l = L(d, o), hp = l - L(e, o); s += l; s2 += hp * hp; n++;
      if (i + 1 < w) gx += Math.abs(l - L(d, o + 4)); if (j + 1 < h) gy += Math.abs(l - L(d, o + w * 4)); }
    out[k] = `lum ${(s / n).toFixed(0).padStart(3)} grão ${Math.sqrt(s2 / n).toFixed(1).padStart(4)} dx/dy ${(gx / Math.max(1e-6, gy)).toFixed(2)}`;
  } return out; }, { src, boxes, W, H });
const R = await stat(dataUrl(REF)), Q = await stat('data:image/png;base64,' + readFileSync(img).toString('base64'));
for (const k of Object.keys(boxes)) console.log(k.padEnd(12), 'REF', R[k], '| RND', Q[k]);
await b.close();
