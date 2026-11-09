// Perfil de LUMINÂNCIA ao longo de linhas (1 amostra por ref px). Mede bordas, largura de bisel/fita, fio de luz, raio de peça.
//   node line-probe.mjs <imagem> '[[x0,y0,x1,y1],...]'     (ref px; vale para a ref e para o render)
import { launch, dataUrl, refSize, jsonArg, cli, usageExit } from './_comum.mjs';
const USO = "uso: node line-probe.mjs <imagem> '[[x0,y0,x1,y1],...]'   (ref px)";
const [img, L] = cli(USO);
if (!L) usageExit(USO);
const b = await launch(), p = await b.newPage(), { W } = refSize();
const r = await p.evaluate(async ({ src, L, W }) => {
  const im = new Image(); im.src = src; await im.decode(); const k = im.width / W;
  const c = document.createElement('canvas'); c.width = im.width; c.height = im.height; const g = c.getContext('2d'); g.drawImage(im, 0, 0);
  return L.map(([x0, y0, x1, y1]) => { const n = Math.round(Math.hypot(x1 - x0, y1 - y0)), o = [];
    for (let i = 0; i <= n; i++) { const x = x0 + (x1 - x0) * i / n, y = y0 + (y1 - y0) * i / n, d = g.getImageData(Math.round(x * k), Math.round(y * k), 1, 1).data;
      o.push(`${Math.round(x)},${Math.round(y)}:${Math.round(.2126 * d[0] + .7152 * d[1] + .0722 * d[2])}`); }
    return o.join(' '); }); }, { src: dataUrl(img), L: jsonArg(L), W });
console.log(r.join('\n\n')); await b.close();
