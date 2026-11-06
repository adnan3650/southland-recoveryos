import {useEffect,useState} from 'react'
import {Link} from 'react-router-dom'
import {ArrowRight, CheckCircle2, CloudRain, FileText, Sparkles} from 'lucide-react'
import {api,json,type CaseData,type Health,type Document} from '../lib/api'
import {Badge,Notice,PageHeading} from '../components/ui'

const STORAGE_KEY='southland_judge_demo_case'
const scenario={resident_name:'Alex Morgan',municipality:'South Holland',zip_code:'60473',disaster_type:'flood',incident_date:'2026-09-12',description:'FICTIONAL JUDGE DEMONSTRATION. Basement flooding affected a sofa and cardboard storage boxes. Alex is temporarily staying with family and needs food assistance. The incident, resident, insurance excerpt, estimate and image are synthetic; no actual September 2026 storm is asserted.',property_situation:'owner',displaced:true,immediate_needs:['food','shelter']}
const beats=[
 {path:'',title:'1. A clear next step',time:'0:00–0:30',say:'Meet Alex, a fictional South Holland resident. After basement flooding, Alex needs one place to organize evidence, find support and decide what to do next.',show:'Show the safety and essentials tasks. The case is saved, and the next steps reflect Alex’s situation.'},
 {path:'evidence',title:'2. Evidence with a source',time:'0:30–1:20',say:'Here are Alex’s synthetic damage image, policy excerpt and estimate. Resident observations are labeled. With consent, Claude can interpret this evidence and retain its reference and uncertainty.',show:'Show the image and resident inventory. If live Claude is configured and verified, analyze the image or policy, then review the saved result.'},
 {path:'resources',title:'3. Local support',time:'1:20–1:50',say:'Alex needs shelter and food referrals. The workspace links to 211, the Red Cross and local food resources, with source dates and availability limits.',show:'Point to the original sources. Do not describe a referral directory as confirmed shelter capacity.'},
 {path:'insurance',title:'4. Readiness that changes',time:'1:50–2:30',say:'The readiness engine identifies missing documentation. Alex has not recorded an insurer conversation yet. I’ll save a fictional contact note and show the checklist update.',show:'Log organization “Synthetic Insurer”, date “2026-11-06”, notes “Fictional rehearsal: requested full policy and evidence checklist.” The documentation score moves from 80% to 100%; this never determines coverage.'},
 {path:'programs',title:'5. Prerequisites, clearly stated',time:'2:30–3:00',say:'The local prevention rebate may be worth exploring, but Alex still needs Village confirmation and pre-approval. Federal assistance requires an applicable declaration; we have not verified one for this fictional incident.',show:'Show missing prerequisites and preliminary statuses. Nothing is submitted and no approval is promised.'},
 {path:'assistant',title:'6. Contextual Claude guidance',time:'3:00–3:40',say:'When live Claude is available, Alex can ask what to do next using the saved case, evidence gaps and official references. Suggestions remain distinct from agency decisions.',show:'With live acceptance passed: check consent and ask “What should Alex do next, and which documents still need verification? Cite the supplied official sources.” If no key is configured, explicitly skip live inference.'},
 {path:'report',title:'7. Leave with something useful',time:'3:40–4:10',say:'Alex can download an organized recovery packet for a conversation with an insurer or support worker, then resume the saved case. Our next step is community validation before a real resident pilot.',show:'Download the actual PDF. Show case summary, evidence register, readiness, sources and outstanding prerequisites.'}
]

