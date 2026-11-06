from io import BytesIO
from xml.etree import ElementTree
from zipfile import ZipFile

from fastapi.testclient import TestClient


def test_checklist_snapshot_and_ownership(client, app, case):
    base = '/api/cases/' + case['id']
    task = client.post(base + '/tasks', json={
        'title': 'Review <policy> & receipts', 'explanation': 'Keep café notes',
        'priority': 'high', 'due_date': '2026-11-10',
    }).json()
    client.patch(base + '/tasks/' + task['id'], json={'status': 'done'})
    text = client.get(base + '/checklist').text
    assert '[Completed] Review <policy> & receipts' in text
    assert '2026-11-10 (not an agency deadline)' in text
    assert 'Keep café notes' in text
    result = client.get(base + '/checklist?format=docx')
    assert result.status_code == 200
    assert result.headers['cache-control'] == 'no-store'
    with ZipFile(BytesIO(result.content)) as archive:
        for name in archive.namelist():
            ElementTree.fromstring(archive.read(name))
        root = ElementTree.fromstring(archive.read('word/document.xml'))
        paragraphs = [''.join(p.itertext()) for p in root.findall('.//{*}p')]
        assert '[Completed] Review <policy> & receipts' in paragraphs
        assert 'Keep café notes' in paragraphs
    assert client.get(base + '/checklist?format=html').status_code == 422
    with TestClient(app) as other:
        assert other.get(base + '/checklist?format=docx').status_code == 404
        assert other.get(base + '/checklist').status_code == 404
