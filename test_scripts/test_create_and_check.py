import requests
from bs4 import BeautifulSoup

# base URL
base = 'http://127.0.0.1:5000'
s = requests.Session()
# Login as admin
login = s.post(base + '/admin/login', data={'username':'admin','password':'admin123'})
print('login status', login.status_code)
# Create encuesta
create_data = {
    'titulo':'Encuesta prueba automatizada',
    'descripcion':'Creada por script de prueba',
    'recolectar_ubicacion':'on',
    'pregunta_texto[]':'Pregunta 1',
    'pregunta_tipo[]':'texto',
    'pregunta_opciones[]':''
}
create = s.post(base + '/admin/encuesta/crear', data=create_data, allow_redirects=True)
print('create status', create.status_code)
# Check user index for the survey
idx = s.get(base + '/')
soup = BeautifulSoup(idx.text, 'html.parser')
found = 'Encuesta prueba automatizada' in idx.text
print('found on index:', found)
# If found, print a snippet
if found:
    print(idx.text.split('Encuesta prueba automatizada')[0][-200:])
