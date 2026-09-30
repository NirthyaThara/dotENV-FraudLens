import {Link} from 'react-router-dom';import {ruleMeta,col,label,stCls,money,tm} from '../util';
export default function FlagTable({rows,fresh,chk,setChk,sel,open,act}){
 if(!rows.length)return<div className="py-16 text-center text-slate-400">No flags match these filters. Use “Simulate fraud” to generate one.</div>;
 const tog=id=>{const n=new Set(chk);n.has(id)?n.delete(id):n.add(id);setChk(n)};
 return(<div className="overflow-x-auto"><table className="w-full min-w-[980px] text-left text-sm">
 <thead className="text-slate-400"><tr className="border-b border-[#1b2440]">{['','Risk','Merchant','Amount','Location','Time','Reasons','Status','Action'].map(h=><th key={h} className="px-3 py-3 font-medium">{h}</th>)}</tr></thead>
 <tbody>{rows.map(f=>{const t=f.transaction,p=f.review_status==='PENDING';return(
 <tr key={f.id} onClick={()=>open(f.id)} className={`cursor-pointer border-b border-[#1b2440] hover:bg-[#0d1326] ${sel===f.id?'bg-[#0d1326] outline outline-1 outline-slate-600':''} ${fresh.has(f.id)?'flash':''}`}>
 <td className="px-3" onClick={e=>e.stopPropagation()}>{p&&<input type="checkbox" aria-label="Select flag" checked={chk.has(f.id)} onChange={()=>tog(f.id)}/>}</td>
 <td className="px-3 py-3 w-28"><span className="rounded-full px-2.5 py-0.5 font-bold text-black" style={{background:col(f.risk_score)}}>{f.risk_score}</span>
 <div className="mt-1.5 h-1 w-20 rounded bg-[#1b2440]"><div className="h-1 rounded" style={{width:`${f.risk_score}%`,background:col(f.risk_score)}}/></div></td>
 <td className="px-3"><div className="font-semibold">{t.merchant}</div><div className="text-xs text-slate-400">TX-{t.id} · <Link to={`/customers/${t.user_id}`} onClick={e=>e.stopPropagation()} className="underline decoration-dotted hover:text-white">{t.user_id}</Link></div></td>
 <td className="px-3 tabular-nums">{money(t.amount,t.currency)}</td><td className="px-3">{t.city}, {t.country}</td><td className="px-3 tabular-nums">{tm(t.timestamp)}</td>
 <td className="px-3"><div className="flex flex-wrap gap-1">{f.reasons.map(r=>{const m=ruleMeta(r.rule);
 return<span key={r.rule} title={r.message} className="inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs" style={{background:m.c+'22',color:m.c}}><m.I size={12}/>{m.n} +{r.score}</span>})}</div></td>
 <td className="px-3"><span className={`rounded px-2 py-0.5 text-xs font-medium ${stCls[f.review_status]}`}>{label[f.review_status]}</span>{f.notified&&<span className="ml-1.5 rounded border border-[#1b2440] px-1.5 py-0.5 text-[11px] text-slate-400">Alert sent</span>}</td>
 <td className="px-3" onClick={e=>e.stopPropagation()}>{p&&<div className="flex gap-1.5">
 <button onClick={()=>act(f.id,'review')} className="rounded-md border border-[#1b2440] bg-[#101833] px-3 py-1 hover:bg-[#182246]">Review</button>
 <button onClick={()=>act(f.id,'clear')} className="rounded-md border border-green-500/30 bg-green-500/10 px-3 py-1 text-green-300 hover:bg-green-500/20">Clear</button></div>}</td></tr>)})}</tbody></table></div>)}
