import {NavLink,Outlet} from 'react-router-dom';import {useAuth} from '../auth';
export default function Shell(){
 const {user,logout}=useAuth();
 const links=[['/','Review queue'],['/transactions','Transactions'],['/analytics','Analytics'],...(user.role==='Admin'?[['/demo','Demo lab']]:[])];
 return(<div className="flex min-h-screen"><nav className="sticky top-0 flex h-screen w-52 shrink-0 flex-col border-r border-[#1b2440] bg-[#0a0f1e] p-4">
 <div className="mb-6 text-lg font-bold">FraudLens</div>
 <div className="space-y-1">{links.map(([to,l])=><NavLink key={to} to={to} end={to==='/'} className={({isActive})=>`block rounded-lg px-3 py-2 text-sm ${isActive?'bg-[#182246] text-white':'text-slate-400 hover:text-white'}`}>{l}</NavLink>)}</div>
 <div className="mt-auto text-sm"><div className="font-medium">{user.name}</div><div className="text-xs text-slate-400">{user.role}</div>
 <button onClick={logout} className="mt-2 text-slate-400 hover:text-white">Sign out</button></div></nav>
 <main className="min-w-0 flex-1"><Outlet/></main></div>)}
