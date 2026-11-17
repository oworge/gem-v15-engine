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
