// Ref e render SOBREPOSTOS num recorte: 'half' (50% cada) mostra deslocamento/tamanho; 'diff' (diferença) mostra o que não bate.
//   node blend.mjs <render.png> <out.png> x y w h [esc=3] [half|diff]     (ref px)
import { writeFileSync } from 'node:fs';
import { launch, dataUrl, refSize, REF, cli, usageExit } from './_comum.mjs';
const USO = 'uso: node blend.mjs <render.png> <out.png> x y w h [esc=3] [half|diff]   (ref px)';
const [rp, out, x, y, w, h, esc = 3, mode = 'half'] = cli(USO);
if (!h) usageExit(USO);
const b = await launch(), p = await b.newPage(), { W } = refSize();
const d = await p.evaluate(async ({ A, B, x, y, w, h, esc, mode, W }) => {
  const ld = async s => { const i = new Image(); i.src = s; await i.decode(); return i; };
  const a = await ld(A), r = await ld(B), ka = a.width / W, kr = r.width / W;
  const c = document.createElement('canvas'); c.width = w * esc; c.height = h * esc; const g = c.getContext('2d');
  g.drawImage(a, x * ka, y * ka, w * ka, h * ka, 0, 0, w * esc, h * esc);
  if (mode === 'diff') g.globalCompositeOperation = 'difference'; else g.globalAlpha = .5;
  g.drawImage(r, x * kr, y * kr, w * kr, h * kr, 0, 0, w * esc, h * esc);
  return c.toDataURL('image/png').split(',')[1]; }, { A: dataUrl(REF), B: dataUrl(rp), x: +x, y: +y, w: +w, h: +h, esc: +esc, mode, W });
writeFileSync(out, Buffer.from(d, 'base64')); console.log(out); await b.close();
