(function(){
var MIN_EV=4.5,ST={tab:'Matches',items:[]};
function pEv(v){var m=String(v||'').match(/[-+]?\d+(?:\.\d+)?/);return m?parseFloat(m[0]):0;}
function norm(x){
  var t=x.title||x.match||x.fixture||(x.home_team?x.home_team+' v '+x.away_team:'GEM Fixture');
  var pk=x.selection||x.pick||x.market||x.desc||'Model Lean';
  var tm=x.kickoff||x.date||x.time||x.league||('Source: '+(x._src||'QUANT'));
  var n=parseFloat(String(x.prob||x.win_prob||x.model_prob||'58').replace('%',''));
  n=!isNaN(n)?((n>0&&n<=1)?Math.round(n*100):Math.round(n)):58;
  var evN=pEv(x.ev||x.edge||x.ev_pct||0),st=x.strategy||x.model||'NB-DC + Elo + LogitPool';
  var bl=(t+' '+pk+' '+st).toLowerCase(),tb='Matches';
  if(bl.indexOf('fold')>-1||bl.indexOf('acca')>-1)tb='3-Fold Accas';
  else if(evN>=MIN_EV)tb='Likely';
  var isTop=evN>=MIN_EV;
  return {tab:tb,title:t,time:tm,pick:pk,prob:n+'%',odds:x.odds||x.price||'--',ev:(evN>=0?'+':'')+evN.toFixed(1)+'%',evNum:evN,kelly:x.kelly||(isTop?'1.5%':'0.0%'),isTop:isTop,tag:isTop?('VERIFIED EDGE ? +'+evN.toFixed(1)+'% EV'):('GLOBAL SCAN ? '+(evN>=0?'+':'')+evN.toFixed(1)+'% EV'),strat:st};
}
function draw(){
  var d=document.getElementById('gem-deck');if(!d)return;
  var list=ST.items.filter(function(c){
    if(ST.tab==='Likely')return c.evNum>=MIN_EV&&c.tab!=='3-Fold Accas';
    if(ST.tab==='3-Fold Accas')return c.tab==='3-Fold Accas'&&c.evNum>=MIN_EV;
    if(ST.tab==='Today Picks')return c.evNum>=2.0;
    return true;
  });
  if(!list.length)list=[{title:'No Fixtures in This Filter Yet',time:'Run your live global odds sync to populate upcoming fixtures',pick:'Switch to "Matches" to view all scanned games',prob:'--',odds:'--',ev:'--',evNum:0,kelly:'--',isTop:false,tag:'AWAITING LIVE SLATE',strat:'NB-DC + Elo + LogitPool'}];
  list.sort(function(a,b){return (b.evNum||0)-(a.evNum||0);});
  d.innerHTML=list.map(function(c){
    var tc=c.isTop?'#facc15':'#38bdf8';
    return '<div class="gem-box" style="margin-bottom:10px;border-color:'+(c.isTop?'#facc15':'#1e3a8a')+'"><div style="display:flex;justify-content:space-between;align-items:center"><span style="font-size:11px;font-weight:800;color:'+tc+'">'+c.tag+'</span><span style="font-size:13px;font-weight:900;color:#fff;font-family:monospace;background:#1e429f;border:1px solid #60a5fa;padding:2px 8px;border-radius:999px">'+c.prob+' LIKELY</span></div><div style="font-weight:800;font-size:15px;color:#fff;margin-top:5px">'+c.title+'</div><div style="font-size:12px;color:#94a3b8;margin-top:2px">'+c.time+'</div><div style="font-size:13px;font-weight:700;color:#e2e8f0;margin-top:6px">'+c.pick+'</div><div style="font-size:11px;color:#34d399;font-family:monospace;margin-top:4px">Model: '+c.strat+'</div><div style="font-size:11px;color:#93c5fd;font-family:monospace;margin-top:3px">Odds: '+c.odds+' &middot; EV: '+c.ev+' &middot; Kelly: '+c.kelly+'</div></div>';
  }).join('');
}
async function loadH(){
  var rE=document.getElementById('ghr'),sE=document.getElementById('ghs');
  try{var r=await fetch('/api/history'),j=await r.json(),it=j.items||[],w=0,l=0,o=0;it.forEach(function(x){var s=String(x.status||'OPEN').toUpperCase();if(s==='WON')w++;else if(s==='LOST')l++;else o++;});sE.textContent='WIN RATE: '+((w+l)?((w/(w+l))*100).toFixed(1)+'%':'Pending')+' | WON: '+w+' | LOST: '+l+' | OPEN: '+o;rE.innerHTML=it.length?'':'No records logged yet.';it.forEach(function(x){var s=String(x.status||'OPEN').toUpperCase(),row=document.createElement('div');row.className='gem-hr '+s;row.innerHTML='<div><b>['+(x._source||'LEDGER')+'] '+(x.title||x.match||'Pick')+'</b></div>';var rt=document.createElement('div');rt.style.cssText='display:flex;gap:6px;align-items:center';rt.innerHTML='<b>'+s+'</b>';if(x.id)['WON','LOST'].forEach(function(a){var b=document.createElement('button');b.className='gem-d';b.textContent=a;b.onclick=async function(){await fetch('/api/history',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:x.id,status:a})});loadH();};rt.appendChild(b);});row.appendChild(rt);rE.appendChild(row);});}catch(e){rE.textContent='Loading...';}
}
function init(){
  if(!document.body||document.getElementById('gem-bar'))return;
  var b=document.createElement('div');b.id='gem-bar';
  ['Matches','Today Picks','Likely','AI Predictions','3-Fold Accas','History'].forEach(function(n){var btn=document.createElement('button');btn.className='gem-c'+(n===ST.tab?' on':'');btn.textContent=n;btn.onclick=async function(){b.querySelectorAll('.gem-c').forEach(function(x){x.classList.remove('on');});btn.classList.add('on');var h=document.getElementById('gem-hd');if(n==='History'){h.classList.add('open');await loadH();}else{h.classList.remove('open');ST.tab=n;draw();}};b.appendChild(btn);});
  var s=document.createElement('div');s.id='gem-spot';s.innerHTML='<div style="font-size:11px;color:#facc15;font-family:monospace">GEM V15 QUANT DESK &middot; GLOBAL SLATE + VERIFIED >= +4.5% EV</div><div id="gem-deck" class="gem-grid" style="margin-top:8px"></div>';
  var h=document.createElement('div');h.id='gem-hd';h.innerHTML='<div style="display:flex;justify-content:space-between;margin-bottom:8px"><b style="color:#facc15">SETTLEMENT HISTORY</b><button class="gem-d" id="gch">Close</button></div><div id="ghs" style="font-size:12px;color:#93c5fd;margin-bottom:6px"></div><div id="ghr" style="font-size:12px"></div>';
  document.body.prepend(h);document.body.prepend(s);document.body.prepend(b);
  document.getElementById('gch').onclick=function(){h.classList.remove('open');};draw();
  fetch('/api/desk?t='+Date.now()).then(function(r){return r.json();}).then(function(j){ST.items=(j&&j.items)?j.items.map(norm):[];draw();}).catch(function(){draw();});
}
setInterval(init,400);
})();
