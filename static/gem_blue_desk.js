(function(){
function init(){
  if(!document.body||document.getElementById('gem-bar'))return;
  var b=document.createElement('div');b.id='gem-bar';
  b.innerHTML=[
    '<button class="gem-c on">Matches</button>',
    '<button class="gem-c">Today Picks</button>',
    '<button class="gem-c">Likely</button>',
    '<button class="gem-c">AI Predictions</button>',
    '<button class="gem-c">Value (+EV)</button>',
    '<button class="gem-c">3-Fold Accas</button>',
    '<button class="gem-c" id="gbh">History</button>'
  ].join('');

  var s=document.createElement('div');s.id='gem-spot';
  s.innerHTML=[
    '<div style="font-size:11px;color:#94a3b8;font-family:monospace">GEM V15 BLUE DESK &middot; LIVE TELEMETRY &amp; SETTLEMENT TRACKER</div>',
    '<div class="gem-days">',
    '<button class="gem-d on">Today (Sun 15)</button>',
    '<button class="gem-d">Tomorrow (Mon 16)</button>',
    '<button class="gem-d">Tue 17</button>',
    '<button class="gem-d">Wed 18</button>',
    '</div>',
    '<div class="gem-grid">',
    '<div class="gem-box">',
    '<div style="display:flex;justify-content:space-between"><span style="font-size:11px;font-weight:800;color:#38bdf8">PICK OF THE DAY</span><span style="font-size:20px;font-weight:900;color:#60a5fa;font-family:monospace">82%</span></div>',
    '<div style="font-weight:800;margin-top:4px">Granada CF v UD Las Palmas</div>',
    '<div style="font-size:12px;color:#94a3b8">Sun 15 Nov &middot; 15:15 GMT &middot; Full time result: Granada</div>',
    '<div style="font-size:11px;color:#94a3b8;font-family:monospace;margin-top:3px">Best 1.95-2.15 &middot; fair 1.85 &middot; EV +8.8% &middot; Kelly 2.2%</div>',
    '<div style="text-align:right;margin-top:8px"><button class="gem-d js-open-hist">See pick history</button></div>',
    '</div>',
    '<div class="gem-box" style="border-left-color:#38bdf8">',
    '<div style="display:flex;justify-content:space-between"><span style="font-size:11px;font-weight:800;color:#38bdf8">ENHANCED PICK OF THE DAY</span><span style="font-size:20px;font-weight:900;color:#60a5fa;font-family:monospace">84%</span></div>',
    '<div style="font-weight:800;margin-top:4px">Spain v England</div>',
    '<div style="font-size:12px;color:#94a3b8">Sun 15 Nov &middot; 19:45 GMT &middot; Spain 1X &amp; Over 1.5 Goals</div>',
    '<div style="font-size:11px;color:#94a3b8;font-family:monospace;margin-top:3px">Best 1.45 (1X+O1.5) / 1.33 DNB &middot; EV +5.6% &middot; Kelly 2.5%</div>',
    '<div style="text-align:right;margin-top:8px"><button class="gem-d js-open-hist">See Enhanced history</button></div>',
    '</div>',
    '</div>'
  ].join('');

  var h=document.createElement('div');h.id='gem-hd';
  h.innerHTML=[
    '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">',
    '<b style="color:#60a5fa;font-family:monospace">PREDICTION &amp; SLIP SETTLEMENT HISTORY</b>',
    '<button class="gem-d" id="gch">Close</button>',
    '</div>',
    '<div id="ghs" style="font-family:monospace;font-size:12px;color:#93c5fd;margin-bottom:8px"></div>',
    '<div id="ghr" style="font-size:12px">Loading...</div>'
  ].join('');

  document.body.prepend(h);
  document.body.prepend(s);
  document.body.prepend(b);

  document.getElementById('gch').onclick=function(){h.classList.remove('open')};
  var toggleHist=async function(){
    h.classList.toggle('open');
    if(h.classList.contains('open'))await loadH();
  };
  document.getElementById('gbh').onclick=toggleHist;
  s.querySelectorAll('.js-open-hist').forEach(function(btn){btn.onclick=toggleHist});
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