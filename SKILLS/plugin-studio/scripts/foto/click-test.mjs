// Teste de gestos: dirige os controles com mouse/teclado reais e imprime window.ui.state() depois de cada passo.
//   node click-test.mjs <roteiro.json | '[...]'>
// Roteiro (coordenadas em ref px = px do viewport, que tem o tamanho da ref):
//   [{"t":"INPUT +","drag":[190,671,-80]}, {"t":"reset","dbl":[190,671]}, {"t":"SPEED","click":[411,682]},
//    {"t":"fino","drag":[190,671,-50],"shift":true}, {"t":"roda","wheel":[190,671,-100]}, {"t":"power","click":[1498,858],"wait":2500},
//    {"t":"api","eval":"ui.set('input',12); return ui.get('input')"}, {"t":"preset ok?","expect":{"preset":"Default Preset"}}]
// Abre sem ?freeze (Q='' por padrão aqui). Sai com código 1 se algum "expect" falhar ou houver erro no console.
process.env.Q ??= '';
const { launch, openUi, jsonArg, reportErrors, cli, usageExit } = await import('./_comum.mjs');
const USO = `uso: node click-test.mjs <roteiro.json | '[{"t":"..","drag":[x,y,dy]},{"click":[x,y]},{"expect":{..}}]'>`;
const steps = jsonArg(cli(USO)[0], null); if (!steps) usageExit(USO);
const b = await launch(), errors = [], p = await openUi(b, 1, errors);
const st = () => p.evaluate(() => window.ui && window.ui.state ? window.ui.state() : null);
const drag = async (x, y, dy) => { await p.mouse.move(x, y); await p.mouse.down(); await p.mouse.move(x, y + dy / 2, { steps: 4 }); await p.mouse.move(x, y + dy, { steps: 4 }); await p.mouse.up(); };
let fail = 0;
for (const s of steps) {
  if (s.shift) await p.keyboard.down('Shift');
  if (s.drag) await drag(...s.drag);
  if (s.click) await p.mouse.click(...s.click);
  if (s.dbl) await p.mouse.dblclick(...s.dbl);
  if (s.wheel) { await p.mouse.move(s.wheel[0], s.wheel[1]); await p.mouse.wheel(0, s.wheel[2]); }
  if (s.shift) await p.keyboard.up('Shift');
  if (s.eval) console.log('eval', s.t || '', JSON.stringify(await p.evaluate(new Function(s.eval))));
  await p.waitForTimeout(s.wait || 120);
  const now = await st(); console.log((s.t || '').padEnd(18), JSON.stringify(now));
  if (s.expect) for (const [k, v] of Object.entries(s.expect)) if (!now || now[k] !== v) { fail++; console.log(`FALHA: ${k} = ${now && now[k]} (esperado ${v})`); }
}
reportErrors(errors); await b.close(); if (fail || errors.length) process.exit(1);
