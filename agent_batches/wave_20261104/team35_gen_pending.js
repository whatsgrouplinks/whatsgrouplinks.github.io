const fs = require('fs');
const cands = JSON.parse(fs.readFileSync('_team35_candidates.json', 'utf8'));
const CATS = new Set(["Sports","Gaming","Jobs","Education","Entertainment","Friendship","News","Islamic","Business","Finance","Buy-Sell","Health","Community","Technology","Crypto","Travel","Music","Movies","Food","Pets","Funny","Girls","Regional","Other"]);
const PAIRS = [
  ['Gaming', ['free fire','gta','minecraft','pubg','call of duty','fortnite','gamer','gaming','juegos','roblox']],
  ['Sports', ['futbol','fútbol','football','deportes','sports','cricket']],
  ['Music', ['musica','música','music','reggaeton','rock','kpop','dj']],
  ['Movies', ['peliculas','películas','movies','series','netflix','anime','cine']],
  ['Friendship', ['amistad','amigos','amor y amistad','conocer gente','nuevos amigos','friendship','friends']],
  ['Girls', ['solteras','solteros y solteras','citas','dating','noviazgo','chicas','singles']],
  ['Jobs', ['empleo','trabajo','trabajos','ofertas laborales','empleos','jobs','vacantes']],
  ['Business', ['negocios','emprendedores','emprendimiento','business']],
  ['Finance', ['finanzas','dinero','inversiones','trading','forex']],
  ['Buy-Sell', ['ventas','compra','vendo','ofertas','descuentos','tienda','venta de']],
  ['Education', ['educacion','educación','estudiantes','universidad','tareas','clases','cursos','estudio']],
  ['News', ['noticias','news','ultima hora','última hora']],
  ['Health', ['salud','fitness','gym','dieta','bienestar']],
  ['Technology', ['tecnologia','tecnología','tech','programacion','programación','software']],
  ['Crypto', ['crypto','bitcoin','cripto']],
  ['Travel', ['viajes','travel','turismo','vacaciones']],
  ['Food', ['comida','recetas','cocina','food']],
  ['Pets', ['mascotas','perros','gatos','pets']],
  ['Funny', ['memes','humor','chistes','funny']],
  ['Entertainment', ['entretenimiento','diversión','diversion','farándula']],
  ['Community', ['comunidad','cristianos','dios','biblia','iglesia','vecinos','colonia','barrio']],
];
function mapCat(title) {
  const t = (title || '').toLowerCase();
  for (const [cat, kws] of PAIRS) if (kws.some(k => t.includes(k))) return cat;
  return 'Other';
}
const NOTE = 'transport failure — outbound proxy timeouts (all HTTPS unreachable); not attempted; resume from this file';
const out = cands.map(c => {
  const name = (c.name || '').replace(/"/g, "'");
  const cat = (CATS.has(c.category) && c.category !== 'Other') ? c.category : mapCat(name);
  const country = /^[A-Z]{2}$/.test(c.country || '') ? c.country : 'International';
  let desc = (c.description || '').replace(/"/g, "'");
  if (desc.startsWith('Pending verification')) desc = '';
  return { name, category: cat, country, description: desc,
           invite: 'https://chat.whatsapp.com/' + c.code, image: '', note: NOTE };
});
fs.writeFileSync('_team35_pending.json', JSON.stringify(out));
console.log('wrote', out.length, 'records');
