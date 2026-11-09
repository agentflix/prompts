// Recorte ampliado de uma imagem (padrão: a ref) com GRADE a cada 10 ref px e rótulos a cada 50. Para medir posições e tamanhos.
//   node grid.mjs <out.png> x y w h [esc=4]      IMG=<outra imagem> mede o render (ex.: shots/r3/full.png)
import { writeFileSync } from 'node:fs';
import { launch, dataUrl, refSize, REF, cli, usageExit } from './_comum.mjs';
const USO = 'uso: node grid.mjs <out.png> x y w h [esc=4]   (IMG=<imagem> mede outra imagem em vez da ref)';
const [out, x, y, w, h, s = 4] = cli(USO);
if (!h) usageExit(USO);
const b = await launch(), p = await b.newPage(), { W } = refSize();
const d = await p.evaluate(async ({ src, x, y, w, h, s, W }) => {
  const im = new Image(); im.src = src; await im.decode(); const k = im.width / W;
  const c = document.createElement('canvas'); c.width = w * s; c.height = h * s; const g = c.getContext('2d'); g.imageSmoothingQuality = 'high';
  g.drawImage(im, x * k, y * k, w * k, h * k, 0, 0, w * s, h * s); g.font = '11px sans-serif';
  for (let X = Math.ceil(x / 10) * 10; X < x + w; X += 10) { g.strokeStyle = X % 50 ? 'rgba(0,255,255,.18)' : 'rgba(0,255,255,.5)'; g.beginPath(); g.moveTo((X - x) * s + .5, 0); g.lineTo((X - x) * s + .5, h * s); g.stroke(); if (!(X % 50)) { g.fillStyle = '#0ff'; g.fillText(X, (X - x) * s + 2, 11); } }
  for (let Y = Math.ceil(y / 10) * 10; Y < y + h; Y += 10) { g.strokeStyle = Y % 50 ? 'rgba(255,255,0,.18)' : 'rgba(255,255,0,.5)'; g.beginPath(); g.moveTo(0, (Y - y) * s + .5); g.lineTo(w * s, (Y - y) * s + .5); g.stroke(); if (!(Y % 50)) { g.fillStyle = '#ff0'; g.fillText(Y, 2, (Y - y) * s - 2); } }
  return c.toDataURL(); }, { src: dataUrl(process.env.IMG || REF), x: +x, y: +y, w: +w, h: +h, s: +s, W });
writeFileSync(out, Buffer.from(d.split(',')[1], 'base64')); console.log(out); await b.close();
