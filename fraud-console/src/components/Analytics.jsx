import {ruleMeta,col} from '../util';
export default function Analytics({stats}){
 if(!stats)return null;const r=Object.entries(stats.by_rule),tot=r.reduce((s,[,v])=>s+v,0)||1,C=2*Math.PI*40;let off=0;
 return(<section className="mt-6 grid gap-4 md:grid-cols-4">
 <div className="flex items-center gap-4 rounded-xl border border-[#1b2440] bg-[#0d1326] p-4">
 <svg viewBox="0 0 100 100" width="90" className="-rotate-90">{r.map(([k,v])=>{const d=v/tot*C,e=<circle key={k} cx="50" cy="50" r="40" fill="none" stroke={ruleMeta(k).c} strokeWidth="14" strokeDasharray={`${d} ${C-d}`} strokeDashoffset={-off}/>;off+=d;return e})}</svg>
 <ul className="text-sm">{r.map(([k,v])=><li key={k}><span style={{color:ruleMeta(k).c}}>●</span> {ruleMeta(k).n} <b>{v}</b></li>)}</ul></div>
 <div className="rounded-xl border border-[#1b2440] bg-[#0d1326] p-4 text-sm"><div className="mb-2 text-slate-400">Flags by risk level</div>
 {[['HIGH',80],['MEDIUM',55],['LOW',20]].map(([k,s])=>{const v=stats.by_level[k]||0,m=Math.max(...Object.values(stats.by_level),1);
 return<div key={k} className="mb-1.5 flex items-center gap-2"><span className="w-16">{k}</span><div className="h-2 flex-1 rounded bg-[#1b2440]"><div className="h-2 rounded" style={{width:`${v/m*100}%`,background:col(s)}}/></div><b>{v}</b></div>})}</div>
 <div className="rounded-xl border border-[#1b2440] bg-[#0d1326] p-4"><div className="text-3xl font-bold">{stats.total_transactions}</div><div className="text-sm text-slate-400">transactions checked · {stats.flag_rate}% flagged</div></div>
 <div className="rounded-xl border border-[#1b2440] bg-[#0d1326] p-4"><div className="text-3xl font-bold text-amber-400">{stats.false_positive_rate}%</div><div className="text-sm text-slate-400">false positives (cleared of all decided)</div></div></section>)}
