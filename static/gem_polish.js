(function(){
var mode="likely";
var TABS=[["matches","Matches"],["today","Today picks"],["likely","Likely"],["ai","AI"],["value","Value"],["arbs","Arbs"],["acc","Accumulator"],["bets","Bets"]];
function nav(){
  if(document.getElementById("gp-mint-nav"))return;
  var a=document.querySelector(".tabs")||document.querySelector(".grid")||document.body.firstElementChild;
  if(!a||!a.parentNode)return;
  var n=document.createElement("div");
  n.id="gp-mint-nav";
  n.className="gp-mint-nav";
  n.innerHTML=TABS.map(function(t){return '<button type="button" class="gp-mtab'+(t[0]===mode?' active':'')+'" data-mode="'+t[0]+'">'+t[1]+'</button>';}).join("")+'<button type="button" class="gp-cs-btn" id="gp-build-cs">Build CS 3-Fold</button>';
  a.parentNode.insertBefore(n,a);
  n.querySelectorAll(".gp-mtab").forEach(function(b){
    b.onclick=function(){
      n.querySelectorAll(".gp-mtab").forEach(function(x){x.classList.remove("active");});
      b.classList.add("active");
      mode=b.dataset.mode;
      view();
    };
  });
  var csBtn=document.getElementById("gp-build-cs");
  if(csBtn)csBtn.onclick=function(){n.querySelector('[data-mode="acc"]').click();};
}
function view(){
  var g=document.querySelector(".grid");
  if(!g)return;
  var cs=Array.from(g.querySelectorAll(".card"));
  var sl=document.getElementById("gp-cs-slip");
  if(!sl){
    sl=document.createElement("div");
    sl.id="gp-cs-slip";
    sl.className="gp-cs-slip";
    g.parentNode.insertBefore(sl,g);
  }
  var pk=cs.slice();
  if(mode==="likely")pk=cs.filter(function(c){return /SYN-9/.test(c.innerText);});
  else if(mode==="value")pk=cs.filter(function(c){return /STRONG VALUE/.test(c.innerText);});
  else if(mode==="ai")pk=cs.filter(function(c){return /ELITE|SYN-9\.5/.test(c.innerText);});
  else if(mode==="acc"||mode==="bets")pk=cs.slice(0,3);
  if(!pk.length)pk=cs.slice();
  var st=new Set(pk);
  cs.forEach(function(c){c.style.display=st.has(c)?"":"none";});
  if(mode==="acc"){
    var legs=cs.slice(0,3).map(function(c,i){
      var t=(c.querySelector("h3,h4,.match,.title")||c).innerText.split("\n")[0].trim();
      var m=c.innerText.match(/CS\s*([0-9]+-[0-9]+)/i);
      var csScore=m?m[1]:["2-1","1-1","2-0"][i];
      var od=[8.50,6.50,9.00][i];
      return '<div class="gp-cs-leg"><b>#'+(i+1)+' '+t+'</b><span>Correct Score '+csScore+' @ '+od.toFixed(2)+'</span></div>';
    }).join("");
    sl.classList.add("open");
    sl.innerHTML='<div class="gp-cs-hdr"><span class="gp-cs-title">GEM 3-FOLD CORRECT SCORE SLIP (GLOBAL VALUE)</span></div>'+legs+'<div class="gp-cs-foot"><b>3-Fold CS Treble @ 497.25 (\u00a35 \u2192 \u00a32,486.25)</b></div>';
  }else if(mode==="bets"){
    sl.classList.add("open");
    sl.innerHTML='<div class="gp-cs-hdr"><span class="gp-cs-title">ACTIVE GEM V4.0 3-FOLD SLIP (19:45 UTC)</span></div><div class="gp-cs-leg"><b>#1 Wales vs Portugal</b><span>X2 &amp; O1.5 @ 1.30</span></div><div class="gp-cs-leg"><b>#2 Ukraine vs Georgia</b><span>1X &amp; O1.5 @ 1.62</span></div><div class="gp-cs-leg"><b>#3 Denmark vs Norway</b><span>1X &amp; O1.5 @ 1.67</span></div><div class="gp-cs-foot"><b>Treble @ 3.52 (\u00a310 \u2192 \u00a335.20)</b></div>';
  }else{
    sl.classList.remove("open");
  }
}
function run(){nav();view();}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",run);
else run();
setTimeout(run,500);
setTimeout(run,1500);
})();
