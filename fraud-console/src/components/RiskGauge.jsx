import {col,lvlName} from '../util';
export default function RiskGauge({score=0,size=220,caption}){
 const c=Math.PI*80,p=Math.min(Math.max(score,0),100)/100,k=col(score);
 return(<div style={{width:size}} className="text-center"><svg viewBox="0 0 200 122" width={size} role="img" aria-label={`Risk ${score} of 100`}>
 <path d="M20 100 A80 80 0 0 1 180 100" fill="none" stroke="#1b2440" strokeWidth="16" strokeLinecap="round"/>
 <path d="M20 100 A80 80 0 0 1 180 100" fill="none" stroke={k} strokeWidth="16" strokeLinecap="round" strokeDasharray={c} strokeDashoffset={c*(1-p)} style={{transition:'stroke-dashoffset .8s ease,stroke .4s'}}/>
 <text x="100" y="92" textAnchor="middle" fontSize="36" fontWeight="700" fill="#f9fafb">{score}</text>
 <text x="100" y="114" textAnchor="middle" fontSize="10" fill={k} letterSpacing="1.5">{caption||lvlName(score)}</text></svg></div>)}
