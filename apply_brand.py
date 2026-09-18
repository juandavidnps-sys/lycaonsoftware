import os

for r, d, files in os.walk('.'):
    if '.git' in r: continue
    for f in files:
        if f.endswith(('.html', '.py')):
            path = os.path.join(r, f)
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
                if 'Lycaon Security' in content:
                    content = content.replace('Lycaon Security', 'Lycaon Security')
                    with open(path, 'w', encoding='utf-8') as file:
                        file.write(content)
            except Exception as e:
                print(f"Error {path}: {e}")

# Add the slogan to index.html
with open('templates/index.html', 'r', encoding='utf-8') as f:
    index = f.read()

old_subtitle = "Firewalls, auditorías de penetración, tokens de autenticación, software de encriptación y monitoreo continuo para proteger su infraestructura."
new_subtitle = "Más que un servicio, una alianza por tu tranquilidad.<br>Firewalls, auditorías de penetración, tokens de autenticación, software de encriptación y monitoreo continuo para proteger su infraestructura."

if old_subtitle in index:
    index = index.replace(old_subtitle, new_subtitle)
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(index)
