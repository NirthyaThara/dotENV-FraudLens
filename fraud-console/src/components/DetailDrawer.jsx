import {useState} from 'react';import RiskGauge from './RiskGauge';import {ruleMeta,label,stCls,money,col} from '../util';
function Travel({rule,to}){
 const md=rule.metadata,m=rule.message.match(/^(.+?)\s+to\s+(.+?)\s+in\s+(.+?)(?:\s*\((.+)\))?$/),
 from=md?.from||m?.[1]||'Previous location',dest=md?.to||m?.[2]||to,
 info=md?.speed_kmh?`${Number(md.speed_kmh).toLocaleString()} km/h`:m?`${m[3]}${m[4]?' · '+m[4]:''}`:'';
 return(<div className="rounded-lg border border-[#1b2440] bg-[#0a0f1e] p-3"><svg viewBox="0 0 300 90" className="w-full">
 <path d="M40 60 Q150 -10 260 60" fill="none" stroke="#f43f5e" strokeWidth="2" strokeDasharray="5 5"/>
 <circle cx="40" cy="60" r="6" fill="#38bdf8"/><circle cx="260" cy="60" r="6" fill="#f43f5e"/>
 <text x="40" y="82" textAnchor="middle" fontSize="11" fill="#cbd5e1">{from}</text><text x="260" y="82" textAnchor="middle" fontSize="11" fill="#cbd5e1">{dest}</text>
 <text x="150" y="38" textAnchor="middle" fontSize="11" fill="#fda4af">{info}</text></svg></div>)}
export default function DetailDrawer({flag:f,onClose,act}){
 const [c,setC]=useState('');if(!f)return null;const t=f.transaction,p=f.review_status==='PENDING',loc=f.reasons.find(r=>r.rule==='impossible_location');
 const go=a=>{act(f.id,a,c);onClose()};
 return(<><div className="fixed inset-0 z-10 bg-black/50" onClick={onClose}/><aside className="drawer fixed right-0 top-0 z-20 h-full w-full max-w-md overflow-y-auto border-l border-[#1b2440] bg-[#0d1326] p-6">
 <div className="flex items-start justify-between"><div><div className="text-xl font-bold">{t.merchant}</div><div className="text-sm text-slate-400">TX-{t.id} · {t.user_id}</div></div>
 <button onClick={onClose} aria-label="Close" className="text-2xl text-slate-400 hover:text-white">×</button></div>
 <div className="my-4 flex flex-col items-center"><RiskGauge score={f.risk_score} size={260}/><span className={`mt-1 rounded px-2 py-0.5 text-xs ${stCls[f.review_status]}`}>{label[f.review_status]}{f.notified?' · Alert sent':''}</span></div>
 <h3 className="mb-2 font-semibold">Why it was flagged</h3>
 <ul className="space-y-3">{f.reasons.map(r=>{const m=ruleMeta(r.rule);return<li key={r.rule}>
 <div className="flex justify-between text-sm"><span className="inline-flex items-center gap-1.5"><m.I size={14}/>{m.n}</span><b>+{r.score}</b></div><div className="my-1 h-1.5 rounded bg-[#1b2440]"><div className="h-1.5 rounded" style={{width:`${Math.min(r.score/Math.max(40,...f.reasons.map(x=>x.score))*100,100)}%`,background:m.c}}/></div>
 <div className="text-xs text-slate-400">{r.message}</div></li>})}</ul>
 {loc&&<div className="mt-4"><Travel rule={loc} to={t.city}/></div>}
 <dl className="mt-4 grid grid-cols-2 gap-2 text-sm"><dt className="text-slate-400">Amount</dt><dd>{money(t.amount,t.currency)}</dd><dt className="text-slate-400">Location</dt><dd>{t.city}, {t.country}</dd>
 <dt className="text-slate-400">Time</dt><dd>{new Date(t.timestamp).toLocaleString()}</dd><dt className="text-slate-400">Risk level</dt><dd style={{color:col(f.risk_score)}}>{f.risk_level}</dd></dl>
 {p?<><textarea value={c} onChange={e=>setC(e.target.value)} placeholder="Add a note, e.g. called the customer" className="mt-4 w-full rounded-lg border border-[#1b2440] bg-[#0a0f1e] p-2 text-sm" rows={3}/>
 <div className="mt-3 flex gap-2"><button onClick={()=>go('review')} className="flex-1 rounded-lg border border-[#1b2440] bg-[#101833] py-2 hover:bg-[#182246]">Review</button>
 <button onClick={()=>go('clear')} className="flex-1 rounded-lg border border-green-500/30 bg-green-500/10 py-2 text-green-300 hover:bg-green-500/20">Clear</button></div></>
 :<div className="mt-4 rounded-lg border border-[#1b2440] p-3 text-sm text-slate-300"><div className="text-slate-400">{label[f.review_status]} at {f.reviewed_at&&new Date(f.reviewed_at).toLocaleString()}</div>{f.review_comment&&<div className="mt-1">“{f.review_comment}”</div>}</div>}
 <p className="mt-4 text-xs text-slate-500">Shortcuts: J/K move · R review · C clear · Esc close</p></aside></>)}
