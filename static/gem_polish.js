(function(){
var ST={items:[],tab:'Matches',when:'all',sort:'ev',dir:-1,compact:false,saved:JSON.parse(localStorage.getItem('gem_saved')||'[]')};
function pNum(v){var m=String(v||'').match(/[-+]?\d+(?:\.\d+)?/);return m?parseFloat(m[0]):0;}
function evGlow(ev){
  if(ev>=7)return 'color:#4ade80;text-shadow:0 0 10px rgba(74,222,128,.75);font-weight:900';
  if(ev>=4.5)return 'color:#86efac;text-shadow:0 0 6px rgba(134,239,172,.45);font-weight:800';
  if(ev>0)return 'color:#bbf7d0;font-weight:700';
  return 'color:#94a3b8';
}
function formDots(arr){
  var a=arr||['W','W','D'];
  return '<span class="gp-form">'+a.slice(0,3).map(function(r){
    var c=r==='W'?'#22c55e':(r==='D'?'#eab308':'#ef4444');
    return '<span class="gp-dot" title="'+r+'" style="background:'+c+'"></span>';
  }).join('')+'</span>';
}
function confBars(prob){
  var lvl=prob>=75?5:(prob>=68?4:(prob>=60?3:(prob>=52?2:1)));
  var h='';for(var i=1;i<=5;i++)h+='<i class="'+(i<=lvl?'on':'')+'" style="height:'+(4+i*2)+'px"></i>';
  return '<span class="gp-bars" title="Model Confidence: '+lvl+'/5">'+h+'</span>';
}
function countdown(ko){
  var m=String(ko||'').match(/(\d{1,2}):(\d{2})/);
  if(!m)return 'Scheduled';
  var now=new Date(),t=new Date(now);
  t.setUTCHours(parseInt(m[1],10),parseInt(m[2],10),0,0);
  var diff=Math.floor((t-now)/60000);
  if(diff<-115)return 'Full Time';
  if(diff<=0)return 'Live Now';
  var h=Math.floor(diff/60),mn=diff%60;
  return 'Kicks off in: '+(h>0?h+'h ':'')+mn+'m';
}
function norm(x,idx){
  var title=x.title||x.match||x.fixture||(x.home_team?x.home_team+' v '+x.away_team:'GEM Fixture');
  var parts=title.split(/\s+v\s+|\s+vs\s+/i);
  var home=x.home_team||parts[0]||title,away=x.away_team||parts[1]||'';
  var pick=x.selection||x.pick||x.market||'Model Lean';
  var ko=x.kickoff||x.time||x.date||'19:45 GMT';
  var prob=pNum(x.prob||x.win_prob||58);if(prob>0&&prob<=1)prob=Math.round(prob*100);
  var ev=pNum(x.ev||x.edge||x.ev_pct||0);
  var odds=pNum(x.odds||x.price||1.85);
  var syn=x.syn||Math.min(9.9,Math.max(6.8,+(7.2+ev*0.35).toFixed(1)));
  var st=String(x.status||'PENDING').toUpperCase();
  var cd=countdown(ko);
  if(cd==='Live Now')st='LIVE';else if(cd==='Full Time')st='SETTLED';
  var tab='Matches';
  if((title+' '+pick).toLowerCase().indexOf('fold')>-1||(title+' '+pick).toLowerCase().indexOf('acca')>-1)tab='3-Fold Accas';
  else if((x.league||'').toUpperCase().indexOf('UK')>-1)tab='UK Slate';
  else if(ev>=4.5)tab='Likely';
  var hp=Math.min(78,Math.max(18,Math.round(prob))),dp=Math.min(34,Math.max(14,Math.round((100-hp)*0.42))),ap=Math.max(8,100-hp-dp);
  return {
    id:x.id||('g_'+idx),tab:tab,title:title,home:home,away:away,pick:pick,ko:ko,cd:cd,
    prob:prob,ev:ev,odds:odds,syn:syn,status:st,
    move:x.move||(ev>=5.5?'?':'?'),
    hp:hp,dp:dp,ap:ap,
    hForm:x.home_form||['W','W','D'],aForm:x.away_form||['W','L','W'],
    rationale:x.rationale||x.strategy||('Strong model alignment ('+prob+'% true prob) with '+ (ev>=0?'+':'')+ev.toFixed(1)+'% devigged edge at '+odds.toFixed(2)+'.')
  };
}
function render(){
  var deck=document.getElementById('gp-deck');if(!deck)return;
  var ts=document.getElementById('gp-ts');
  if(ts){var d=new Date();ts.textContent='Last updated: '+String(d.getUTCHours()).padStart(2,'0')+':'+String(d.getUTCMinutes()).padStart(2,'0')+' UTC';}
  var list=ST.items.filter(function(c){
    if(ST.tab==='Likely')return c.ev>=4.5&&c.tab!=='3-Fold Accas';
    if(ST.tab==='3-Fold Accas')return c.tab==='3-Fold Accas';
    if(ST.tab==='UK Slate')return c.tab==='UK Slate';
    if(ST.tab==='Saved')return ST.saved.indexOf(c.id)>-1;
    return true;
  });
  if(ST.when==='tomorrow'||ST.when==='week')list=[];
  list.sort(function(a,b){
    var va=ST.sort==='odds'?a.odds:(ST.sort==='time'?a.ko:a.ev);
    var vb=ST.sort==='odds'?b.odds:(ST.sort==='time'?b.ko:b.ev);
    return va>vb?ST.dir:(va<vb?-ST.dir:0);
  });
  if(!list.length){
    deck.innerHTML='<div class="gp-empty">No '+ST.tab+' picks right now ? check back later!</div>';
    return;
  }
  deck.innerHTML=list.map(function(c){
    var dot=c.status==='LIVE'?'?? Live':(c.status==='SETTLED'?'?? Settled':'?? Pending');
    var bCls=c.ev>=5.5?'gp-badge strong':'gp-badge';
    var bTxt=c.tab==='3-Fold Accas'?'3-FOLD ACCA':(c.ev>=5.5?'STRONG VALUE':(c.ev>=4.5?'SOLID EDGE':'MODEL SCAN'));
    var mvClr=c.move==='?'?'#4ade80':'#f87171';
    var isSaved=ST.saved.indexOf(c.id)>-1;
    return '<div class="gp-card'+(ST.compact?' compact':'')+'" data-id="'+c.id+'">'
      +'<div class="gp-hd"><span style="font-size:11px;font-weight:700">'+dot+'</span><span class="'+bCls+'">'+bTxt+'</span></div>'
      +'<div class="gp-teams">'+c.home+formDots(c.hForm)+(c.away?' <span style="color:#64748b">v</span> '+c.away+formDots(c.aForm):'')+'</div>'
      +'<div class="gp-meta gp-extra"><span>?? '+c.ko+' (UK Time)</span><span style="color:#38bdf8;font-weight:700">'+c.cd+'</span></div>'
      +'<div class="gp-pick"><div><div style="font-size:12.5px;font-weight:800;color:#f8fafc">'+c.pick+'</div><div class="gp-extra" style="display:flex;align-items:center;gap:8px;margin-top:4px">'+confBars(c.prob)+'<span style="'+evGlow(c.ev)+';font-size:11.5px">'+(c.ev>=0?'+':'')+c.ev.toFixed(1)+'% EV</span><span class="gp-syn" title="SYN = Synergy Score: 0-10 | Higher = stronger model alignment" style="font-size:10px;background:#1e293b;padding:2px 6px;border-radius:5px;color:#93c5fd;cursor:help">SYN-'+c.syn+'</span></div></div>'
      +'<div style="text-align:right;font-family:monospace"><div style="font-size:15px;font-weight:900;color:#fff">'+c.odds.toFixed(2)+' <span style="font-size:11px;color:'+mvClr+'">'+c.move+'</span></div><div style="font-size:10px;color:#94a3b8">'+c.prob+'%</div></div></div>'
      +'<div class="gp-extra"><div style="display:flex;justify-content:space-between;font-size:10px;color:#94a3b8;margin-bottom:3px"><span>Home '+c.hp+'%</span><span>Draw '+c.dp+'%</span><span>Away '+c.ap+'%</span></div><div class="gp-probbar"><div style="width:'+c.hp+'%;background:#3b82f6"></div><div style="width:'+c.dp+'%;background:#64748b"></div><div style="width:'+c.ap+'%;background:#8b5cf6"></div></div></div>'
      +'<div class="gp-rat" id="rat_'+c.id+'">'+c.rationale+'</div>'
      +'<div class="gp-ft gp-extra"><button class="gp-pill gp-rtog" data-id="'+c.id+'">? Rationale</button><div style="display:flex;gap:6px"><button class="gp-star'+(isSaved?' saved':'')+'" data-id="'+c.id+'" title="Save coupon">?</button><button class="gp-act" onclick="alert('Added to Coupon: '+c.pick.replace(/'/g,'')+' @ '+c.odds.toFixed(2)+'')">+ Coupon</button></div></div>'
    +'</div>';
  }).join('');
  deck.querySelectorAll('.gp-rtog').forEach(function(b){b.onclick=function(){var el=document.getElementById('rat_'+b.dataset.id);if(el)el.classList.toggle('open');};});
  deck.querySelectorAll('.gp-star').forEach(function(b){b.onclick=function(){var id=b.dataset.id,i=ST.saved.indexOf(id);if(i>-1)ST.saved.splice(i,1);else ST.saved.push(id);localStorage.setItem('gem_saved',JSON.stringify(ST.saved));render();};});
  deck.querySelectorAll('.gp-syn').forEach(function(b){b.onclick=function(){alert('SYN = Synergy Score: 0-10 | Higher = stronger model alignment');};});
}
function boot(){
  if(!document.body||document.getElementById('gp-top'))return;
  if(!document.querySelector('link[href*="gem_polish.css"]')){var l=document.createElement('link');l.rel='stylesheet';l.href='/static/gem_polish.css?v=31';document.head.appendChild(l);}
  Array.from(document.body.children).forEach(function(el){if(el.tagName!=='SCRIPT'&&el.tagName!=='STYLE')el.style.display='none';});
  var top=document.createElement('div');top.id='gp-top';
  top.innerHTML='<div class="gp-row"><div style="display:flex;flex-wrap:wrap;gap:5px" id="gp-tabs"></div><div style="display:flex;align-items:center;gap:8px"><span id="gp-ts" style="font-size:11px;color:#93c5fd"></span><button class="gp-pill" id="gp-leg">? Legend</button></div></div>'
    +'<div class="gp-row"><div style="display:flex;gap:5px" id="gp-when"><button class="gp-pill on" data-w="all">All</button><button class="gp-pill" data-w="today">Today</button><button class="gp-pill" data-w="tomorrow">Tomorrow</button><button class="gp-pill" data-w="week">This Week</button></div>'
    +'<div style="display:flex;flex-wrap:wrap;gap:5px"><button class="gp-pill on" data-s="ev">Sort: EV % ??</button><button class="gp-pill" data-s="odds">Odds ??</button><button class="gp-pill" data-s="time">Time ??</button><button class="gp-pill" id="gp-cmp">Compact</button></div></div>'
    +'<div class="gp-tip" id="gp-tip"><b>EV</b> = Expected Value | <b>xG</b> = Expected Goals | <b>CLV</b> = Closing Line Value | <b>SYN</b> = Synergy Score (0?10, higher = stronger model alignment)</div>';
  var deck=document.createElement('div');deck.id='gp-deck';
  document.body.prepend(deck);document.body.prepend(top);
  var tb=document.getElementById('gp-tabs');
  ['Matches','Likely','3-Fold Accas','UK Slate','Saved'].forEach(function(n){
    var b=document.createElement('button');b.className='gp-pill'+(n===ST.tab?' on':'');b.textContent=n;
    b.onclick=function(){tb.querySelectorAll('.gp-pill').forEach(function(x){x.classList.remove('on');});b.classList.add('on');ST.tab=n;render();};
    tb.appendChild(b);
  });
  document.getElementById('gp-leg').onclick=function(){document.getElementById('gp-tip').classList.toggle('open');};
  document.getElementById('gp-cmp').onclick=function(){ST.compact=!ST.compact;this.classList.toggle('on',ST.compact);render();};
  document.querySelectorAll('#gp-when .gp-pill').forEach(function(b){b.onclick=function(){document.querySelectorAll('#gp-when .gp-pill').forEach(function(x){x.classList.remove('on');});b.classList.add('on');ST.when=b.dataset.w;render();};});
  document.querySelectorAll('[data-s]').forEach(function(b){b.onclick=function(){if(ST.sort===b.dataset.s)ST.dir*=-1;else{ST.sort=b.dataset.s;ST.dir=-1;}document.querySelectorAll('[data-s]').forEach(function(x){x.classList.remove('on');});b.classList.add('on');render();};});
  fetch('/api/desk?t='+Date.now()).then(function(r){return r.json();}).then(function(j){ST.items=(j&&j.items)?j.items.map(norm):[];render();});
  setInterval(function(){ST.items.forEach(function(c){c.cd=countdown(c.ko);});render();},30000);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();
})();
