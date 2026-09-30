import {useEffect,useRef,useState,useCallback,useMemo} from 'react';
import {api,setMock,setOutage,getMode} from '../api';import {label,beep} from '../util';import {useAuth} from '../auth';
import Header from '../components/Header';import Analytics from '../components/Analytics';import DemoPanel from '../components/DemoPanel';
import FlagTable from '../components/FlagTable';import DetailDrawer from '../components/DetailDrawer';
const TABS=[['ALL','All'],['PENDING','Flagged'],['REVIEWED','Reviewed'],['CLEARED','Cleared']];
export default function ReviewQueue(){
 const {user}=useAuth();
 const [flags,setFlags]=useState([]),[stats,setStats]=useState(null),[err,setErr]=useState(''),[upd,setUpd]=useState(null);
 const [tab,setTab]=useState('ALL'),[lvl,setLvl]=useState('ALL'),[q,setQ]=useState('');
 const [sel,setSel]=useState(null),[chk,setChk]=useState(new Set()),[fresh,setFresh]=useState(new Set()),[toasts,setToasts]=useState([]);
 const [mock,setM]=useState(getMode().mock),[out,setO]=useState(getMode().outage),[snd,setSnd]=useState(true);
 const seen=useRef(null),sndR=useRef(snd);sndR.current=snd;
 const toast=(m,bad)=>{const id=Math.random();setToasts(t=>[...t,{id,m,bad}]);setTimeout(()=>setToasts(t=>t.filter(x=>x.id!==id)),3000)};
 const load=useCallback(async()=>{try{
  const [f,s]=await Promise.all([api.flags(),api.stats()]);
  if(seen.current){const nw=f.items.filter(x=>!seen.current.has(x.id));
   if(nw.length){setFresh(new Set(nw.map(x=>x.id)));setTimeout(()=>setFresh(new Set()),2500);if(nw.some(x=>x.risk_level==='HIGH')&&sndR.current)beep()}}
  seen.current=new Set(f.items.map(x=>x.id));setFlags(f.items);setStats(s);setErr('');setUpd(new Date());
 }catch(e){setErr(e.message)}},[]);
 useEffect(()=>{load();const t=setInterval(load,3000);return()=>clearInterval(t)},[load]);
 useEffect(()=>{document.title=`(${stats?.by_status?.PENDING??0}) Fraud console`},[stats]);
 const act=async(id,a,comment)=>{if(user.role==='Viewer')return toast('Viewer accounts are read-only',true);const st=a==='review'?'REVIEWED':'CLEARED',prev=flags;
  setFlags(fs=>fs.map(f=>f.id===id?{...f,review_status:st}:f));
  try{await api.act(id,a,comment);toast(`${label[st]} flag #${id}`);load()}catch(e){setFlags(prev);toast(`Could not update flag #${id}: ${e.message}`,true)}};
 const bulk=a=>{flags.filter(f=>chk.has(f.id)&&f.review_status==='PENDING').forEach(f=>act(f.id,a));setChk(new Set())};
 const run=async fn=>{try{const r=await fn();toast(r.flags!=null?`Created ${r.created} transactions, ${r.flags} flagged`:'Demo reset');seen.current=fn.name==='reset'?null:seen.current;load()}catch(e){toast(e.message,true)}};
 const switchMode=(k,v)=>{k==='mock'?(setMock(v),setM(v)):(setOutage(v),setO(v));if(k==='mock'){seen.current=null;setSel(null)}load()};
 const rows=useMemo(()=>flags.filter(f=>(tab==='ALL'||f.review_status===tab)&&(lvl==='ALL'||f.risk_level===lvl)&&
  (!q||`${f.transaction.user_id} ${f.transaction.merchant} TX-${f.transaction.id}`.toLowerCase().includes(q.toLowerCase()))),[flags,tab,lvl,q]);
 const cur=flags.find(f=>f.id===sel);
 useEffect(()=>{const h=e=>{if(/INPUT|TEXTAREA|SELECT/.test(e.target.tagName))return;const i=rows.findIndex(f=>f.id===sel),k=e.key.toLowerCase();
  if(k==='j')setSel(rows[Math.min(i+1,rows.length-1)]?.id??null);else if(k==='k')setSel(rows[Math.max(i-1,0)]?.id??null);
  else if(k==='escape')setSel(null);else if((k==='r'||k==='c')&&cur?.review_status==='PENDING'){act(cur.id,k==='r'?'review':'clear');setSel(null)}};
  window.addEventListener('keydown',h);return()=>window.removeEventListener('keydown',h)});
 const cnt=k=>k==='ALL'?stats?.total_flags:stats?.by_status?.[k];
 return(<div className="mx-auto max-w-[1400px] px-6 pb-16">
 {err&&<div className="mt-4 rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-2 text-sm text-red-200">Backend offline: {err}. Retrying every 3 seconds. Switch on “Mock data” to keep demoing.</div>}
 <Header stats={stats} flags={flags}/><Analytics stats={stats}/>
 <div className="mt-8 flex flex-wrap items-center justify-between gap-4">
  <div className="flex flex-wrap items-center gap-1">{TABS.map(([k,l])=><button key={k} onClick={()=>setTab(k)} className={`rounded-lg px-4 py-2 text-sm ${tab===k?'bg-[#182246] text-white':'text-slate-400 hover:text-white'}`}>{l} <span className="ml-1 rounded-full bg-[#1b2440] px-2 py-0.5 text-xs">{cnt(k)??0}</span></button>)}
   <select value={lvl} onChange={e=>setLvl(e.target.value)} aria-label="Risk level" className="ml-3 rounded-lg border border-[#1b2440] bg-[#0d1326] px-2 py-2 text-sm">{['ALL','HIGH','MEDIUM','LOW'].map(v=><option key={v} value={v}>{v==='ALL'?'All risk levels':v}</option>)}</select>
   <input value={q} onChange={e=>setQ(e.target.value)} placeholder="Search user, merchant, TX" className="rounded-lg border border-[#1b2440] bg-[#0d1326] px-3 py-2 text-sm"/></div>
  <DemoPanel sim={s=>run(()=>api.simulate(s))} reset={()=>run(function reset(){return api.reset()})} mock={mock} setMock={v=>switchMode('mock',v)} out={out} setOut={v=>switchMode('out',v)} snd={snd} setSnd={setSnd}/></div>
 {chk.size>0&&<div className="mt-3 flex items-center gap-3 rounded-lg bg-[#101833] px-4 py-2 text-sm"><b>{chk.size} selected</b>
  <button onClick={()=>bulk('review')} className="rounded border border-[#1b2440] px-3 py-1 hover:bg-[#182246]">Review all</button>
  <button onClick={()=>bulk('clear')} className="rounded border border-green-500/30 px-3 py-1 text-green-300 hover:bg-green-500/10">Clear all</button>
  <button onClick={()=>setChk(new Set())} className="text-slate-400">Deselect</button></div>}
 <div className="mt-3"><FlagTable rows={rows} fresh={fresh} chk={chk} setChk={setChk} sel={sel} open={setSel} act={act}/></div>
 <div className="mt-3 text-xs text-slate-500">{upd?`Last updated ${upd.toLocaleTimeString()}`:'Loading…'} · {mock?'mock data':'live API'}</div>
 <DetailDrawer key={sel} flag={cur} onClose={()=>setSel(null)} act={act}/>
 <div className="fixed bottom-4 right-4 z-30 space-y-2" aria-live="polite">{toasts.map(t=><div key={t.id} className={`rounded-lg border px-4 py-2 text-sm shadow-lg ${t.bad?'border-red-500/40 bg-red-950 text-red-200':'border-green-500/30 bg-[#0d1f18] text-green-200'}`}>{t.m}</div>)}</div></div>)}
