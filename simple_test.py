import urllib.request
import re

url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSsNCEFZvBR3UjBwTbyaPPz-B1SKw17I7Jb72XWweS1y75HmzXfgdFJ1TpZX6_S06m9_phJTy5XnCI6/pub?gid=36065074&single=true&output=tsv'

print('=== TESTE DE EXTRAÇÃO DE NOME ===')

# Testar filename via headers
try:
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0')
    
    with urllib.request.urlopen(req, timeout=10) as response:
        disposition = response.headers.get('Content-Disposition', '')
        print(f'Content-Disposition: {disposition}')
        
        if disposition:
            match = re.search(r'filename[^;=\n]*=(([^;]*))', disposition)
            if match:
                filename = match.group(1).strip('"\'')
                print(f'Filename: {filename}')
                if filename.endswith('.tsv'):
                    filename = filename[:-4]
                print(f'Nome limpo: {filename}')
        
        # Testar primeira linha
        content = response.read().decode('utf-8')
        lines = content.split('\n')
        if lines:
            first_line = lines[0]
            first_cell = first_line.split('\t')[0] if '\t' in first_line else first_line
            print(f'Primeira célula: {first_cell}')
            
            # Verificar se parece um título
            if len(first_cell) > 3 and len(first_cell) < 100 and not first_cell.isdigit():
                print(f'✅ Primeira célula pode ser um título: {first_cell}')
        
except Exception as e:
    print(f'Erro: {e}')
