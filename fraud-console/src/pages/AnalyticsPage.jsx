import {Link} from 'react-router-dom';import {api} from '../api';import {usePoll} from '../hooks';import {col,money} from '../util';
const top=(fl,k)=>Object.entries(fl.reduce((m,f)=>{const x=(m[k(f)]??={n:0,a:0});x.n++;x.a+=f.transaction.amount;return m},{})).sort((a,b)=>b[1].n-a[1].n||b[1].a-a[1].a).slice(0,5);
const csv=fl=>{const r=fl.map(f=>[f.id,f.transaction.id,f.transaction.user_id,`"${f.transaction.merchant}"`,f.transaction.amount,f.transaction.city,f.risk_score,f.risk_level,f.review_status,`"${f.reasons.map(x=>x.rule).join('|')}"`].join(','));
 const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([['flag_id,tx_id,user,merchant,amount,city,risk_score,level,status,reasons',...r].join('\n')],{type:'text/csv'}));a.download='flags.csv';a.click()};
const Card=({t,children})=><section className="rounded-xl border border-[#1b2440] bg-[#0d1326] p-4"><h2 className="mb-3 text-sm text-slate-400">{t}</h2>{children}</section>;
const List=({t,rows,link})=><Card t={t}>{rows.map(([k,v])=><div key={k} className="flex justify-between border-b border-[#1b2440] py-1.5 text-sm last:border-0">
 {link?<Link to={`/customers/${k}`} className="underline decoration-dotted">{k}</Link>:<span>{k}</span>}<span className="text-slate-400">{v.n} flags · {money(v.a)}</span></div>)}</Card>;
export default function Analytics(){
 const [d,err]=usePoll(()=>Promise.all([api.flags(),api.stats()]).then(([f,s])=>({fl:f.items,s})),4000);
 if(!d)return<div className="p-8 text-slate-400">{err?`Could not load: ${err}`:'Loading…'}</div>;
 const {fl,s}=d,held=fl.filter(f=>f.review_status==='PENDING').reduce((a,f)=>a+f.transaction.amount,0),avg=fl.length?Math.round(fl.reduce((a,f)=>a+f.risk_score,0)/fl.length):0;
 const B=[0,20,40,60,80].map(lo=>({lo,n:fl.filter(f=>f.risk_score>=lo&&f.risk_score<lo+20+(lo===80?1:0)).length})),mx=Math.max(...B.map(b=>b.n),1);
 const o=s.by_status,ot=(o.PENDING+o.REVIEWED+o.CLEARED)||1,K=[[money(held),'held in pending flags'],[avg,'average risk score'],[`${s.flag_rate}%`,'of transactions flagged'],[`${s.false_positive_rate}%`,'false positives']];
 return(<div className="mx-auto max-w-[1400px] px-6 py-8"><div className="flex items-center justify-between"><h1 className="text-3xl font-bold">Analytics</h1>
 <button onClick={()=>csv(fl)} className="rounded-lg border border-[#1b2440] bg-[#101833] px-3 py-1.5 text-sm hover:bg-[#182246]">Export flags (CSV)</button></div>
 <div className="my-6 grid gap-4 md:grid-cols-4">{K.map(([v,l])=><Card key={l} t={l}><div className="text-3xl font-bold">{v}</div></Card>)}</div>
 <div className="grid gap-4 md:grid-cols-2"><Card t="Risk score distribution"><div className="flex h-40 items-end gap-3">{B.map(b=><div key={b.lo} className="flex flex-1 flex-col items-center justify-end gap-1">
 <b className="text-sm">{b.n}</b><div className="w-full rounded-t" style={{height:`${b.n/mx*100}%`,minHeight:2,background:col(b.lo+10)}}/><span className="text-xs text-slate-400">{b.lo}–{b.lo===80?100:b.lo+19}</span></div>)}</div></Card>
 <Card t="Review outcomes"><div className="flex h-4 overflow-hidden rounded">{[['PENDING','#ef4444'],['REVIEWED','#f59e0b'],['CLEARED','#22c55e']].map(([k,c])=><div key={k} style={{width:`${o[k]/ot*100}%`,background:c}}/>)}</div>
 <div className="mt-3 flex gap-6 text-sm"><span>Flagged <b>{o.PENDING}</b></span><span>Reviewed <b>{o.REVIEWED}</b></span><span>Cleared <b>{o.CLEARED}</b></span></div></Card>
 <List t="Top merchants by flags" rows={top(fl,f=>f.transaction.merchant)}/><List t="Top customers by flags" rows={top(fl,f=>f.transaction.user_id)} link/></div></div>)}
