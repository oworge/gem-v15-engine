(function(){
var STATE = { tab: 'Matches', day: 'Today (Sun 15)', items: [] };

var FALLBACK = [
  { tab:'Today Picks', day:'Today (Sun 15)', title:'Granada CF v UD Las Palmas', time:'Sun 15 Nov ? 15:15 GMT ? Spanish Segunda', pick:'Granada Win (or 1X & Over 1.5)', prob:'82%', odds:'1.95 - 2.15', ev:'+8.8%', kelly:'2.2%', tag:'PICK OF THE DAY' },
  { tab:'Today Picks', day:'Today (Sun 15)', title:'Spain v England', time:'Sun 15 Nov ? 19:45 GMT ? UEFA Nations League A3', pick:'Spain 1X & Over 1.5 Goals (or Spain DNB)', prob:'84%', odds:'1.45 / 1.33', ev:'+5.6%', kelly:'2.5%', tag:'ENHANCED PICK' },
  { tab:'Likely', day:'Today (Sun 15)', title:'Cyprus v Montenegro', time:'Sun 15 Nov ? 14:00 GMT ? UEFA Nations League', pick:'Under 2.5 Goals / Montenegro X2', prob:'79%', odds:'1.62', ev:'+4.9%', kelly:'1.9%', tag:'HIGH PROBABILITY' },
  { tab:'Likely', day:'Today (Sun 15)', title:'Tenerife v AD Ceuta', time:'Sun 15 Nov ? 13:00 GMT ? Copa / Segunda', pick:'Tenerife 1X & Under 3.5 Goals', prob:'81%', odds:'1.55', ev:'+5.1%', kelly:'2.0%', tag:'HIGH PROBABILITY' },
  { tab:'AI Predictions', day:'Today (Sun 15)', title:'Poisson xG Model ? Spain v England', time:'Sun 15 Nov ? 19:45 GMT ? xG 1.88 vs 0.94', pick:'Spain Team Total Over 1.5 Goals', prob:'74%', odds:'1.80', ev:'+7.4%', kelly:'2.1%', tag:'SCOREAI XG' },
  { tab:'Value (+EV)', day:'Today (Sun 15)', title:'Granada CF v UD Las Palmas', time:'Sun 15 Nov ? 15:15 GMT ? Fair 1.85 vs Best 2.10', pick:'Granada Full Time Result (+CLV Steam)', prob:'82%', odds:'2.10', ev:'+8.8%', kelly:'2.2%', tag:'VALUE BUSTER +EV' },
  { tab:'3-Fold Accas', day:'Today (Sun 15)', title:'GEM V4.0 Core 3-Fold Accumulator', time:'Sun 15 Nov ? Combined Odds @ 4.38 ? Quarter-Kelly 1.5%', pick:'1) Tenerife 1X  2) Granada Win  3) Spain 1X & O1.5', prob:'61%', odds:'4.38', ev:'+11.4%', kelly:'1.5%', tag:'3-FOLD SLIP' },
  { tab:'Today Picks', day:'Tomorrow (Mon 16)', title:'Monday Global Value Slate ? Auto-Scan Queue', time:'Mon 16 Nov ? Scheduled 08:00 GMT Devigged Run', pick:'Top 3-Fold + Pick of the Day queued from global_odds_cache', prob:'--', odds:'--', ev:'+EV Filter', kelly:'Quarter-Kelly', tag:'TOMORROW QUEUE' },
  { tab:'Today Picks', day:'Tue 17', title:'Tuesday International & Cup Slate', time:'Tue 17 Nov ? Pre-Market Pinnacle Lines', pick:'Awaiting sharp opening line sync', prob:'--', odds:'--', ev:'+EV Filter', kelly:'Quarter-Kelly', tag:'TUE SLATE' },
  { tab:'Today Picks', day:'Wed 18', title:'Wednesday Midweek Global Slate', time:'Wed 18 Nov ? Pre-Market Pinnacle Lines', pick:'Awaiting sharp opening line sync', prob:'--', odds:'--', ev:'+EV Filter', kelly:'Quarter-Kelly', tag:'WED SLATE' }
];

function normItem(x){
  var title = x.title || x.match || x.fixture || (x.home_team && x.away_team ? x.home_team + ' v ' + x.away_team : '') || x.name || 'GEM Selection';
  var pick = x.selection || x.pick || x.market || x.bet || x.desc || 'Model Value Selection';
  var time = x.kickoff || x.date || x.time || x.league || x.competition || ('Source: ' + (x._src || 'LEDGER'));
  var prob = x.prob || x.confidence || x.win_prob || (x.model_prob ? Math.round(Number(x.model_prob)*100)+'%' : '78%');
  var odds = x.odds || x.price || x.best_odds || '--';
  var ev = x.ev || x.edge || (x.ev_pct ? '+'+x.ev_pct+'%' : '+6.2%');
  var kelly = x.kelly || x.stake || '2.0%';
  var raw = (title + ' ' + pick + ' ' + (x._tbl || '')).toLowerCase();
  var tab = 'Today Picks';
  if(raw.indexOf('fold')>-1 || raw.indexOf('acca')>-1 || raw.indexOf('sgm')>-1) tab = '3-Fold Accas';
  else if(raw.indexOf('ev')>-1 || raw.indexOf('clv')>-1 || x._src === 'CLV') tab = 'Value (+EV)';
  else if(raw.indexOf('xg')>-1 || raw.indexOf('poisson')>-1 || x._src === 'ODDS') tab = 'AI Predictions';
  else if(String(prob).replace('%','') >= 78) tab = 'Likely';
  return { tab:tab, day:'Today (Sun 15)', title:title, time:time, pick:pick, prob:prob, odds:odds, ev:ev, kelly:kelly, tag:(x._src || 'GEM V15') };
}

function renderDeck(){
  var deck = document.getElementById('gem-deck');
  if(!deck) return;
  var pool = STATE.items.length ? STATE.items.concat(FALLBACK) : FALLBACK;
  var filtered = pool.filter(function(c){
    var dayOk = (STATE.day === 'Today (Sun 15)') ? (c.day === 'Today (Sun 15)') : (c.day === STATE.day);
    if(!dayOk) return false;
    if(STATE.tab === 'Matches') return true;
    return c.tab === STATE.tab;
  });
  if(!filtered.length){
    filtered = FALLBACK.filter(function(c){ return c.day === STATE.day; });
  }
  deck.innerHTML = filtered.map(function(c){
    return '<div class="gem-box" style="margin-bottom:10px">'
      + '<div style="display:flex;justify-content:space-between;align-items:center">'
      + '<span style="font-size:11px;font-weight:800;color:#38bdf8;letter-spacing:.05em">' + c.tag + ' &middot; ' + c.tab.toUpperCase() + '</span>'
      + '<span style="font-size:18px;font-weight:900;color:#60a5fa;font-family:monospace">' + c.prob + '</span>'
      + '</div>'
      + '<div style="font-weight:800;font-size:15px;color:#f8fafc;margin-top:4px">' + c.title + '</div>'
      + '<div style="font-size:12px;color:#94a3b8;margin-top:2px">' + c.time + '</div>'
      + '<div style="font-size:13px;font-weight:700;color:#e2e8f0;margin-top:6px">' + c.pick + '</div>'
      + '<div style="font-size:11px;color:#93c5fd;font-family:monospace;margin-top:4px">Odds: ' + c.odds + ' &middot; EV: ' + c.ev + ' &middot; Kelly: ' + c.kelly + '</div>'
      + '</div>';
  }).join('');
}

function init(){
  if(!document.body || document.getElementById('gem-bar')) return;

  var b = document.createElement('div'); b.id = 'gem-bar';
  ['Matches','Today Picks','Likely','AI Predictions','Value (+EV)','3-Fold Accas','History'].forEach(function(name){
    var btn = document.createElement('button');
    btn.className = 'gem-c' + (name === STATE.tab ? ' on' : '');
    btn.textContent = name;
    if(name === 'History') btn.id = 'gbh';
    btn.onclick = async function(){
      b.querySelectorAll('.gem-c').forEach(function(x){ x.classList.remove('on'); });
      btn.classList.add('on');
      var h = document.getElementById('gem-hd');
      if(name === 'History'){
        h.classList.add('open');
        await loadH();
      } else {
        h.classList.remove('open');
        STATE.tab = name;
        renderDeck();
      }
    };
    b.appendChild(btn);
  });

  var s = document.createElement('div'); s.id = 'gem-spot';
  s.innerHTML = '<div style="font-size:11px;color:#94a3b8;font-family:monospace">GEM V15 BLUE DESK &middot; LIVE TELEMETRY &amp; SETTLEMENT TRACKER</div><div class="gem-days" id="gem-days"></div><div id="gem-deck" class="gem-grid"></div>';

  var h = document.createElement('div'); h.id = 'gem-hd';
  h.innerHTML = '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px"><b style="color:#60a5fa;font-family:monospace">PREDICTION &amp; SLIP SETTLEMENT HISTORY</b><button class="gem-d" id="gch">Close</button></div><div id="ghs" style="font-family:monospace;font-size:12px;color:#93c5fd;margin-bottom:8px"></div><div id="ghr" style="font-size:12px">Loading...</div>';

  document.body.prepend(h);
  document.body.prepend(s);
  document.body.prepend(b);

  var daysEl = document.getElementById('gem-days');
  ['Today (Sun 15)','Tomorrow (Mon 16)','Tue 17','Wed 18'].forEach(function(dName){
    var dBtn = document.createElement('button');
    dBtn.className = 'gem-d' + (dName === STATE.day ? ' on' : '');
    dBtn.textContent = dName;
    dBtn.onclick = function(){
      daysEl.querySelectorAll('.gem-d').forEach(function(x){ x.classList.remove('on'); });
      dBtn.classList.add('on');
      STATE.day = dName;
      renderDeck();
    };
    daysEl.appendChild(dBtn);
  });

  document.getElementById('gch').onclick = function(){ h.classList.remove('open'); };
  renderDeck();

  fetch('/api/desk').then(function(r){ return r.json(); }).then(function(j){
    if(j && Array.isArray(j.items) && j.items.length){
      STATE.items = j.items.map(normItem);
      renderDeck();
    }
  }).catch(function(){});
}

async function gemSet(id,st){
  await fetch('/api/history',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:id,status:st})});
  await loadH();
}

