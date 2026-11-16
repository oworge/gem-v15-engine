(function(){
var MIN_EV=4.5,ST={tab:'Matches',q:'',items:[]};
function pEv(v){var m=String(v||'').match(/[-+]?\d+(?:\.\d+)?/);return m?parseFloat(m[0]):0;}
function injectCSS(){
  if(document.getElementById('gem-tidy-css'))return;
  var st=document.createElement('style');st.id='gem-tidy-css';
  st.textContent=[
    '#gem-bar{display:flex;flex-wrap:wrap;gap:6px;align-items:center;padding:10px 12px;background:#071124;border-bottom:1px solid #1e3a8a;position:sticky;top:0;z-index:9999}',
    '.gem-c{background:#0f172a;color:#cbd5e1;border:1px solid #1e3a8a;padding:6px 12px;border-radius:8px;font-size:12px;font-weight:700;cursor:pointer;transition:.15s}',
    '.gem-c.on{background:#1d4ed8;color:#fff;border-color:#60a5fa;box-shadow:0 0 10px rgba(59,130,246,.35)}',
    '#gem-q{margin-left:auto;background:#0f172a;color:#f8fafc;border:1px solid #334155;border-radius:8px;padding:6px 10px;font-size:12px;min-width:170px}',
    '#gem-spot{padding:12px;background:#040b18;min-height:100vh;font-family:system-ui,-apple-system,sans-serif}',
    '#gem-kpi{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px;margin-bottom:12px}',
    '.gem-kp{background:#0b1730;border:1px solid #1e3a8a;border-radius:10px;padding:8px 10px}',
    '.gem-kp b{display:block;font-size:15px;color:#f8fafc;font-family:monospace;margin-top:2px}',
    '.gem-kp span{font-size:10px;color:#93c5fd;text-transform:uppercase;letter-spacing:.5px}',
    '#gem-deck{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:10px}',
    '.gem-box{background:linear-gradient(180deg,#0c1933 0%,#081226 100%);border:1px solid #1e3a8a;border-radius:12px;padding:12px;display:flex;flex-direction:column;justify-content:space-between}',
    '.gem-box.top{border-color:#facc15;box-shadow:0 0 14px rgba(250,204,21,.12)}',
    '.gem-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:5px;margin-top:10px;background:#050d1d;border:1px solid #172554;border-radius:8px;padding:6px}',
    '.gem-st{text-align:center}',
    '.gem-st small{display:block;font-size:9px;color:#64748b;text-transform:uppercase}',
    '.gem-st strong{font-size:12px;color:#e2e8f0;font-family:monospace}'
  ].join('');
  document.head.appendChild(st);
}
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
  return {tab:tb,title:t,time:tm,pick:pk,prob:n+'%',odds:x.odds||x.price||'--',ev:(evN>=0?'+':'')+evN.toFixed(1)+'%',evNum:evN,kelly:x.kelly||(isTop?'1.45%':'0.00%'),isTop:isTop,tag:isTop?('VERIFIED +EV ? +'+evN.toFixed(1)+'%'):('GLOBAL SCAN ? '+(evN>=0?'+':'')+evN.toFixed(1)+'%'),strat:st};
}
function draw(){
  var d=document.getElementById('gem-deck'),k=document.getElementById('gem-kpi');if(!d)return;
  var topC=ST.items.filter(function(c){return c.isTop&&c.tab!=='3-Fold Accas';}).length;
  var accC=ST.items.filter(function(c){return c.tab==='3-Fold Accas';}).length;
  if(k){
    k.innerHTML=[
      '<div class="gem-kp"><span>Global Fixtures</span><b>'+ST.items.length+' Games</b></div>',
      '<div class="gem-kp"><span>Verified >= +4.5% EV</span><b style="color:#facc15">'+topC+' Edges</b></div>',
      '<div class="gem-kp"><span>3-Fold Acca Slips</span><b style="color:#34d399">'+accC+' Active</b></div>',
      '<div class="gem-kp"><span>Engine Core</span><b style="color:#60a5fa">NB-DC ? Logit</b></div>'
    ].join('');
  }
  var q=ST.q.trim().toLowerCase();
  var list=ST.items.filter(function(c){
    if(q&&(c.title+' '+c.pick+' '+c.time).toLowerCase().indexOf(q)===-1)return false;
    if(ST.tab==='Likely')return c.evNum>=MIN_EV&&c.tab!=='3-Fold Accas';
    if(ST.tab==='3-Fold Accas')return c.tab==='3-Fold Accas';
    if(ST.tab==='Today Picks')return c.evNum>=2.0;
    return true;
  });
  if(!list.length)list=[{title:'No Matching Fixtures',time:'Clear search filter or switch to "Matches" tab',pick:'All scanned games remain preserved in Matches',prob:'--',odds:'--',ev:'--',evNum:0,kelly:'--',isTop:false,tag:'FILTER EMPTY',strat:'NB-DC + Elo + LogitPool'}];
  list.sort(function(a,b){return (b.evNum||0)-(a.evNum||0);});
  d.innerHTML=list.map(function(c){
    var tc=c.isTop?'#facc15':'#38bdf8';
    return '<div class="gem-box'+(c.isTop?' top':'')+'">'
      +'<div>'
        +'<div style="display:flex;justify-content:space-between;align-items:center;gap:6px">'
          +'<span style="font-size:10px;font-weight:800;letter-spacing:.4px;color:'+tc+'">'+c.tag+'</span>'
          +'<span style="font-size:11px;font-weight:800;color:#fff;font-family:monospace;background:#1e3a8a;border:1px solid #3b82f6;padding:2px 7px;border-radius:999px">'+c.prob+'</span>'
        +'</div>'
        +'<div style="font-weight:800;font-size:14px;color:#f8fafc;margin-top:6px;line-height:1.25">'+c.title+'</div>'
        +'<div style="font-size:11px;color:#94a3b8;margin-top:2px">'+c.time+'</div>'
        +'<div style="font-size:12.5px;font-weight:700;color:#e2e8f0;margin-top:7px;padding:5px 8px;background:#071226;border-left:3px solid '+tc+';border-radius:4px">'+c.pick+'</div>'
      +'</div>'
      +'<div>'
        +'<div style="font-size:10.5px;color:#34d399;font-family:monospace;margin-top:7px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">'+c.strat+'</div>'
        +'<div class="gem-stats">'
          +'<div class="gem-st"><small>Odds</small><strong>'+c.odds+'</strong></div>'
          +'<div class="gem-st"><small>Prob</small><strong>'+c.prob+'</strong></div>'
          +'<div class="gem-st"><small>Edge</small><strong style="color:'+tc+'">'+c.ev+'</strong></div>'
          +'<div class="gem-st"><small>Kelly</small><strong>'+c.kelly+'</strong></div>'
        +'</div>'
      +'</div>'
    +'</div>';
  }).join('');
}
async function loadH(){
  var rE=document.getElementById('ghr'),sE=document.getElementById('ghs');
  try{var r=await fetch('/api/history'),j=await r.json(),it=j.items||[],w=0,l=0,o=0;it.forEach(function(x){var s=String(x.status||'OPEN').toUpperCase();if(s==='WON')w++;else if(s==='LOST')l++;else o++;});sE.textContent='WIN RATE: '+((w+l)?((w/(w+l))*100).toFixed(1)+'%':'Pending')+' | WON: '+w+' | LOST: '+l+' | OPEN: '+o;rE.innerHTML=it.length?'':'No records logged yet.';it.forEach(function(x){var s=String(x.status||'OPEN').toUpperCase(),row=document.createElement('div');row.className='gem-hr '+s;row.innerHTML='<div><b>['+(x._source||'LEDGER')+'] '+(x.title||x.match||'Pick')+'</b></div>';var rt=document.createElement('div');rt.style.cssText='display:flex;gap:6px;align-items:center';rt.innerHTML='<b>'+s+'</b>';if(x.id)['WON','LOST'].forEach(function(a){var b=document.createElement('button');b.className='gem-d';b.textContent=a;b.onclick=async function(){await fetch('/api/history',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:x.id,status:a})});loadH();};rt.appendChild(b);});row.appendChild(rt);rE.appendChild(row);});}catch(e){rE.textContent='Loading...';}
}
function init(){
  if(!document.body||document.getElementById('gem-bar'))return;
  injectCSS();
  var b=document.createElement('div');b.id='gem-bar';
  ['Matches','Today Picks','Likely','AI Predictions','3-Fold Accas','History'].forEach(function(n){var btn=document.createElement('button');btn.className='gem-c'+(n===ST.tab?' on':'');btn.textContent=n;btn.onclick=async function(){b.querySelectorAll('.gem-c').forEach(function(x){x.classList.remove('on');});btn.classList.add('on');var h=document.getElementById('gem-hd');if(n==='History'){h.classList.add('open');await loadH();}else{h.classList.remove('open');ST.tab=n;draw();}};b.appendChild(btn);});
  var qi=document.createElement('input');qi.id='gem-q';qi.placeholder='Filter team or market...';qi.oninput=function(){ST.q=qi.value;draw();};b.appendChild(qi);
  var s=document.createElement('div');s.id='gem-spot';s.innerHTML='<div id="gem-kpi"></div><div id="gem-deck"></div>';
  var h=document.createElement('div');h.id='gem-hd';h.innerHTML='<div style="display:flex;justify-content:space-between;margin-bottom:8px"><b style="color:#facc15">SETTLEMENT HISTORY</b><button class="gem-d" id="gch">Close</button></div><div id="ghs" style="font-size:12px;color:#93c5fd;margin-bottom:6px"></div><div id="ghr" style="font-size:12px"></div>';
  document.body.prepend(h);document.body.prepend(s);document.body.prepend(b);
  document.getElementById('gch').onclick=function(){h.classList.remove('open');};draw();
  fetch('/api/desk?t='+Date.now()).then(function(r){return r.json();}).then(function(j){ST.items=(j&&j.items)?j.items.map(norm):[];draw();}).catch(function(){draw();});
}
setInterval(init,400);
})();
