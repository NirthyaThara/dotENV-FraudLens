import {useEffect,useState} from 'react';import {api} from './api';
export function usePoll(fn,ms=4000,deps=[]){const [d,setD]=useState(null),[err,setErr]=useState('');
 useEffect(()=>{let on=true;const run=()=>fn().then(r=>{if(on){setD(r);setErr('')}}).catch(e=>on&&setErr(e.message));run();const t=setInterval(run,ms);return()=>{on=false;clearInterval(t)}},deps);
 return[d,err]}
export const loadBoth=uid=>Promise.all([api.transactions(uid),api.flags()]).then(([t,f])=>({tx:t.items,flags:f.items}));
