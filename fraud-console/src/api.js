const BASE=import.meta.env.VITE_API_URL||'http://localhost:8000';
const list=r=>Array.isArray(r)?r:(r?.items||[]);
const nf=f=>({reasons:[],notified:false,...f,review_status:String(f.review_status||'PENDING').toUpperCase(),transaction:{amount:0,currency:'INR',merchant:'Unknown',city:'',country:'',user_id:'',...(f.transaction||{})}});
const ns=s=>({total_transactions:0,total_flags:0,flag_rate:0,false_positive_rate:0,...s,by_level:{LOW:0,MEDIUM:0,HIGH:0,...s?.by_level},by_status:{PENDING:0,REVIEWED:0,CLEARED:0,...s?.by_status},by_rule:{...s?.by_rule}});
let mock=true,outage=false;
export const setMock=v=>{mock=v};export const setOutage=v=>{outage=v};export const getMode=()=>({mock,outage});
const C=['Chennai,IN','London,GB','Dubai,AE','Kyiv,UA','Singapore,SG','Sao Paulo,BR','Mumbai,IN','Tokyo,JP'];
const M=['Vault Crypto Exchange','Crestview Jewellers','PayBridge Transfer','Aurora Electronics','Orbit Cab','StreamBox','Lumen Fuel'];
const R=a=>a[Math.floor(Math.random()*a.length)];
const RS={velocity:()=>['6 transactions in 5 minutes',30],amount:()=>["Amount is 8x the user's average",25],
impossible_location:()=>{const[a,b]=[R(C),R(C)].map(x=>x.split(',')[0]);return[`${a} to ${b} in 20 min (about 24,000 km/h)`,40,{from:a,to:b,speed_kmh:24000}]}};
let seq=1000,fid=0,normal=20,db=[];
function mk(rules,status='PENDING'){
 const reasons=rules.map(r=>{const[message,score,metadata]=RS[r]();return{rule:r,score,message,metadata}});
 const risk_score=Math.min(99,reasons.reduce((s,r)=>s+r.score,0)+Math.floor(Math.random()*12));
 const[city,country]=R(C).split(',');const now=new Date().toISOString();
 const f={id:++fid,transaction_id:++seq,risk_score,risk_level:risk_score>=70?'HIGH':risk_score>=40?'MEDIUM':'LOW',reasons,review_status:status,
 reviewed_at:status==='PENDING'?null:now,review_comment:null,notified:risk_score>=70,created_at:now,
 transaction:{id:seq,user_id:'U'+(1000+Math.floor(Math.random()*9)),amount:Math.round(2000+Math.random()*60000),currency:'INR',merchant:R(M),city,country,timestamp:now}};
 db.unshift(f);return f}
let ntx=[];const gen=n=>Array.from({length:n},()=>{const[city,country]=R(C).split(',');return{id:++seq,user_id:'U'+(1000+Math.floor(Math.random()*9)),amount:Math.round(500+Math.random()*9000),currency:'INR',merchant:R(M),city,country,timestamp:new Date().toISOString()}});
const seed=()=>{db=[];fid=0;normal=20;ntx=gen(20);['impossible_location','velocity','amount'].forEach(r=>mk([r]));mk(['velocity','amount','impossible_location']);mk(['amount']);mk(['velocity'],'CLEARED');mk(['amount'],'REVIEWED')};
seed();
const mstats=()=>{const by=(fn,ks)=>Object.fromEntries(ks.map(k=>[k,db.filter(f=>fn(f,k)).length]));
 const rv=db.filter(f=>f.review_status==='REVIEWED').length,cl=db.filter(f=>f.review_status==='CLEARED').length;
 return{total_transactions:normal+db.length,total_flags:db.length,flag_rate:+(db.length/(normal+db.length)*100).toFixed(1),
 by_level:by((f,k)=>f.risk_level===k,['LOW','MEDIUM','HIGH']),by_status:by((f,k)=>f.review_status===k,['PENDING','REVIEWED','CLEARED']),
 by_rule:by((f,k)=>f.reasons.some(r=>r.rule===k),['velocity','amount','impossible_location']),false_positive_rate:rv+cl?+(cl/(rv+cl)*100).toFixed(1):0}};
async function req(p,o={}){
 const r=await fetch(BASE+p,{headers:{'Content-Type':'application/json'},...o});
 if(!r.ok)throw new Error((await r.json().catch(()=>({}))).detail||r.statusText);return r.json()}
const guard=v=>outage?Promise.reject(new Error('Backend offline')):Promise.resolve(structuredClone(v));
export const api={
 flags:()=>mock?guard({items:db}):(outage?guard():req('/flags?limit=200').then(r=>({items:list(r).map(nf)}))),
 transactions:uid=>mock?guard({items:[...db.map(f=>f.transaction),...ntx].filter(t=>!uid||t.user_id===uid).sort((a,b)=>b.id-a.id)}):req(`/transactions?limit=200${uid?`&user_id=${uid}`:''}`).then(r=>({items:list(r)})),
 stats:()=>mock?guard(mstats()):req('/stats').then(ns),
 act:(id,a,comment)=>{if(!mock)return req(`/flags/${id}/${a}`,{method:'PATCH',body:JSON.stringify({comment:comment||null})});
  const f=db.find(x=>x.id===id);f.review_status=a==='review'?'REVIEWED':'CLEARED';f.reviewed_at=new Date().toISOString();f.review_comment=comment||null;return guard(f)},
 simulate:s=>{if(!mock)return req(`/simulate/${s}`,{method:'POST'});
  if(s==='normal'){normal+=5;ntx.push(...gen(5));return guard({created:5,flags:0})}
  if(s==='velocity'){mk(['velocity','amount']);return guard({created:6,flags:1})}
  mk(['impossible_location','velocity']);return guard({created:2,flags:1})},
 reset:()=>{if(!mock)return req('/demo/reset',{method:'DELETE'});seed();return guard({status:'ok'})}};
