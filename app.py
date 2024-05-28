import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify, render_template, request, send_from_directory
from PyPDF2 import PdfReader
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
app.config['LOG_FOLDER'] = './logs'
app.config['SERVICE_TOKEN'] = 'SIMULATED_TOKEN'

if not os.path.exists(app.config['LOG_FOLDER']):
    os.makedirs(app.config['LOG_FOLDER'])

log_handler = RotatingFileHandler(os.path.join(app.config['LOG_FOLDER'], 'app.log'), maxBytes=10000, backupCount=1)
log_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)
app.logger.addHandler(log_handler)
app.logger.setLevel(logging.INFO)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def pdf_to_text(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
        return text
    except Exception as e:
        return f"Error: {str(e)}"

def log_message(message):
    app.logger.info(message)

@app.route('/convert/pdf2txt', methods=['POST'])
def convert_pdf_to_txt():
    if 'file' not in request.files:
        log_message('No file sent')
        return jsonify({'error': 'No file sent'}), 400

    file = request.files['file']
    if file.filename == '':
        log_message('No file selected')
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(pdf_path)

        text = pdf_to_text(pdf_path)
        if text.startswith("Error"):
            log_message(f'Error converting file {filename}: {text}')
            return jsonify({'error': text}), 500

        txt_filename = filename.rsplit('.', 1)[0] + '.txt'
        txt_path = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(text)

        log_message(f'Conversion completed for file {filename}, saved as {txt_filename}')
        return jsonify({
            'message': 'Conversion completed',
            'txt_file': txt_filename,
            'download_link': f'/download/{txt_filename}'
        }), 201
    else:
        log_message(f'File not allowed: {file.filename}')
        return jsonify({'error': 'File not allowed'}), 400

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
