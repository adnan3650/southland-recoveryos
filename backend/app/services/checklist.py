"""Portable snapshots of the saved checklist; no external account access required."""
from io import BytesIO
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

from .rules import prioritized_plan


def checklist_lines(case, resources):
    sources = {r['id']: r for r in resources}
    lines = [
        'Recovery checklist',
        f"{case['resident_name']} | {case['municipality']} | Incident: {case['incident_date']}",
        'Synthetic demonstration case. Snapshot of saved tasks; edits outside the app do not sync back.',
        'Target dates are personal goals, not agency deadlines. This checklist does not determine safety, coverage or eligibility.',
        '',
    ]
    for task in prioritized_plan(case, resources):
        status = 'Completed' if task['status'] == 'done' else 'To do'
        lines.append(f"[{status}] {task['title']}")
        lines.append(f"Priority: {task['priority']}")
        if task.get('explanation'):
            lines.append(task['explanation'])
        if task.get('due_date'):
            lines.append(f"My target date: {task['due_date']} (not an agency deadline)")
        source = sources.get(task.get('source_id'))
        if source:
            lines.append(f"Source: {source['name']} — {source['source_url']}")
        lines.append('')
    if not case['tasks']:
        lines.append('No saved tasks yet.')
    return lines


def checklist_docx(lines):
    # Minimal Office Open XML package, with text escaped rather than interpreted as markup.
    paragraphs = []
    for index, line in enumerate(lines):
        style = '<w:pPr><w:pStyle w:val="Title"/></w:pPr>' if index == 0 else ''
        paragraphs.append(f'<w:p>{style}<w:r><w:t xml:space="preserve">{escape(line)}</w:t></w:r></w:p>')
    document = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
                + ''.join(paragraphs)
                + '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1080" w:right="1080" w:bottom="1080" w:left="1080"/></w:sectPr></w:body></w:document>')
    output = BytesIO()
    with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
        archive.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>')
        archive.writestr('_rels/.rels', '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        archive.writestr('word/document.xml', document)
        archive.writestr('word/_rels/document.xml.rels', '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
        archive.writestr('word/styles.xml', '<?xml version="1.0"?><w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/></w:rPr></w:rPrDefault></w:docDefaults><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style><w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:rPr><w:b/><w:sz w:val="36"/></w:rPr></w:style></w:styles>')
    return output.getvalue()
