// Peças reutilizáveis para escrever os decks (arquivos decks/*.js).
// Em cada deck:  const C = require('/caminho/da/skill/scripts/common.js');
//   about(au, min)         -> slide "Sobre a professora" (lê perfil de PROFILE_JSON ou assets/profile.default.json)
//   pause(...)             -> slide de parada ao fim de uma aula de 50 min
//   close(au, min, points, next)
// Os demais slides são objetos simples; veja references/deck-schema.md.
const fs = require('fs'), path = require('path');
const profilePath = process.env.PROFILE_JSON || path.join(__dirname, '..', 'assets', 'profile.default.json');
const P = JSON.parse(fs.readFileSync(profilePath, 'utf8'));
module.exports = {
  profile: P,
  about: (au, min = 2) => ({ k: 'about', a: 0, au, min, title: 'Sobre a professora', name: P.name, role: P.role, facts: P.facts, lattes: P.lattes }),
  pause: (a, au, n, kept, next, ask, min = 2) => ({ k: 'pause', a, au, min, n, title: `Fim da ${n} aula`, kept, next, ask }),
  close: (au, min, points, next) => ({ k: 'close', a: 0, au, min, title: 'Para levar', points, next }),
};
