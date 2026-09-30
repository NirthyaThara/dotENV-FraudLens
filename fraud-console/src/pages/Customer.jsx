import {Link,useParams} from 'react-router-dom';import {usePoll,loadBoth} from '../hooks';import {TxTable} from './Transactions';import {ruleMeta,col,label,stCls,money} from '../util';
export default function Customer(){
 const {userId}=useParams(),[d,err]=usePoll(()=>loadBoth(userId),4000,[userId]);
 if(!d)return<div className="p-8 text-slate-400">{err?`Could not load: ${err}`:'Loading…'}</div>;
 const tx=d.tx.filter(t=>t.user_id===userId),fl=d.flags.filter(f=>f.transaction.user_id===userId),fm=new Map(fl.map(f=>[f.transaction_id,f]));
 const avg=tx.length?tx.reduce((a,t)=>a+t.amount,0)/tx.length:0,K=[[tx.length,'transactions'],[money(avg),'average amount'],[fl.length,'flags'],[new Set(tx.map(t=>t.city)).size,'cities used']];
 return(<div className="mx-auto max-w-[1400px] px-6 py-8"><Link to="/transactions" className="text-sm text-slate-400 hover:text-white">Back to transactions</Link>
 <h1 className="mt-2 text-3xl font-bold">Customer {userId}</h1>
 <div className="my-6 grid gap-4 md:grid-cols-4">{K.map(([v,l])=><div key={l} className="rounded-xl border border-[#1b2440] bg-[#0d1326] p-4"><div className="text-3xl font-bold">{v}</div><div className="text-sm text-slate-400">{l}</div></div>)}</div>
 <h2 className="mb-2 font-semibold">Flags</h2>{fl.length?<div className="space-y-2">{fl.map(f=><div key={f.id} className="flex flex-wrap items-center gap-3 rounded-lg border border-[#1b2440] bg-[#0d1326] p-3 text-sm">
 <span className="rounded-full px-2.5 py-0.5 font-bold text-black" style={{background:col(f.risk_score)}}>{f.risk_score}</span><span>{f.transaction.merchant}</span><span className="text-slate-400">{money(f.transaction.amount,f.transaction.currency)}</span>
 {f.reasons.map(r=>{const m=ruleMeta(r.rule);return<span key={r.rule} title={r.message} className="inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs" style={{background:m.c+'22',color:m.c}}><m.I size={12}/>{m.n}</span>})}
 <span className={`ml-auto rounded px-2 py-0.5 text-xs ${stCls[f.review_status]}`}>{label[f.review_status]}</span></div>)}</div>:<p className="text-sm text-slate-400">No flags for this customer.</p>}
 <h2 className="mb-2 mt-8 font-semibold">Transaction history</h2><TxTable rows={tx} fm={fm}/></div>)}
