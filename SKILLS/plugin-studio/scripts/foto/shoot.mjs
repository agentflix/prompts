// Shot da UI: full em DPR 1 (mesma escala da ref, para medir) + recortes ampliados em DPR 3 + erros do console.
//   node shoot.mjs <outDir> [recortes.json | '{"nome":[x,y,w,h],...}']
// Saída: <outDir>/full.png, <outDir>/z3-<nome>.png. Recortes em ref px relativos ao palco (SEL). Ver _comum.mjs para REF/PAGE/Q/SEL.
import { mkdirSync, writeFileSync } from 'node:fs';
import { launch, openUi, shootStage, stageBox, reportErrors, jsonArg, cli } from './_comum.mjs';
const USO = `uso: node shoot.mjs <outDir=shots/atual> [recortes.json | '{"nome":[x,y,w,h]}']   (ref px, relativos ao palco SEL)`;
const [outDir = 'shots/atual', cropsArg] = cli(USO);
const crops = jsonArg(cropsArg, {});
mkdirSync(outDir, { recursive: true });
const b = await launch(), errors = [];
const p1 = await openUi(b, 1, errors);
writeFileSync(`${outDir}/full.png`, await shootStage(p1)); await p1.close();
if (Object.keys(crops).length) {
  const p3 = await openUi(b, 3, errors), o = await stageBox(p3);   // clip é em px da página: soma a origem do palco
  for (const [n, [x, y, w, h]] of Object.entries(crops)) await p3.screenshot({ path: `${outDir}/z3-${n}.png`, clip: { x: o.x + x, y: o.y + y, width: w, height: h } });
}
reportErrors(errors); await b.close();
