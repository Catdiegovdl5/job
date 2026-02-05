import os
import csv
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Ensure leads.csv is saved in the same directory as app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEADS_FILE = os.path.join(BASE_DIR, 'leads.csv')

def init_csv():
    """Initializes the CSV file with headers if it doesn't exist."""
    if not os.path.exists(LEADS_FILE):
        with open(LEADS_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Nome', 'Telefone', 'Interesse'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    phone = request.form.get('phone')
    service = request.form.get('service')

    if name and phone and service:
        init_csv()
        with open(LEADS_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name, phone, service])

        # In a real app, we might flash a message. For now, simple redirect with success param.
        return redirect(url_for('index', success=1))
    else:
        return "Erro: Todos os campos são obrigatórios.", 400

if __name__ == '__main__':
    # Initialize CSV on startup
    init_csv()
    app.run(host='0.0.0.0', port=5000)
