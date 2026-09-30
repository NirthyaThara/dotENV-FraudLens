import {useState} from 'react';import {Navigate,useNavigate} from 'react-router-dom';import {useAuth,USERS} from '../auth';
const IN="w-full rounded-lg border border-[#1b2440] bg-[#0a0f1e] px-3 py-2 text-sm";
export default function Login(){
 const {user,login}=useAuth(),nav=useNavigate(),[e,setE]=useState(''),[p,setP]=useState(''),[err,setErr]=useState('');
 if(user)return<Navigate to="/" replace/>;
 const go=(a,b)=>login(a,b)?nav('/'):setErr('Email or password is incorrect. Use one of the demo accounts below.');
 return(<div className="grid min-h-screen place-items-center px-4"><div className="w-full max-w-sm rounded-2xl border border-[#1b2440] bg-[#0d1326] p-8">
 <h1 className="text-2xl font-bold">Fraud review console</h1><p className="mt-1 text-sm text-slate-400">Sign in to review flagged transactions.</p>
 <form onSubmit={ev=>{ev.preventDefault();go(e,p)}} className="mt-6 space-y-3">
 <input className={IN} type="email" value={e} onChange={x=>setE(x.target.value)} placeholder="Email" autoFocus/>
 <input className={IN} type="password" value={p} onChange={x=>setP(x.target.value)} placeholder="Password"/>
 {err&&<div role="alert" className="text-sm text-red-300">{err}</div>}
 <button className="w-full rounded-lg bg-red-500/80 py-2 font-semibold hover:bg-red-500">Sign in</button></form>
 <div className="mt-6 border-t border-[#1b2440] pt-4"><div className="mb-2 text-xs text-slate-400">Demo accounts: one click to sign in</div>
 <div className="flex gap-2">{USERS.map(u=><button key={u.role} onClick={()=>go(u.email,u.password)} className="flex-1 rounded-lg border border-[#1b2440] bg-[#101833] py-1.5 text-sm hover:bg-[#182246]">{u.role}</button>)}</div></div></div></div>)}
