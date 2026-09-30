import {createContext,useContext,useState} from 'react';
export const USERS=[{email:'analyst@fraudlens.dev',password:'demo123',name:'Asha Rao',role:'Analyst'},{email:'admin@fraudlens.dev',password:'admin123',name:'Dev Kumar',role:'Admin'},{email:'viewer@fraudlens.dev',password:'view123',name:'Guest Auditor',role:'Viewer'}];
const Ctx=createContext(null);export const useAuth=()=>useContext(Ctx);
export function AuthProvider({children}){
 const [user,setUser]=useState(()=>{try{return JSON.parse(sessionStorage.getItem('user'))}catch{return null}});
 const login=(email,pw)=>{const u=USERS.find(x=>x.email===email.trim().toLowerCase()&&x.password===pw);if(!u)return false;
  const {password,...s}=u;sessionStorage.setItem('user',JSON.stringify(s));setUser(s);return true};
 const logout=()=>{sessionStorage.removeItem('user');setUser(null)};
 return<Ctx.Provider value={{user,login,logout}}>{children}</Ctx.Provider>}
