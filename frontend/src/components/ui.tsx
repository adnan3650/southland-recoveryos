import { ArrowUpRight, Check, Circle, LoaderCircle, ShieldCheck, AlertCircle } from 'lucide-react';
import type { Resource } from '../lib/api';
import { displayDate } from '../lib/api';
import type { ReactNode } from 'react';
export function Badge({ children, tone = 'muted' }: {
    children: ReactNode;
    tone?: string;
}) { return <span className={'badge ' + tone}>{children}</span>; }
export function Notice({ children, tone = 'info' }: {
    children: ReactNode;
    tone?: string;
}) { return <div className={'notice ' + tone}><AlertCircle size={19}/><div>{children}</div></div>; }
export function Empty({ title, children }: {
    title: string;
    children: ReactNode;
}) { return <div className="empty"><span className="empty-icon"><Circle size={23}/></span><h3>{title}</h3><p>{children}</p></div>; }
export function Loading() { return <div className="loading" role="status"><LoaderCircle className="spin"/> Opening your workspace…</div>; }
export function PageHeading({ eyebrow, title, description, action }: {
    eyebrow: string;
    title: string;
    description: string;
    action?: ReactNode;
}) { return <div className="page-heading"><div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p>{description}</p></div>{action}</div>; }
export function SectionTitle({ title, children }: {
    title: string;
    children?: ReactNode;
}) { return <div className="section-title"><h2>{title}</h2>{children}</div>; }
export function SourceCard({ resource: r }: {
    resource: Resource;
}) { return <article className="resource-card"><div className="resource-top"><span className="source-icon"><ShieldCheck size={21}/></span><Badge tone={r.verified_at ? 'green' : 'amber'}>{r.verified_at ? 'Source reviewed' : 'Reference · unverified'}</Badge></div><p className="eyebrow">{r.category.replace('_', ' ')} · {r.geographic_coverage.join(', ')}</p><h3>{r.name}</h3><p>{r.description}</p><div className="contact-line">{r.contact}</div><div className="resource-detail"><strong>Before you go</strong><p>{r.limitations}</p><small>{r.verified_at ? 'Page checked ' + displayDate(r.verified_at) : 'Page content could not be verified'}. Capacity and current availability are not verified.</small></div><a className="text-link" href={r.source_url} target="_blank" rel="noreferrer">Visit official source <ArrowUpRight size={16}/></a></article>; }
export function CheckMark({ complete }: {
    complete: boolean;
}) { return <span className={'check-mark ' + (complete ? 'complete' : '')}>{complete ? <Check size={14}/> : <span />}</span>; }
