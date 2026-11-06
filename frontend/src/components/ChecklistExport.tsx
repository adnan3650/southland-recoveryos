import { useState } from 'react';

export default function ChecklistExport({ caseId }: { caseId: string }) {
  const [message, setMessage] = useState('');
  const [fallback, setFallback] = useState('');
  const [busy, setBusy] = useState(false);
  async function exportChecklist(format: 'txt' | 'docx', copy = false) {
    setBusy(true); setMessage(''); setFallback('');
    try {
      const response = await fetch(`/api/cases/${caseId}/checklist?format=${format}`, { credentials: 'same-origin' });
      if (!response.ok) throw new Error('Could not export the checklist. Please try again.');
      if (copy) {
        const text = await response.text();
        try {
          await navigator.clipboard.writeText(text);
          setMessage('Checklist copied. Paste it into Google Docs, Word or Notes.');
        } catch {
          setFallback(text);
          setMessage('Select and copy the text below, then paste it into your document app.');
        }
      } else {
        const url = URL.createObjectURL(await response.blob());
        const link = document.createElement('a');
        link.href = url; link.download = `southland-recovery-checklist.${format}`;
        document.body.appendChild(link); link.click(); link.remove();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
        setMessage('Checklist downloaded. Review it before sharing.');
      }
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Export failed. Please retry.'); }
    finally { setBusy(false); }
  }
  return <div className="panel" style={{ marginBottom: '1rem' }}>
    <strong>Take your checklist with you</strong>
    <p>Download for Word or upload the Word file to Google Docs. Copy the text to paste into Notes or another document app.</p>
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
      <button className="button outline small" disabled={busy} onClick={() => exportChecklist('docx')}>Download Word checklist</button>
      <button className="button outline small" disabled={busy} onClick={() => exportChecklist('txt', true)}>Copy checklist</button>
      <button className="text-link" disabled={busy} onClick={() => exportChecklist('txt')}>Download text</button>
    </div>
    <p className="fine-print">Includes saved tasks and their statuses. This is a snapshot; changes in another app do not update this case. Review personal details before sharing.</p>
    {message && <p role="status">{message}</p>}
    {fallback && <label>Checklist text<textarea readOnly rows={10} value={fallback} onFocus={event => event.currentTarget.select()}/></label>}
  </div>;
}
