import os
import json
from flask import Flask, request, render_template, redirect, url_for, flash
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Construir las credenciales desde variables de entorno
google_credentials = {
    "type": os.getenv("GOOGLE_TYPE"),
    "project_id": os.getenv("GOOGLE_PROJECT_ID"),
    "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
    "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
    "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("GOOGLE_UNIVERSE_DOMAIN")
}

# Configurar el alcance (scope) de las credenciales
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

# Crear las credenciales
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    google_credentials, scopes=scope)

# Autorizar el cliente de gspread
client = gspread.authorize(creds)


@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    title = "Formulario"
    return render_template('formulario.html', title=title)


@app.route('/handle_formulario', methods=['POST'])
def handle_formulario():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    email = request.form['email']
    telefono = request.form['telefono']
    mensaje = request.form['mensaje']
    fecha_envio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        sheet = client.open_by_url(
            "https://docs.google.com/spreadsheets/d/1xRvKsi8ZMb5ILpvJTqkTW9MKAHXal_laWo_2_9p9VJY/edit?usp=sharing")
        worksheet = sheet.get_worksheet(0)
        worksheet.append_row(
            [nombre, apellido, email, telefono, mensaje, fecha_envio])
        flash('Datos enviados correctamente', 'success')
    except Exception as e:
        flash(f'Hubo un error: {e}', 'danger')

    return redirect(url_for('inicio'))


@app.route('/')
def inicio():
    return "Inicio"


if __name__ == '__main__':
    app.run(debug=True)
