import {HashRouter,Routes,Route,Navigate} from 'react-router-dom';
import {AuthProvider,useAuth} from './auth';import Shell from './components/Shell';
import Login from './pages/Login';import ReviewQueue from './pages/ReviewQueue';import Transactions from './pages/Transactions';
import Analytics from './pages/AnalyticsPage';import Customer from './pages/Customer';import DemoLab from './pages/DemoLab';
const Guard=()=>useAuth().user?<Shell/>:<Navigate to="/login" replace/>;
const Admin=({children})=>useAuth().user.role==='Admin'?children:<Navigate to="/" replace/>;
const NotFound=()=><div className="p-16 text-center"><h1 className="text-2xl font-bold">Page not found</h1><a href="#/" className="mt-3 inline-block text-slate-400 underline">Back to the review queue</a></div>;
export default function App(){return(<HashRouter><AuthProvider><Routes>
 <Route path="/login" element={<Login/>}/>
 <Route element={<Guard/>}><Route index element={<ReviewQueue/>}/><Route path="transactions" element={<Transactions/>}/>
  <Route path="analytics" element={<Analytics/>}/><Route path="customers/:userId" element={<Customer/>}/>
  <Route path="demo" element={<Admin><DemoLab/></Admin>}/><Route path="*" element={<NotFound/>}/></Route>
 </Routes></AuthProvider></HashRouter>)}