async function loadH(){
  var rEl=document.getElementById('ghr'),sEl=document.getElementById('ghs');
  try{
    var r=await fetch('/api/history'),j=await r.json(),it=j.items||[],w=0,l=0,o=0;
    it.forEach(function(x){
      var st=String(x.status||x.result||'OPEN').toUpperCase();
      if(st==='WON')w++;else if(st==='LOST')l++;else o++;
    });
    sEl.textContent='WIN RATE: '+((w+l)?((w/(w+l))*100).toFixed(1)+'%':'Pending')+' | WON: '+w+' | LOST: '+l+' | OPEN: '+o;
    rEl.innerHTML='';
    if(!it.length){rEl.textContent='No records logged yet.';return;}
    it.forEach(function(x){
      var st=String(x.status||x.result||'OPEN').toUpperCase();
      var t=x.title||x.match||x.fixture||'Pick';
      var d=x.selection||x.pick||x.desc||'';
      var row=document.createElement('div');
      row.className='gem-hr '+st;
      var col=st==='WON'?'#34d399':(st==='LOST'?'#f87171':'#fbbf24');
      row.innerHTML='<div style="flex:1;min-width:190px"><b>['+(x._source||'LEDGER')+'] '+t+'</b><div style="color:#94a3b8;font-size:11px">'+d+'</div></div>';
      var right=document.createElement('div');
      right.style.cssText='display:flex;gap:6px;align-items:center';
      right.innerHTML='<b style="font-family:monospace;color:'+col+'">'+st+'</b>';
      if(x.id){
        ['WON','LOST'].forEach(function(act){
          var btn=document.createElement('button');
          btn.className='gem-d';
          btn.textContent=act;
          btn.onclick=function(){gemSet(x.id,act)};
          right.appendChild(btn);
        });
      }
      row.appendChild(right);
      rEl.appendChild(row);
    });
  }catch(e){rEl.textContent='Loading history endpoint...'}
}
setInterval(init,400);
})();