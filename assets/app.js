/* WhatsApp Groups Directory — client-side search & filtering */
(function(){
  var GROUPS = [];
  var shown = 24;

  function el(id){ return document.getElementById(id); }

  function card(g){
    var img = g.image || 'assets/default-group.png';
    var desc = (g.description || '').replace(/ on Groupizo\.?/gi,'').slice(0,140);
    return '<div class="gcard">'
      + '<a href="groups/' + g.slug + '.html"><img class="gimg" loading="lazy" src="' + esc(img) + '" alt="' + esc(g.name) + ' WhatsApp group"></a>'
      + '<div class="gbody">'
      + '<span class="gcat">' + esc(g.category || 'General') + '</span>'
      + '<h3><a href="groups/' + g.slug + '.html">' + esc(g.name) + '</a></h3>'
      + '<p class="gdesc">' + esc(desc) + '</p>'
      + '<a class="joinbtn" href="groups/' + g.slug + '.html">View & Join</a>'
      + '</div></div>';
  }

  function esc(s){
    return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  function render(list){
    var grid = el('group-grid');
    if(!grid) return;
    grid.innerHTML = list.slice(0, shown).map(card).join('');
    var more = el('load-more');
    if(more) more.style.display = list.length > shown ? 'block' : 'none';
    var cnt = el('result-count');
    if(cnt) cnt.textContent = list.length + ' groups found';
  }

  var current = [];
  function applyFilters(){
    var q = (el('search-input') ? el('search-input').value : '').toLowerCase().trim();
    var cat = el('cat-filter') ? el('cat-filter').value : '';
    current = GROUPS.filter(function(g){
      var okCat = !cat || g.category === cat;
      var okQ = !q || (g.name+' '+(g.description||'')+' '+(g.category||'')).toLowerCase().indexOf(q) >= 0;
      return okCat && okQ;
    });
    shown = 24;
    render(current);
  }

  function init(){
    var dataEl = el('groups-data');
    if(dataEl){
      try{ GROUPS = JSON.parse(dataEl.textContent); }catch(e){ GROUPS = []; }
      boot();
    } else {
      // Load the directory dataset from groups.json (keeps index.html small)
      fetch('groups.json').then(function(r){ return r.json(); }).then(function(data){
        GROUPS = (data || []).map(function(g){
          return { name: g.name, slug: g.slug, category: g.category || 'General',
                   description: g.description || '', image: g.image || '' };
        });
        boot();
      }).catch(function(){ boot(); });
    }
  }

  function boot(){
    var ld = el('grid-loading');
    if(ld) ld.style.display = 'none';
    current = GROUPS.slice();
    render(current);
    var si = el('search-input');
    if(si){
      si.addEventListener('input', applyFilters);
      // support ?q= param
      var q = new URLSearchParams(location.search).get('q');
      if(q){ si.value = q; applyFilters(); }
    }
    var cf = el('cat-filter');
    if(cf) cf.addEventListener('change', applyFilters);
    var more = el('load-more');
    if(more) more.addEventListener('click', function(){ shown += 24; render(current); });
    // category cards on homepage filter
    document.querySelectorAll('[data-cat-link]').forEach(function(a){
      a.addEventListener('click', function(e){
        var cf2 = el('cat-filter');
        if(cf2){ cf2.value = a.getAttribute('data-cat-link'); applyFilters(); }
      });
    });
  }

  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
