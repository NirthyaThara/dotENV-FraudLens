import RiskGauge from './RiskGauge';import {money} from '../util';
const S=({v,l,c})=>(<div><div className="text-3xl font-bold" style={{color:c}}>{v}</div><div className="text-sm text-slate-400">{l}</div></div>);
export default function Header({stats,flags}){
 const pend=flags.filter(f=>f.review_status==='PENDING'),held=pend.reduce((s,f)=>s+f.transaction.amount,0);
 const avg=pend.length?Math.round(pend.reduce((s,f)=>s+f.risk_score,0)/pend.length):0,b=stats?.by_status||{};
 return(<header className="flex flex-wrap items-center justify-between gap-6 pt-6">
 <div><h1 className="text-4xl font-bold tracking-tight">Fraud review console</h1><p className="mt-2 text-slate-400">The engine flags. You decide.</p></div>
 <div className="flex flex-wrap items-center gap-8"><S v={b.PENDING??0} l="awaiting review" c="#ef4444"/><S v={money(held)} l="held in flagged"/>
 <S v={b.REVIEWED??0} l="reviewed" c="#f59e0b"/><S v={b.CLEARED??0} l="cleared" c="#22c55e"/>
 <div title={pend.length?`Average risk score of the ${pend.length} flags awaiting review`:'No flags awaiting review'}><RiskGauge score={avg} size={170} caption="SYSTEM THREAT LEVEL"/></div></div></header>)}
