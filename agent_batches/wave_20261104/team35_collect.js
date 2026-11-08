// Reads verify.py JSON lines from stdin, applies content filters, writes _v.json (chunked) + _v_codes.json
const fs = require('fs');
const readline = require('readline');
const cands = JSON.parse(fs.readFileSync('_team35_candidates.json', 'utf8'));
const byCode = {}; cands.forEach(c => byCode[c.code] = c);
const CATS = new Set(["Sports","Gaming","Jobs","Education","Entertainment","Friendship","News","Islamic","Business","Finance","Buy-Sell","Health","Community","Technology","Crypto","Travel","Music","Movies","Food","Pets","Funny","Girls","Regional","Other"]);
const CNAMES = {MX:'Mexico',CO:'Colombia',VE:'Venezuela',AR:'Argentina',CL:'Chile',PE:'Peru',EC:'Ecuador',BO:'Bolivia',PY:'Paraguay',UY:'Uruguay',BR:'Brazil',CR:'Costa Rica',PA:'Panama',GT:'Guatemala',HN:'Honduras',SV:'El Salvador',NI:'Nicaragua',DO:'Dominican Republic',CU:'Cuba',ES:'Spain',US:'United States',IN:'India',PK:'Pakistan'};
const PAIRS = [
  ['Gaming', ['free fire','fre fire','gta','minecraft','pubg','call of duty','fortnite','gamer','gaming','juegos','roblox','brawl stars']],
  ['Sports', ['futbol','fútbol','football','deportes','sports','cricket','messi']],
  ['Music', ['musica','música','music','reggaeton','rock','kpop','dj','trap']],
  ['Movies', ['peliculas','películas','movies','series','netflix','anime','cine']],
  ['Friendship', ['amistad','amigos','amor y amistad','conocer gente','nuevos amigos','friendship','friends','socializar']],
  ['Girls', ['solteras','solteros y solteras','citas','dating','noviazgo','chicas','singles','pareja']],
  ['Jobs', ['empleo','trabajo','trabajos','ofertas laborales','empleos','jobs','vacantes']],
  ['Business', ['negocios','emprendedores','emprendimiento','business']],
  ['Finance', ['finanzas','dinero','inversiones','trading','forex']],
  ['Buy-Sell', ['ventas','compra','vendo','ofertas','descuentos','tienda','venta de']],
  ['Education', ['educacion','educación','estudiantes','universidad','tareas','clases','cursos','estudio','escuela']],
  ['News', ['noticias','news','ultima hora','última hora']],
  ['Health', ['salud','fitness','gym','dieta','bienestar','ejercicio']],
  ['Technology', ['tecnologia','tecnología','tech','programacion','programación','software']],
  ['Crypto', ['crypto','bitcoin','cripto']],
  ['Travel', ['viajes','travel','turismo','vacaciones']],
  ['Food', ['comida','recetas','cocina','food']],
  ['Pets', ['mascotas','perros','gatos','pets']],
  ['Funny', ['memes','humor','chistes','funny']],
  ['Entertainment', ['entretenimiento','diversión','diversion','farándula']],
  ['Community', ['comunidad','cristianos','dios','biblia','iglesia','vecinos','colonia','barrio','oracion']],
];
const PORN = ['porn','pornhub','xxx','nude','sex video','escort','call girl','fuck','dick','pussy','boobs','anal','bokep','videos porno','porno gratis','putas','sexo explicito'];
const PEMOJI = ['\u{1F975}','\u{1F346}','\u{1F351}','\u{1F51E}','\u{1F4A6}','\u{1F445}','\u{1F444}','\u{1F48B}'];
const SCAM = ['satta','matka','double your money','hyip','paypal receiver','and loader','carding','fullz',' dumps','cvv','phishing','money mule'];
const MINOR = ['teen dating','dating teens','13-17','14-17','menores de edad solteros'];
function mapCat(title, cc) {
  if (CATS.has(cc) && cc !== 'Other') return cc;
  const t = (title || '').toLowerCase();
  for (const [cat, kws] of PAIRS) if (kws.some(k => t.includes(k))) return cat;
  return 'Other';
}
const hasPorn = t => { const l = t.toLowerCase(); return PORN.some(s => l.includes(s)) || PEMOJI.some(e => t.includes(e)); };
const hasScam = t => SCAM.some(s => t.toLowerCase().includes(s));
const hasMinor = t => MINOR.some(s => t.toLowerCase().includes(s));
const TMPLS = [
  c => `A ${c.catw} WhatsApp group for ${c.cn} members to connect, share updates, and chat about ${c.topic}.`,
  c => `Join this active ${c.catw} WhatsApp group from ${c.cn} for daily conversation and ${c.topic} discussions.`,
  c => `A community WhatsApp group in ${c.cn} focused on ${c.catw} topics and ${c.topic} with friendly members.`,
  c => `Connect with people across ${c.cn} in this ${c.catw} WhatsApp group sharing ${c.topic} content and chat.`,
  c => `This ${c.cn} WhatsApp group brings together ${c.catw} fans to talk ${c.topic} and make new friends.`,
];
function cleanTopic(name) {
  const t = name.replace(/[^\w\s\-.&]/gu, ' ').replace(/\s+/g, ' ').trim().split(' ').slice(0, 6).join(' ');
  return t || 'general topics';
}
function makeDesc(name, cat, country) {
  const cn = CNAMES[country] || (country.length === 2 ? country : 'Latin America');
  const ctx = { catw: cat.toLowerCase().replace('-', ' '), cn, topic: cleanTopic(name) };
  let h = 0; for (const ch of name) h = (h * 31 + ch.codePointAt(0)) >>> 0;
  return TMPLS[h % TMPLS.length](ctx);
}
const verified = [], codesDone = [];
const stats = { dead: 0, porn: 0, scam: 0, minors: 0, transport: 0, ratelimited: 0, other: 0 };
const rl = readline.createInterface({ input: process.stdin, terminal: false });
rl.on('line', line => {
  line = line.trim();
  if (!line || line.startsWith('TOVERIFY')) return;
  let r; try { r = JSON.parse(line); } catch (e) { return; }
  codesDone.push(r.code);
  const c = byCode[r.code] || {};
  if (r.st === 200 && r.t) {
    if (hasPorn(r.t)) { stats.porn++; return; }
    if (hasScam(r.t)) { stats.scam++; return; }
    if (hasMinor(r.t)) { stats.minors++; return; }
    const country = /^[A-Z]{2}$/.test(c.country || '') ? c.country : 'International';
    const cat = mapCat(r.t, c.category);
    const name = r.t.length > 120 ? r.t.slice(0, 120) : r.t;
    verified.push({ name, category: cat, country, description: makeDesc(name, cat, country),
                    invite: 'https://chat.whatsapp.com/' + r.code, image: '' });
  } else if (r.st === 200) { stats.dead++; }
  else if (r.st === 'timeout' || r.st === 'error') { stats.transport++; }
  else if (String(r.st).startsWith('429')) { stats.ratelimited++; }
  else { stats.other++; }
});
rl.on('close', () => {
  const CH = 350, OUT = '_v.json';
  try { fs.unlinkSync(OUT); } catch (e) {}
  for (let i = 0; i < verified.length; i += CH) {
    const s = JSON.stringify(verified.slice(i, i + CH)).slice(1, -1);
    if (i === 0) fs.writeFileSync(OUT, '[' + s); else fs.appendFileSync(OUT, ',' + s);
  }
  fs.appendFileSync(OUT, ']');
  // done-codes in small pieces (also serves as resume state)
  fs.writeFileSync('_v_done.json', JSON.stringify(codesDone));
  fs.writeFileSync('_v_codes.json', JSON.stringify(verified.map(v => v.invite.split('/').pop())));
  console.log(JSON.stringify({ lines: codesDone.length, verified: verified.length, ...stats }));
});
