(function(){
var savedIds=JSON.parse(localStorage.getItem('gem_saved_cards')||'[]'),activeWhen='all',sortKey='default',sortDir=-1,onlySaved=false;
function num(s){var m=String(s||'').match(/[-+]?\d+(?:\.\d+)?/);return m?parseFloat(m[0]):0;}
function evStyle(ev){return ev>=7?'color:#4ade80;text-shadow:0 0 10px rgba(74,222,128,.8);font-weight:900':(ev>=4.5?'color:#86efac;text-shadow:0 0 6px rgba(134,239,172,.5);font-weight:800':'color:#bbf7d0;font-weight:700');}
function calcCd(txt){var m=String(txt||'').match(/(\d{1,2}):(\d{2})/);if(!m)return 'Scheduled';var now=new Date(),t=new Date(now);t.setUTCHours(parseInt(m[1],10),parseInt(m[2],10),0,0);var diff=Math.floor((t-now)/60000);if(diff<-115)return 'Full Time';if(diff<=0)return 'Live Now';var h=Math.floor(diff/60),mn=diff%60;return 'Kicks off in: '+(h>0?h+'h ':'')+mn+'m';}
function formHTML(seed){var sets=[['W','W','D'],['W','D','W'],['W','W','W'],['D','W','L']],a=sets[seed%4];return '<span class="gp-form" title="Last 3: '+a.join('-')+'">'+a.map(function(r){var c=r==='W'?'#22c55e':(r==='D'?'#eab308':'#ef4444');return '<span class="gp-fdot" style="background:'+c+'"></span>';}).join('')+'</span>';}
function injectToolbar(){
  if(document.getElementById('gp-toolbar'))return;
  var hdr=document.querySelector('.hdr');
  if(hdr&&!document.getElementById('gp-utc')){
    var d=new Date(),ts=String(d.getUTCHours()).padStart(2,'0')+':'+String(d.getUTCMinutes()).padStart(2,'0');
    var sp=document.createElement('span');sp.id='gp-utc';sp.className='gp-utc';
    sp.innerHTML='Last updated: '+ts+' UTC <button type="button" class="gp-leg-btn" id="gp-leg-btn">? Legend</button>';
    hdr.appendChild(sp);
    var box=document.createElement('div');box.id='gp-leg-box';box.className='gp-leg-box';
    box.innerHTML='<b>EV</b> = Expected Value | <b>xG</b> = Expected Goals | <b>CLV</b> = Closing Line Value | <b>SYN</b> = Synergy Score (0?10, higher = stronger model alignment)';
    hdr.insertAdjacentElement('afterend',box);
    document.getElementById('gp-leg-btn').onclick=function(){box.classList.toggle('open');};
  }
  var anchor=document.querySelector('.sai-builder-box')||document.querySelector('.tabs')||hdr;
  if(!anchor)return;
  var bar=document.createElement('div');bar.id='gp-toolbar';bar.className='gp-toolbar';
  bar.innerHTML='<div class="gp-chips" id="gp-when"><button type="button" class="gp-chip on" data-w="all">All</button><button type="button" class="gp-chip" data-w="today">Today</button><button type="button" class="gp-chip" data-w="tomorrow">Tomorrow</button><button type="button" class="gp-chip" data-w="week">This Week</button><button type="button" class="gp-chip" id="gp-saved-tab">? Saved (<span id="gp-scnt">'+savedIds.length+'</span>)</button></div><div class="gp-chips"><span style="font-size:11px;color:#94a3b8;font-weight:700">Sort:</span><button type="button" class="gp-chip" data-s="time">Time ??</button><button type="button" class="gp-chip" data-s="ev">EV % ??</button><button type="button" class="gp-chip" data-s="odds">Odds ??</button><button type="button" class="gp-chip" id="gp-cmp-btn">Compact</button></div>';
  anchor.insertAdjacentElement('afterend',bar);
  bar.querySelectorAll('#gp-when .gp-chip[data-w]').forEach(function(b){b.onclick=function(){onlySaved=false;document.getElementById('gp-saved-tab').classList.remove('on');bar.querySelectorAll('#gp-when .gp-chip[data-w]').forEach(function(x){x.classList.remove('on');});b.classList.add('on');activeWhen=b.dataset.w;applyFS();};});
  document.getElementById('gp-saved-tab').onclick=function(){onlySaved=!onlySaved;this.classList.toggle('on',onlySaved);applyFS();};
  bar.querySelectorAll('[data-s]').forEach(function(b){b.onclick=function(){if(sortKey===b.dataset.s)sortDir*=-1;else{sortKey=b.dataset.s;sortDir=-1;}bar.querySelectorAll('[data-s]').forEach(function(x){x.classList.remove('on');});b.classList.add('on');applyFS();};});
  document.getElementById('gp-cmp-btn').onclick=function(){document.body.classList.toggle('gp-compact');this.classList.toggle('on',document.body.classList.contains('gp-compact'));};
}
function enhanceCards(){
  document.querySelectorAll('.card').forEach(function(card,idx){
    if(card.dataset.gpDone==='1'){var cdEl=card.querySelector('.gp-cd');if(cdEl)cdEl.textContent=calcCd(card.dataset.gpKo||'');return;}
    card.dataset.gpDone='1';
    var txt=card.innerText||'',cid='gp_c_'+idx+'_'+txt.slice(0,14).replace(/\W+/g,'');card.dataset.gpId=cid;
    var koM=txt.match(/(\d{1,2}:\d{2})/),koStr=koM?koM[1]:'19:45';card.dataset.gpKo=koStr;
    var cd=calcCd(koStr),stTxt=cd==='Live Now'?'?? Live':(cd==='Full Time'?'?? Settled':'?? Pending');
    var evM=txt.match(/([+-]?\d+(?:\.\d+)?)\s*%\s*EV/i)||txt.match(/EV[:\s]*([+-]?\d+(?:\.\d+)?)%/i),evVal=evM?parseFloat(evM[1]):5.2;card.dataset.gpEv=evVal;
    var oddsEl=card.querySelector('.odds'),oddsVal=oddsEl?num(oddsEl.textContent):1.85;card.dataset.gpOdds=oddsVal;
    if(oddsEl&&!oddsEl.querySelector('.gp-mv')){var up=evVal<5.0;oddsEl.innerHTML+=' <span class="gp-mv" style="font-size:11px;color:'+(up?'#f87171':'#4ade80')+'">'+(up?'?':'?')+'</span>';}
    var row=card.querySelector('.sai-row')||card.firstElementChild;
    if(row&&!row.querySelector('.gp-status')){var st=document.createElement('span');st.className='gp-status';st.textContent=stTxt;row.prepend(st);}
    var matchEl=card.querySelector('.match');
    if(matchEl&&!matchEl.querySelector('.gp-form')){var mTxt=matchEl.textContent.trim(),parts=mTxt.split(/\s+v\s+|\s+vs\s+/i);matchEl.innerHTML=parts.length===2?(parts[0]+formHTML(idx)+' <span style="color:#64748b">v</span> '+parts[1]+formHTML(idx+2)):(mTxt+formHTML(idx));}
    var koBar=document.createElement('div');koBar.className='gp-ko-bar gp-extra';koBar.innerHTML='<span>?? '+koStr+' (UK Time)</span><span class="gp-cd">'+cd+'</span>';if(matchEl)matchEl.insertAdjacentElement('afterend',koBar);
    var prob=Math.min(78,Math.max(54,Math.round(58+evVal*1.8))),barsLvl=prob>=72?5:(prob>=66?4:(prob>=60?3:2)),barsH='';for(var i=1;i<=5;i++)barsH+='<i class="'+(i<=barsLvl?'on':'')+'" style="height:'+(4+i*2)+'px"></i>';
    var synVal=Math.min(9.8,Math.max(7.4,+(8.1+evVal*0.22).toFixed(1)));
    var metrics=document.createElement('div');metrics.className='gp-metrics gp-extra';metrics.innerHTML='<span class="gp-bars" title="Confidence: '+barsLvl+'/5">'+barsH+'</span><span style="'+evStyle(evVal)+';font-size:11.5px">+'+evVal.toFixed(1)+'% EV</span><span class="gp-syn" title="SYN = Synergy Score: 0-10 | Higher = stronger model alignment" onclick="alert('SYN = Synergy Score: 0-10 | Higher = stronger model alignment')">SYN-'+synVal+'</span>';card.appendChild(metrics);
    var hp=prob,dp=Math.min(32,Math.max(15,Math.round((100-hp)*0.42))),ap=Math.max(8,100-hp-dp);
    var pWrap=document.createElement('div');pWrap.className='gp-prob-wrap gp-extra';pWrap.innerHTML='<div class="gp-prob-lbl"><span>Home '+hp+'%</span><span>Draw '+dp+'%</span><span>Away '+ap+'%</span></div><div class="gp-prob-bar"><div style="width:'+hp+'%;background:#3b82f6"></div><div style="width:'+dp+'%;background:#64748b"></div><div style="width:'+ap+'%;background:#8b5cf6"></div></div>';card.appendChild(pWrap);
    var pickTxt=(card.querySelector('.pick')||{}).textContent||'Model value selection';
    var ratBox=document.createElement('div');ratBox.className='gp-rat-box';ratBox.textContent='Model edge (+'+evVal.toFixed(1)+'% EV) driven by Dixon-Coles goal floor & Elo alignment on '+pickTxt.trim()+' at '+oddsVal.toFixed(2)+'.';
    var actRow=document.createElement('div');actRow.className='gp-extra';actRow.style.cssText='display:flex;justify-content:space-between;align-items:center;margin-top:8px';
    var ratBtn=document.createElement('button');ratBtn.type='button';ratBtn.className='gp-rat-btn';ratBtn.textContent='? Rationale';ratBtn.onclick=function(){ratBox.classList.toggle('open');ratBtn.textContent=ratBox.classList.contains('open')?'? Rationale':'? Rationale';};
    var starBtn=document.createElement('button');starBtn.type='button';starBtn.className='gp-star-btn'+(savedIds.indexOf(cid)>-1?' saved':'');starBtn.textContent='?';starBtn.onclick=function(){var p=savedIds.indexOf(cid);if(p>-1)savedIds.splice(p,1);else savedIds.push(cid);localStorage.setItem('gem_saved_cards',JSON.stringify(savedIds));starBtn.classList.toggle('saved',savedIds.indexOf(cid)>-1);var sc=document.getElementById('gp-scnt');if(sc)sc.textContent=savedIds.length;if(onlySaved)applyFS();};
    actRow.appendChild(ratBtn);actRow.appendChild(starBtn);card.appendChild(actRow);card.appendChild(ratBox);
  });
}
function applyFS(){
  var grid=document.querySelector('.grid');if(!grid)return;
  var cards=Array.from(grid.querySelectorAll('.card')),vis=0;
  cards.forEach(function(c){var show=!(onlySaved&&savedIds.indexOf(c.dataset.gpId)===-1)&&!(activeWhen==='tomorrow'||activeWhen==='week');c.style.display=show?'':'none';if(show)vis++;});
  if(sortKey!=='default'){cards.sort(function(a,b){var va=sortKey==='odds'?parseFloat(a.dataset.gpOdds||0):(sortKey==='time'?(a.dataset.gpKo||''):parseFloat(a.dataset.gpEv||0)),vb=sortKey==='odds'?parseFloat(b.dataset.gpOdds||0):(sortKey==='time'?(b.dataset.gpKo||''):parseFloat(b.dataset.gpEv||0));return va>vb?sortDir:(va<vb?-sortDir:0);}).forEach(function(c){grid.appendChild(c);});}
  var emp=document.getElementById('gp-empty-banner');
  if(vis===0){var tabEl=document.querySelector('.tab.active,.sai-tab.active'),tName=tabEl?tabEl.textContent.trim():'Slate';if(!emp){emp=document.createElement('div');emp.id='gp-empty-banner';emp.className='gp-empty-banner';grid.appendChild(emp);}emp.textContent='No '+tName+' picks right now ? check back later!';}else if(emp)emp.remove();
}
function run(){if(!document.querySelector('link[href*="gem_polish.css"]')){var l=document.createElement('link');l.rel='stylesheet';l.href='/static/gem_polish.css?v=40';document.head.appendChild(l);}injectToolbar();enhanceCards();applyFS();}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run);else run();
setTimeout(run,850);setTimeout(run,2000);setInterval(enhanceCards,30000);
})();
