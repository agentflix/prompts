// Média RGB e faixa de luminância por caixa numa imagem qualquer (rápido; para ref x render use tone-probe.mjs).
//   node probe.mjs <imagem> '{"esq":[120,300,40,40],"meio":[...]}'     (ref px; imagem escalada por largura/REF_W)
import { launch, dataUrl, refSize, jsonArg, cli, usageExit } from './_comum.mjs';
const USO = `uso: node probe.mjs <imagem> '{"nome":[x,y,w,h]}'   (ref px)`;
const [img, boxes] = cli(USO);
if (!boxes) usageExit(USO);
const b = await launch(), p = await b.newPage(), { W } = refSize();
const out = await p.evaluate(async ({ src, boxes, W }) => {
  const im = new Image(); im.src = src; await im.decode(); const k = im.width / W;
  const c = document.createElement('canvas'); c.width = im.width; c.height = im.height; const g = c.getContext('2d'); g.drawImage(im, 0, 0); const r = {};
  for (const [n, [x, y, w, h]] of Object.entries(boxes)) {
    const d = g.getImageData(Math.round(x * k), Math.round(y * k), Math.max(1, Math.round(w * k)), Math.max(1, Math.round(h * k))).data; const s = [0, 0, 0]; let cnt = 0, mn = 999, mx = 0;
    for (let i = 0; i < d.length; i += 4) { s[0] += d[i]; s[1] += d[i + 1]; s[2] += d[i + 2]; cnt++; const l = .2126 * d[i] + .7152 * d[i + 1] + .0722 * d[i + 2]; mn = Math.min(mn, l); mx = Math.max(mx, l); }
    r[n] = s.map(v => Math.round(v / cnt)).join(',') + ` lum ${Math.round(mn)}-${Math.round(mx)}`;
  }
  return r; }, { src: dataUrl(img), boxes: jsonArg(boxes), W });
console.log(out); await b.close();
