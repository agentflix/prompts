// Perfil POLAR de cor num raio: ângulo horário a partir do topo -> média RGB (janela ±2° x ±1 px).
// Mede onde ficam os lóbulos claros/vales de uma tampa de knob, anel de LED, flange de carretel, tampa de guia.
//   node polar-probe.mjs <imagem> cx cy r [passo°=15]     (cx, cy, r em ref px; vale para a ref e para o render)
import { launch, dataUrl, refSize, cli, usageExit } from './_comum.mjs';
const USO = 'uso: node polar-probe.mjs <imagem> cx cy r [passo°=15]   (ref px)';
const [img, cx, cy, r, st = 15] = cli(USO);
if (!r) usageExit(USO);
const b = await launch(), p = await b.newPage(), { W } = refSize();
const o = await p.evaluate(async ({ src, cx, cy, r, st, W }) => {
  const im = new Image(); im.src = src; await im.decode(); const k = im.width / W;
  const c = document.createElement('canvas'); c.width = im.width; c.height = im.height; const g = c.getContext('2d'); g.drawImage(im, 0, 0); const out = [];
  for (let a = 0; a < 360; a += st) { const s = [0, 0, 0]; let n = 0;
    for (let da = -2; da <= 2; da++) for (let dr = -1; dr <= 1; dr++) { const t = (a + da) * Math.PI / 180, R = r + dr, d = g.getImageData(Math.round((cx + Math.sin(t) * R) * k), Math.round((cy - Math.cos(t) * R) * k), 1, 1).data; s[0] += d[0]; s[1] += d[1]; s[2] += d[2]; n++; }
    const m = s.map(v => Math.round(v / n)); out.push(`${String(a).padStart(3)}°: ${m.join(',')} L${Math.round(.2126 * m[0] + .7152 * m[1] + .0722 * m[2])}`); }
  return out.join('\n'); }, { src: dataUrl(img), cx: +cx, cy: +cy, r: +r, st: +st, W });
console.log(o); await b.close();
