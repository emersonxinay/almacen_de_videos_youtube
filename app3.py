from flask import Flask, request, render_template, redirect, url_for, flash
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configura la autorización con Google API
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "./compilandocode-64219584fe2f.json", scope)
client = gspread.authorize(creds)

# Ruta para mostrar el formulario


@app.route('/formulario', methods=['GET'])
def formulario():
    return render_template('formulario.html')

# Ruta para manejar el envío del formulario


@app.route('/formulario', methods=['POST'])
def handle_formulario():
    nombre = request.form['nombre']
    email = request.form['email']
    mensaje = request.form['mensaje']

    try:
        # Abre la hoja de Google Sheets
        sheet = client.open_by_url(
            "https://docs.google.com/spreadsheets/d/1xRvKsi8ZMb5ILpvJTqkTW9MKAHXal_laWo_2_9p9VJY/edit?usp=sharing")
        worksheet = sheet.get_worksheet(0)  # Abre la primera hoja

        # Escribe datos en la hoja
        worksheet.append_row([nombre, email, mensaje])

        flash('Datos enviados correctamente')
    except Exception as e:
        flash(f'Hubo un error: {e}')

    return redirect(url_for('formulario'))


if __name__ == '__main__':
    app.run(debug=True)
