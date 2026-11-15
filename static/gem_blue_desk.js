(function(){
var MIN_EV=4.5,ST={tab:'Likely',day:'Today (Sun 15)',items:[]};
var FB=[
  {tab:'Likely',day:'Today (Sun 15)',title:'Spain v England',time:'Sun 15 Nov ? 19:45 GMT ? UEFA Nations League',pick:'Spain Full Time Win (10/11)',prob:'64%',odds:'1.91',ev:'+5.6%',evNum:5.6,kelly:'1.55%',tag:'PERFECT VALUE ? 19:45 GMT',strat:'Dixon-Coles + No-Vig (60/40) | Fair 1.81 vs 1.91'},
  {tab:'Likely',day:'Today (Sun 15)',title:'Belgium v Italy',time:'Sun 15 Nov ? 19:45 GMT ? UEFA Nations League',pick:'Belgium Draw No Bet / Win',prob:'58%',odds:'2.20',ev:'+5.1%',evNum:5.1,kelly:'1.06%',tag:'PERFECT VALUE ? 19:45 GMT',strat:'Dixon-Coles + No-Vig (60/40) | Fair 2.09 vs 2.20'},
  {tab:'Likely',day:'Today (Sun 15)',title:'Granada CF v UD Las Palmas (FT 1-0 WON)',time:'Sun 15 Nov ? Settled ? Segunda',pick:'Granada Full Time Result',prob:'61%',odds:'2.10',ev:'+8.8%',evNum:8.8,kelly:'2.00%',tag:'SETTLED WON ? +8.8% EV',strat:'Dixon-Coles + No-Vig (60/40) | Fair 1.85 vs 2.10'},
  {tab:'Likely',day:'Today (Sun 15)',title:'CD Tenerife v AD Ceuta FC (FT 2-0 WON)',time:'Sun 15 Nov ? Settled ? Segunda',pick:'Tenerife Home Win',prob:'68%',odds:'1.62',ev:'+5.1%',evNum:5.1,kelly:'2.06%',tag:'SETTLED WON ? +5.1% EV',strat:'Dixon-Coles + No-Vig (60/40) | Fair 1.54 vs 1.62'},
  {tab:'Today Picks',day:'Today (Sun 15)',title:'Spain v England',time:'Sun 15 Nov ? 19:45 GMT ? Nations League',pick:'Spain Full Time Win (10/11)',prob:'64%',odds:'1.91',ev:'+5.6%',evNum:5.6,kelly:'1.55%',tag:'PICK OF THE DAY ? +5.6% EV',strat:'Dixon-Coles + No-Vig (60/40) | Fair 1.81 vs 1.91'},
  {tab:'AI Predictions',day:'Today (Sun 15)',title:'Dixon-Coles xG ? Spain v England',time:'Sun 15 Nov ? 19:45 GMT ? xG 1.78 vs 0.96',pick:'Spain Win & Over 1.5 Goals',prob:'64%',odds:'1.91',ev:'+5.6%',evNum:5.6,kelly:'1.55%',tag:'DIXON-COLES +5.6% EV',strat:'Bivariate Poisson (rho=-0.13) + Pinnacle No-Vig'},
  {tab:'3-Fold Accas',day:'Today (Sun 15)',title:'Tonight 19:45 GMT +4.5% EV 3-Fold',time:'Sun 15 Nov ? 19:45 GMT Kick-Offs',pick:'1) Spain Win  2) Belgium DNB  3) Croatia Win',prob:'52%',odds:'4.46',ev:'+11.2%',evNum:11.2,kelly:'0.85%',tag:'3-FOLD ACCA ? >= +4.5% EV',strat:'Strict >= +4.5% EV Gate ? Quarter-Kelly 0.85%'}
];
function pEv(v){var m=String(v||'').match(/[-+]?\d+(?:\.\d+)?/);return m?parseFloat(m[0]):0;}
function norm(x){
  var t=x.title||x.match||x.fixture||(x.home_team?x.home_team+' v '+x.away_team:'GEM Pick');
  var pk=x.selection||x.pick||x.market||x.desc||'Model Selection';
  var tm=x.kickoff||x.date||x.time||x.league||('Source: '+(x._src||'QUANT'));
  var n=parseFloat(String(x.prob||x.win_prob||x.model_prob||'62').replace('%',''));
  n=!isNaN(n)?((n>0&&n<=1)?Math.round(n*100):Math.round(n)):62;
  var evN=pEv(x.ev||x.edge||x.ev_pct||0),st=x.strategy||x.model||'Dixon-Coles + No-Vig (60/40)';
  var bl=(t+' '+pk+' '+st).toLowerCase(),tb='Likely';
  if(bl.indexOf('fold')>-1||bl.indexOf('acca')>-1)tb='3-Fold Accas';else if(bl.indexOf('xg')>-1)tb='AI Predictions';
  return {tab:tb,day:'Today (Sun 15)',title:t,time:tm,pick:pk,prob:n+'%',odds:x.odds||x.price||'--',ev:'+'+evN.toFixed(1)+'%',evNum:evN,kelly:x.kelly||'1.5%',tag:'PERFECT VALUE ? +'+evN.toFixed(1)+'% EV',strat:st};
}
