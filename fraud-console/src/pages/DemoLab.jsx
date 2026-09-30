import {useState} from 'react';import {api,setMock,setOutage,getMode} from '../api';import {usePoll} from '../hooks';
const S=[['impossible_travel','Impossible travel','One customer in two distant cities minutes apart. Expect a HIGH flag and an alert.'],['velocity','Velocity burst','A burst of rapid transactions. Expect a MEDIUM or HIGH flag.'],['normal','Normal traffic','Five ordinary transactions that should not be flagged.']];
export default function DemoLab(){
 const [m,setM]=useState(getMode()),[msg,setMsg]=useState(''),[st]=usePoll(api.stats,3000);
 const run=async(fn,ok)=>{try{setMsg(ok(await fn()))}catch(e){setMsg('Failed: '+e.message)}};
 const T=({k,l})=><label className="flex items-center gap-2 text-sm text-slate-300"><input type="checkbox" checked={m[k]} onChange={e=>{(k==='mock'?setMock:setOutage)(e.target.checked);setM(getMode())}}/>{l}</label>;
 return(<div className="mx-auto max-w-4xl px-6 py-8"><h1 className="text-3xl font-bold">Demo lab</h1><p className="mt-1 text-slate-400">Controls for the live presentation. Only admins see this page.</p>
 <div className="my-6 grid gap-4 md:grid-cols-3">{S.map(([k,t,d])=><div key={k} className="rounded-xl border border-[#1b2440] bg-[#0d1326] p-4"><div className="font-semibold">{t}</div><p className="my-2 text-sm text-slate-400">{d}</p>
 <button onClick={()=>run(()=>api.simulate(k),r=>`${t}: created ${r.created} transactions, ${r.flags} flagged`)} className="rounded-lg border border-red-500/40 bg-red-500/15 px-3 py-1.5 text-sm font-semibold text-red-200 hover:bg-red-500/25">Run scenario</button></div>)}</div>
 <div className="flex flex-wrap items-center gap-6 rounded-xl border border-[#1b2440] bg-[#0d1326] p-4"><button onClick={()=>run(()=>api.reset(),()=>'Demo data reset')} className="rounded-lg border border-[#1b2440] bg-[#101833] px-3 py-1.5 text-sm hover:bg-[#182246]">Reset demo data</button>
 <T k="mock" l="Mock data"/><T k="outage" l="Simulate outage"/></div>
 <div aria-live="polite" className="mt-4 min-h-6 text-sm text-green-300">{msg}</div>
 <div className="mt-4 text-sm text-slate-400">{st?`Live counts: ${st.total_transactions} transactions, ${st.total_flags} flags, ${st.by_status.PENDING} awaiting review`:'Waiting for data…'}</div></div>)}