export default function JudgeDemo(){
 const [health,setHealth]=useState<Health|null>(null)
 const [caseId,setCaseId]=useState<string|null>(null)
 const [busy,setBusy]=useState(false)
 const [error,setError]=useState('')
 const [status,setStatus]=useState('')
 useEffect(()=>{api<Health>('/health').then(setHealth).catch(e=>setError(e.message));const id=localStorage.getItem(STORAGE_KEY);if(id)api<CaseData>('/cases/'+id).then(()=>setCaseId(id)).catch(()=>localStorage.removeItem(STORAGE_KEY))},[])
 async function prepare(){
  setBusy(true);setError('');setStatus('Creating a fictional case through the application API…')
  try{
   if(!health?.synthetic_only)throw new Error('The judge fixture is only available in local synthetic mode.')
   let c=caseId?await api<CaseData>('/cases/'+caseId):await api<CaseData>('/cases',json(scenario))
   setCaseId(c.id);localStorage.setItem(STORAGE_KEY,c.id)
   const files=[['synthetic-basement-demo.png','damage'],['synthetic-policy.txt','policy'],['synthetic-estimate.txt','estimate']]
   for(const [name,category] of files){
    if(c.documents.some(d=>d.name===name))continue
    setStatus('Saving labeled demonstration evidence: '+name)
    const source=await fetch('/demo-assets/'+name)
    if(!source.ok)throw new Error('Demo asset is unavailable: '+name)
    const body=new FormData();body.append('file',new File([await source.blob()],name));body.append('category',category)
    await api<Document>('/cases/'+c.id+'/documents',{method:'POST',body})
   }
   for(const item of [{item:'Basement sofa',area:'Finished basement',observation:'Synthetic scenario: damp upholstery and staining near the bottom. Resident-provided demonstration observation; no safety or price assessment.'},{item:'Cardboard storage boxes',area:'Basement storage area',observation:'Synthetic scenario: damp, deformed cardboard boxes. Contents and extent of damage require resident verification.'}]){
    if(!c.damage_items.some(d=>d.item===item.item))await api('/cases/'+c.id+'/damage',json(item))
   }
   if(!c.insurance.insurer)await api('/cases/'+c.id+'/insurance',json({insurer:'Synthetic Insurer',policy_number:'DEMO-SOUTHLAND-001',claim_number:'',notes:'Fictional rehearsal only. Full policy, insurer review and reporting requirements still need verification.'},'PUT'))
   setStatus('Demo case prepared. No AI responses were generated. Open the workspace and follow the speaking cues below.')
  }catch(e){setError((e as Error).message);setStatus('Preparation did not finish. Your saved case is preserved; retry to add only missing fixtures.')}
  finally{setBusy(false)}
 }
 return <div className="content-width page-pad judge-demo"><PageHeading eyebrow="JUDGE DEMONSTRATION" title="One resident. One connected recovery journey." description="A four-minute rehearsal with a fictional South Holland resident. These timings are a suggested format, not confirmed competition rules."/>
 <div className="demo-start-grid"><section className="panel"><div className="row"><span className="icon-bubble"><CloudRain/></span><Badge tone="green">Fictional scenario</Badge></div><h2>Meet Alex Morgan.</h2><p>South Holland · September 12, 2026 · Homeowner</p><p>Basement flooding, damaged belongings, temporary displacement and a need for food referrals. All evidence and personal details are synthetic.</p><button className="button" disabled={busy||!health?.synthetic_only} onClick={prepare}>{busy?'Preparing case…':caseId?'Check and finish demo setup':'Prepare judge demo case'}<ArrowRight size={16}/></button>{status&&<p role="status" className="demo-status">{status}</p>}{caseId&&<Link className="text-link demo-open" to={'/case/'+caseId}>Open Alex’s workspace <ArrowRight size={16}/></Link>}</section>
 <aside className="panel"><p className="eyebrow">BEFORE YOU PRESENT</p><h2>Show what actually runs.</h2><Badge tone={health?.ai_configured?'green':'amber'}>{health?.ai_configured?'Claude key configured — live quality still requires acceptance':'Live Claude awaits API key'}</Badge><p className="demo-status">The prepared case contains real saved records and labeled synthetic evidence. It contains no simulated Claude answers.</p><p>A fresh demo starts with 80% documentation readiness. Log a matching insurer contact to demonstrate 100%. Neither number means safety, coverage or eligibility.</p><a className="text-link" href="/demo-assets/synthetic-policy.txt" download>Sample policy excerpt <FileText size={15}/></a></aside></div>
 {error&&<div role="alert"><Notice tone="error">{error}</Notice></div>}
 <Notice>For immediate danger, call 911. This prototype does not submit applications, determine coverage or confirm live shelter availability. Keep presentation data fictional.</Notice>
 <div className="demo-opening"><p className="eyebrow">YOUR OPENING</p><blockquote>“A disaster doesn’t end when the floodwater disappears. That’s when residents face scattered evidence, insurance questions and disconnected assistance websites. Southland RecoveryOS helps them take the next step.”</blockquote></div>
 <h2 className="demo-script-title">Your click-by-click speaking cues</h2><div className="demo-beats">{beats.map(beat=><article className="panel" key={beat.title}><div className="row"><h3>{beat.title}</h3><Badge>{beat.time}</Badge></div><p className="demo-say">“{beat.say}”</p><p className="demo-show"><strong>On screen:</strong> {beat.show}</p>{caseId?<Link className="text-link" to={'/case/'+caseId+(beat.path?'/'+beat.path:'')}>Open this step <ArrowRight size={15}/></Link>:<small>Prepare the case above to open this step.</small>}</article>)}</div>
 <div className="demo-close panel"><CheckCircle2/><div><h2>Your closing line</h2><p>“Our goal is a resident who leaves with organized evidence, clear questions and a useful recovery packet. We’re ready to validate this workflow with community partners.”</p></div></div><p className="fine-print"><Sparkles size={13}/> AI-generated demonstration image; not a real property or disaster. If live Claude is unavailable, present the verified local workflow and state that live AI acceptance is pending.</p></div>
}
