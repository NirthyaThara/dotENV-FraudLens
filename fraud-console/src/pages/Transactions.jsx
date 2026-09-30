import {useState} from 'react';import {Link} from 'react-router-dom';import {usePoll,loadBoth} from '../hooks';import {money,tm,col} from '../util';
export function TxTable({rows,fm}){return(<div className="overflow-x-auto"><table className="w-full min-w-[820px] text-left text-sm">
 <thead className="text-slate-400"><tr className="border-b border-[#1b2440]">{['Transaction','Customer','Merchant','Amount','Location','Time','Result'].map(h=><th key={h} className="px-3 py-3 font-medium">{h}</th>)}</tr></thead>
 <tbody>{rows.map(t=>{const fl=fm.get(t.id);return<tr key={t.id} className="border-b border-[#1b2440]">
 <td className="px-3 py-3 text-slate-400">TX-{t.id}</td><td className="px-3"><Link to={`/customers/${t.user_id}`} className="underline decoration-dotted hover:text-white">{t.user_id}</Link></td>
 <td className="px-3">{t.merchant}</td><td className="px-3 tabular-nums">{money(t.amount,t.currency)}</td><td className="px-3">{t.city}, {t.country}</td><td className="px-3 tabular-nums">{tm(t.timestamp)}</td>
 <td className="px-3">{fl?<span className="rounded-full px-2.5 py-0.5 text-xs font-bold text-black" style={{background:col(fl.risk_score)}}>Flagged {fl.risk_score}</span>:<span className="text-xs text-slate-500">Clean</span>}</td></tr>})}</tbody></table>
 {!rows.length&&<div className="py-12 text-center text-slate-400">No transactions match.</div>}</div>)}
export default function Transactions(){
 const [d,err]=usePoll(()=>loadBoth(),4000),[f,setF]=useState('ALL'),[q,setQ]=useState('');
 const fm=new Map((d?.flags||[]).map(x=>[x.transaction_id,x]));
 const rows=(d?.tx||[]).filter(t=>(f==='ALL'||(f==='FLAGGED')===fm.has(t.id))&&(!q||`${t.user_id} ${t.merchant} ${t.city}`.toLowerCase().includes(q.toLowerCase())));
 return(<div className="mx-auto max-w-[1400px] px-6 py-8"><h1 className="text-3xl font-bold">All transactions</h1>
 <p className="mt-1 text-slate-400">{d?`${d.tx.length} screened · ${fm.size} flagged`:err?`Could not load: ${err}`:'Loading…'}</p>
 <div className="my-5 flex flex-wrap gap-2">{[['ALL','All'],['FLAGGED','Flagged'],['CLEAN','Clean']].map(([k,l])=><button key={k} onClick={()=>setF(k)} className={`rounded-lg px-4 py-2 text-sm ${f===k?'bg-[#182246]':'text-slate-400 hover:text-white'}`}>{l}</button>)}
 <input value={q} onChange={e=>setQ(e.target.value)} placeholder="Search customer, merchant, city" className="rounded-lg border border-[#1b2440] bg-[#0d1326] px-3 py-2 text-sm"/></div>
 <TxTable rows={rows} fm={fm}/></div>)}
