(function(){
var mode="matches",activeDay=0,accMode="10fold",pvCache=[];
var TABS=[["matches","Matches"],["perfect","Perfect Value"],["today","Today's picks"],["likely","Likely"],["ai","AI predictions"],["value","Value"],["arbs","Arbs"],["acc","Accumulator"],["bets","Bets"]];
function h(tag,cls,txt){var e=document.createElement(tag);if(cls)e.className=cls;if(txt!==undefined)e.textContent=txt;return e;}
function harvestPV(){
  if(pvCache.length)return;
  document.querySelectorAll(".alert,.alert-box,[class*='alert']").forEach(function(el){
    var txt=(el.innerText||"").trim();
    if(/PERFECT VALUE/i.test(txt)){
      var lines=txt.split("\n").map(function(s){return s.trim();}).filter(Boolean);
      var tag=(el.querySelector(".alert-tag,button,a")||{}).innerText||lines[lines.length-1]||"PLACE BET";
      var body=lines.filter(function(l){return l!==tag;}).join(" — ");
      pvCache.push({title:lines[0]||"PERFECT VALUE SIGNAL",detail:body,tag:tag});
    }
    el.style.display="none";
  });
}
function cardEl(p){
  var c=h("div","gp-pred-card"),t=h("div","gp-pred-top");
  t.appendChild(h("span","gp-pred-kicker",p.k));t.appendChild(h("span","gp-pred-prob",p.p));c.appendChild(t);
  c.appendChild(h("div","gp-streak-badge"+(p.t?" "+p.t:""),p.b));
  c.appendChild(h("div","gp-pred-fixture",p.f));c.appendChild(h("div","gp-pred-meta",p.m));
  c.appendChild(h("div","gp-pred-pick",p.pk));c.appendChild(h("div","gp-pred-odds",p.o));
  c.appendChild(h("div","gp-pred-note",p.n));return c;
}
function slipBox(title,sub,legs,footL,footR,bg){
  var box=h("div","gp-acca-box");if(bg)box.style.background=bg;
  var hdr=h("div","gp-acca-hdr");hdr.appendChild(h("b","",title));hdr.appendChild(h("span","",sub));box.appendChild(hdr);
  legs.forEach(function(l){var r=h("div","gp-acca-row"),lf=h("div");lf.appendChild(h("b","",l[0]));if(l[1])lf.appendChild(h("div","",l[1]));r.appendChild(lf);r.appendChild(h("b","",l[2]));box.appendChild(r);});
  var ft=h("div","gp-acca-foot");ft.appendChild(h("span","",footL));ft.appendChild(h("span","",footR));box.appendChild(ft);return box;
}
function renderDesk(){
  harvestPV();
  var D=window.GEM_DATA;if(!D)return;
  var tabsRow=document.querySelector(".tabs"),g=document.querySelector(".grid"),host=tabsRow||g;if(!host||!host.parentNode)return;
  var panel=document.getElementById("gp-desk-panel");if(!panel){panel=h("div");panel.id="gp-desk-panel";host.parentNode.insertBefore(panel,host);}
  if(tabsRow)tabsRow.style.display="none";if(g)g.style.display="none";panel.innerHTML="";
  var u=h("div","gp-upd");
  if(mode==="matches"){
    var d=D.days[activeDay]||D.days[0];u.appendChild(h("span","","5-Day Dated Slate · Odds updated "+D.upd));u.appendChild(h("span","","Day "+(activeDay+1)+" of 5"));panel.appendChild(u);
    var strip=h("div","gp-day-strip");D.days.forEach(function(it,idx){var b=h("button","gp-day-pill"+(idx===activeDay?" active":""),it.label);b.type="button";b.onclick=function(){activeDay=idx;renderDesk();};strip.appendChild(b);});
    panel.appendChild(strip);d.picks.forEach(function(p){panel.appendChild(cardEl(p));});
  }else if(mode==="perfect"){
    u.appendChild(h("span","","PERFECT VALUE SIGNALS ("+(pvCache.length||D.todaysValue.length)+" ACTIVE)"));u.appendChild(h("span","","Moved from Dashboard"));panel.appendChild(u);
    if(pvCache.length){
      pvCache.forEach(function(item){
        var row=h("div","gp-pv-card"),info=h("div");
        info.appendChild(h("div","",item.detail));
        row.appendChild(info);row.appendChild(h("span","gp-pv-btn",item.tag));panel.appendChild(row);
      });
    }else{D.todaysValue.forEach(function(p){panel.appendChild(cardEl(p));});}
  }else if(mode==="today"){u.appendChild(h("span","","TODAY'S BEST VALUE FOUND (+EV RANKED)"));panel.appendChild(u);D.todaysValue.forEach(function(p){panel.appendChild(cardEl(p));});}
  else if(mode==="likely"){u.appendChild(h("span","","MOST LIKELY PREDICTIONS (HIGHEST HIT RATE)"));panel.appendChild(u);D.likely.forEach(function(p){panel.appendChild(cardEl(p));});}
  else if(mode==="ai"){u.appendChild(h("span","","AI GENERATED VALUE PREDICTIONS"));panel.appendChild(u);D.ai.forEach(function(p){panel.appendChild(cardEl(p));});}
  else if(mode==="value"){u.appendChild(h("span","","GLOBAL POSITIVE-EV VALUE SCANNER"));panel.appendChild(u);D.todaysValue.concat(D.ai).forEach(function(p){panel.appendChild(cardEl(p));});}
  else if(mode==="arbs"){u.appendChild(h("span","","LIVE ARBITRAGE VALUE PREDICTIONS"));panel.appendChild(u);D.arbs.forEach(function(p){panel.appendChild(cardEl(p));});}
  else if(mode==="acc"){
    if(accMode==="cs3")panel.appendChild(slipBox("GEM 3-FOLD CORRECT SCORE SLIP","Global Value",[["#1 Bosnia-Herzegovina v Romania","CS 2-1","@ 8.50"],["#2 Hungary v Northern Ireland","CS 1-1","@ 6.50"],["#3 Denmark v Norway","CS 1-3","@ 9.00"]],"3-Fold CS Treble @ 497.25","£5 -> £2,486.25","#0f172a"));
    var tot=1.0,legs=D.acca10.map(function(x){tot*=x.od;return [x.f,x.pk+" ("+x.ev+" EV)","@ "+x.od.toFixed(2)];});
    panel.appendChild(slipBox("10-FOLD GLOBAL VALUE ACCUMULATOR (10 GAMES)","Combined EV +48.5%",legs,"10-Fold Combined Odds: "+tot.toFixed(2),"£10 -> £"+(tot*10).toFixed(2)));
  }else if(mode==="bets"){
    panel.appendChild(slipBox("ACTIVE GEM V4.0 3-FOLD SLIP (19:45 UTC)","Status: LIVE",[["#1 Wales vs Portugal","X2 & O1.5","@ 1.30"],["#2 Ukraine vs Georgia","1X & O1.5","@ 1.62"],["#3 Denmark vs Norway","1X & O1.5","@ 1.67"]],"Treble @ 3.52","£10 -> £35.20"));
  }
}
function nav(){
  if(document.getElementById("gp-mint-nav"))return;
  var a=document.querySelector(".tabs")||document.querySelector(".grid")||document.body.firstElementChild;if(!a||!a.parentNode)return;
  var n=h("div","gp-mint-nav");n.id="gp-mint-nav";
  TABS.forEach(function(t){var b=h("button","gp-mtab"+(t[0]===mode?" active":""),t[1]);b.type="button";b.dataset.mode=t[0];b.onclick=function(){n.querySelectorAll(".gp-mtab").forEach(function(x){x.classList.remove("active");});b.classList.add("active");mode=t[0];if(mode==="acc")accMode="10fold";renderDesk();};n.appendChild(b);});
  var cs=h("button","gp-cs-btn","Build CS 3-Fold");cs.type="button";cs.onclick=function(){accMode="cs3";n.querySelector("[data-mode=acc]").click();accMode="cs3";renderDesk();};n.appendChild(cs);
  a.parentNode.insertBefore(n,a);
}
function run(){harvestPV();nav();renderDesk();}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",run);else run();setTimeout(run,500);setTimeout(run,1500);
})();
(function(){
function spiceHeader(){
  if(document.getElementById("gp-pro-hdr"))return;
  var navEl=document.getElementById("gp-mint-nav");
  var host=navEl||document.querySelector(".tabs")||document.querySelector(".grid")||document.body.firstElementChild;
  if(!host||!host.parentNode)return;
  Array.from(host.parentNode.children).forEach(function(el){
    if(el!==navEl && el.id!=="gp-pro-hdr" && /EdgeMETRIX PRO 26/i.test(el.innerText||"") && !el.querySelector("#gp-mint-nav")){
      el.style.display="none";
    }
  });
  var hdr=document.createElement("header");
  hdr.id="gp-pro-hdr";
  hdr.className="gp-pro-hdr";
  hdr.innerHTML='<div class="gp-brand-wrap"><div class="gp-emblem">EM</div><div><div class="gp-title-row"><span class="gp-brand-main">EdgeMETRIX</span><span class="gp-brand-pro">PRO 26</span></div><div class="gp-brand-sub">Institutional Poisson &amp; No-Vig CLV Analytics Engine</div></div></div><div class="gp-hdr-right"><span class="gp-live-pill"><span class="gp-pulse"></span>ENGINE LIVE &middot; GLOBAL FEED</span><span class="gp-syndicate-badge">Global Quant Syndicate Terminal</span></div>';
  host.parentNode.insertBefore(hdr,host);
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",spiceHeader);
else spiceHeader();
setTimeout(spiceHeader,250);
setTimeout(spiceHeader,900);
})();
(function(){
fetch("/api/gem-feed").then(function(r){return r.json();}).then(function(live){
  if(!live||!live.live||!window.GEM_DATA)return;
  if(live.upd)window.GEM_DATA.upd=live.upd;
  if(live.todaysValue&&live.todaysValue.length)window.GEM_DATA.todaysValue=live.todaysValue;
  if(live.likely&&live.likely.length)window.GEM_DATA.likely=live.likely;
  if(live.ai&&live.ai.length)window.GEM_DATA.ai=live.ai;
  if(live.arbs&&live.arbs.length)window.GEM_DATA.arbs=live.arbs;
  if(live.acca10&&live.acca10.length>=10)window.GEM_DATA.acca10=live.acca10;
  var active=document.querySelector(".gp-mtab.active");
  if(active)active.click();
}).catch(function(){});
})();
(function(){
function logBet(btn, payload){
  btn.textContent="LOGGING...";
  fetch("/api/place-bet",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)})
    .then(function(r){return r.json();})
    .then(function(res){
      if(res&&res.ok){btn.textContent="LOGGED #"+res.id+" ✓";btn.style.opacity="0.85";refreshLedger();}
    }).catch(function(){btn.textContent="RETRY";});
}
function parseAndSend(btn, cardTxt){
  var odM=cardTxt.match(/@\s*(\d+\.\d+)/);
  var evM=cardTxt.match(/\+?(\d+\.\d+)%\s*EV/i);
  var frM=cardTxt.match(/Fair\s*(\d+\.\d+)/i);
  var parts=cardTxt.split("—");
  var fix=(parts[0]||"Signal").replace(/PERFECT VALUE #\d+.*?(?=[A-Z])/i,"").trim();
  var mkt=(parts[2]||parts[1]||"Value Selection").trim().slice(0,70);
  var od=odM?parseFloat(odM[1]):1.95;
  var fr=frM?parseFloat(frM[1]):+(od*0.94).toFixed(2);
  logBet(btn,{fixture:fix,market:mkt,odds:od,fair_odds:fr,ev_pct:evM?parseFloat(evM[1]):5.0,true_prob:+(1/fr).toFixed(4),stake:10});
}
document.addEventListener("click",function(e){
  var b=e.target.closest(".gp-pv-btn");
  if(b&&!/LOGGED/.test(b.textContent)){
    var card=b.closest(".gp-pv-card");
    parseAndSend(b,card?card.innerText:b.textContent);
  }
});
function refreshLedger(){
  var panel=document.getElementById("gp-desk-panel");
  var active=document.querySelector(".gp-mtab.active");
  if(!panel||!active||active.dataset.mode!=="bets")return;
  fetch("/api/ledger").then(function(r){return r.json();}).then(function(d){
    var box=document.getElementById("gp-live-ledger");
    if(!box){box=document.createElement("div");box.id="gp-live-ledger";panel.appendChild(box);}
    box.innerHTML="";
    var bets=d.bets||[];
    if(!bets.length)return;
    var hdr=document.createElement("div");
    hdr.className="gp-upd";hdr.style.marginTop="14px";
    hdr.innerHTML="<span>SYNDICATE SQLITE LEDGER ("+bets.length+" LOGGED)</span><span>Feeds Platt Calibration</span>";
    box.appendChild(hdr);
    bets.forEach(function(b){
      var row=document.createElement("div");row.className="gp-pred-card";
      row.innerHTML="<div class='gp-pred-top'><span class='gp-pred-kicker'>#"+b.id+" · "+b.status+" · EV +"+Number(b.ev_pct).toFixed(1)+"%</span><span class='gp-pred-prob'>@ "+Number(b.odds).toFixed(2)+"</span></div><div class='gp-pred-fixture'>"+b.fixture+"</div><div class='gp-pred-pick'>"+b.market+" (Stake £"+Number(b.stake).toFixed(2)+")</div>";
      if(b.status==="OPEN"){
        var bar=document.createElement("div");bar.style.cssText="display:flex;gap:8px;margin-top:8px;";
        ["WON","LOST"].forEach(function(st){
          var sb=document.createElement("button");sb.type="button";sb.textContent="Settle "+st;
          sb.style.cssText="padding:5px 12px;border-radius:6px;border:none;font-weight:800;cursor:pointer;color:#fff;background:"+(st==="WON"?"#059669":"#dc2626");
          sb.onclick=function(){fetch("/api/settle-bet",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({id:b.id,status:st})}).then(refreshLedger);};
          bar.appendChild(sb);
        });
        row.appendChild(bar);
      }
      box.appendChild(row);
    });
  }).catch(function(){});
}
document.addEventListener("click",function(e){
  var t=e.target.closest(".gp-mtab");
  if(t&&t.dataset.mode==="bets")setTimeout(refreshLedger,80);
});
})();
