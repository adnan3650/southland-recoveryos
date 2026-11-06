export interface Resource {
    id: string;
    name: string;
    category: string;
    description: string;
    geographic_coverage: string[];
    eligibility: string[];
    contact: string;
    source_url: string;
    verified_at: string | null;
    verification: string;
    availability: string;
    limitations: string;
    needs: string[];
    program: boolean;
    match_status?: string;
    reasons?: string[];
    missing_requirements?: string[];
}
export interface Task {
    id: string;
    title: string;
    explanation: string;
    priority: 'urgent' | 'high' | 'normal';
    status: 'todo' | 'done';
    due_date?: string | null;
    source_id?: string;
}
export interface Damage {
    id: string;
    item: string;
    area: string;
    observation: string;
    provenance: string;
    uncertainty: string;
    evidence_ids: string[];
}
export interface Analysis {
    summary: string;
    observations: Damage[];
    missing_details: string[];
    uncertainties: string[];
    policy: {
        policy_identifier: string;
        coverage_wording: string[];
        exclusions: string[];
        deductible_wording: string;
        insurer_questions: string[];
    };
}
export interface Document {
    id: string;
    name: string;
    category: string;
    media_type: string;
    size: number;
    created_at: string;
    analysis: null | {
        result: Analysis;
        usage: Usage;
    };
}
export interface Usage {
    input_tokens: number;
    output_tokens: number;
    latency_ms: number;
    model: string;
    at: string;
}
export interface Conversation {
    id: string;
    question: string;
    answer: string;
    resource_ids: string[];
    uncertainties: string[];
    usage: Usage;
}
export interface CaseData {
    id: string;
    resident_name: string;
    municipality: string;
    zip_code: string;
    disaster_type: string;
    incident_date: string;
    description: string;
    property_situation: string;
    displaced: boolean;
    immediate_needs: string[];
    created_at: string;
    updated_at: string;
    documents: Document[];
    damage_items: Damage[];
    tasks: Task[];
    insurance: Record<string, string>;
    contacts: {
        id: string;
        organization: string;
        contacted_on: string;
        notes: string;
    }[];
    conversations: Conversation[];
    reports: {
        id: string;
        created_at: string;
    }[];
    ai_plan: null | {
        result: {
            steps: {
                title: string;
                explanation: string;
                priority: string;
                required_information: string[];
                responsible_party: string;
                resource_ids: string[];
                status: string;
            }[];
            uncertainties: string[];
        };
        usage: Usage;
    };
}
export interface Readiness {
    percent: number;
    meaning: string;
    checks: {
        id: string;
        title: string;
        complete: boolean;
        next_step: string;
    }[];
}
export interface Health {
    status: string;
    mode: string;
    ai_configured: boolean;
    model: string;
    synthetic_only: boolean;
}
export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
    const headers = new Headers(init.headers);
    if (init.body && !(init.body instanceof FormData))
        headers.set('Content-Type', 'application/json');
    const response = await fetch('/api' + path, { ...init, headers, credentials: 'same-origin' });
    if (!response.ok) {
        let message = 'The request could not be completed.';
        try {
            const body = await response.json();
            message = body.error?.message || message;
            if (body.error?.fields)
                message += ': ' + body.error.fields.map((f: {
                    field: string;
                    message: string;
                }) => f.field + ' ' + f.message).join('; ');
        }
        catch { }
        throw new Error(message);
    }
    return response.json();
}
export const json = (body: unknown, method = 'POST') => ({ method, body: JSON.stringify(body) });
export async function downloadReport(caseId: string) {
    const response = await fetch('/api/cases/' + caseId + '/report', { method: 'POST', credentials: 'same-origin' });
    if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error?.message || 'Report generation failed');
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'southland-recovery-packet.pdf';
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
}
export function displayDate(value: string) { return new Date(value.length === 10 ? value + 'T12:00:00' : value).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }); }
export function today() { return new Date().toLocaleDateString('en-CA', { timeZone: 'America/Chicago' }); }
