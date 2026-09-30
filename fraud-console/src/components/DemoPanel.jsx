const B="rounded-lg border border-[#1b2440] bg-[#101833] px-3 py-1.5 text-sm hover:bg-[#182246]";
export default function DemoPanel({sim,reset,mock,setMock,out,setOut,snd,setSnd}){
 const T=({v,s,l})=><label className="flex items-center gap-1.5 text-sm text-slate-400"><input type="checkbox" checked={v} onChange={e=>s(e.target.checked)}/>{l}</label>;
 return(<div className="flex flex-wrap items-center gap-3">
 <button onClick={()=>sim('impossible_travel')} className="rounded-lg border border-red-500/40 bg-red-500/15 px-3 py-1.5 text-sm font-semibold text-red-200 hover:bg-red-500/25">Simulate fraud</button>
 <button onClick={()=>sim('velocity')} className={B}>Velocity burst</button><button onClick={()=>sim('normal')} className={B}>Normal traffic</button>
 <button onClick={reset} className={B}>Reset demo</button>
 <T v={mock} s={setMock} l="Mock data"/><T v={out} s={setOut} l="Simulate outage"/><T v={snd} s={setSnd} l="Sound"/></div>)}
