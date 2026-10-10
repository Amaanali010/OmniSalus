"""Dependency-free, paginated PDF report writer (Python standard library)."""
import textwrap

def build_report(snapshot):
    lines = []
    def add(text=''):
        text = str(text).encode('ascii', 'replace').decode('ascii')
        lines.extend(textwrap.wrap(text, width=88, break_long_words=True) or [''])
    def fields(data, prefix=''):
        for key, value in data.items():
            if key in ('badge_class', 'accuracy'):
                continue
            title = key.replace('_', ' ').capitalize()
            if isinstance(value, dict):
                add(prefix + title)
                fields(value, '  ')
            elif isinstance(value, list):
                add(prefix + title + ': ' + ', '.join(map(str, value)))
            else:
                add(prefix + title + ': ' + str(value))
    add(snapshot['model_type'].replace('-', ' ').title() + ' assessment')
    add('Assessment time (UTC): ' + snapshot['created_at'])
    add()
    add('MODEL OUTPUT')
    fields(snapshot['result'])
    add()
    add('SUBMITTED INPUTS')
    fields(snapshot['inputs'])
    add()
    add('These are the exact inputs and model output from the completed assessment.')
    add('Classification confidence describes the predicted category, not disease severity.')
    add('Educational model output only; not a medical diagnosis. Discuss health concerns with a qualified healthcare professional.')
    pages = [lines[i:i+42] for i in range(0, len(lines), 42)]
    objects = [b'', b'', b'<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>', b'<< /Type /Font /Subtype /Type1 /BaseFont /Courier-Bold >>']
    def esc(s):
        return s.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
    page_ids = []
    for index, page in enumerate(pages):
        commands = ['0.03 0.08 0.12 rg 0 758 595 84 re f', 'BT /F2 24 Tf 0.35 0.9 0.75 rg 42 804 Td (OmniSalus) Tj ET', 'BT /F2 10 Tf 1 1 1 rg 42 782 Td (MODEL ASSESSMENT REPORT) Tj ET']
        y = 729
        for line in page:
            commands.append(f'BT /F1 9 Tf 0.12 0.18 0.21 rg 42 {y} Td ({esc(line)}) Tj ET')
            y -= 15
        commands.append(f'BT /F1 8 Tf 0.3 0.4 0.4 rg 42 32 Td (OmniSalus | Educational prototype | Page {index+1} of {len(pages)}) Tj ET')
        stream = '\n'.join(commands).encode('ascii')
        stream_id = len(objects)+1
        objects.append(b'<< /Length '+str(len(stream)).encode()+b' >>\nstream\n'+stream+b'\nendstream')
        page_id = len(objects)+1
        page_ids.append(page_id)
        objects.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents {stream_id} 0 R >>'.encode())
    objects[0] = b'<< /Type /Catalog /Pages 2 0 R >>'
    objects[1] = ('<< /Type /Pages /Kids ['+' '.join(f'{i} 0 R' for i in page_ids)+f'] /Count {len(pages)} >>').encode()
    out = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n'); offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(out)); out.extend(f'{number} 0 obj\n'.encode()+obj+b'\nendobj\n')
    xref = len(out)
    out.extend(f'xref\n0 {len(offsets)}\n0000000000 65535 f \n'.encode())
    for offset in offsets[1:]: out.extend(f'{offset:010d} 00000 n \n'.encode())
    out.extend(f'trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode())
    return bytes(out)
