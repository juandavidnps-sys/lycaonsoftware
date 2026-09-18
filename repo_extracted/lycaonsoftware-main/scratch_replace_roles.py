import os

files_to_process = [
    'templates/login.html',
    'templates/factura_pdf.html',
    'templates/dashboard/users.html',
    'templates/dashboard/index.html',
    'templates/ayuda.html',
    'static/js/main.js',
    'app.py'
]

base_dir = 'c:/Users/SENA/Desktop/bluebird_flask'

for file_path in files_to_process:
    full_path = os.path.join(base_dir, file_path)
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace occurrences safely
        new_content = content.replace('operadores', 'clientes')
        new_content = new_content.replace('Operadores', 'Clientes')
        new_content = new_content.replace('operador', 'cliente')
        new_content = new_content.replace('Operador', 'Cliente')
        
        if new_content != content:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {file_path}")
    else:
        print(f"File not found: {file_path}")

print("Done")
