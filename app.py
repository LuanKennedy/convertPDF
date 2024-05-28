import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify, render_template, request, send_from_directory
from PyPDF2 import PdfReader
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['PASTA_UPLOAD'] = './uploads'
app.config['EXTENSOES_PERMITIDAS'] = {'pdf'}
app.config['PASTA_LOGS'] = './logs'
app.config['TOKEN_SERVICO'] = 'SIMULANDO_TOKEN'

if not os.path.exists(app.config['PASTA_LOGS']):
    os.makedirs(app.config['PASTA_LOGS'])

log_handler = RotatingFileHandler(os.path.join(app.config['PASTA_LOGS'], 'app.log'), maxBytes=10000, backupCount=1)
log_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)
app.logger.addHandler(log_handler)
app.logger.setLevel(logging.INFO)

def arquivo_permitido(nome_arquivo):
    return '.' in nome_arquivo and nome_arquivo.rsplit('.', 1)[1].lower() in app.config['EXTENSOES_PERMITIDAS']

def pdf_para_texto(caminho_pdf):
    try:
        leitor = PdfReader(caminho_pdf)
        texto = ''
        for pagina in leitor.pages:
            texto += pagina.extract_text() or ''
        return texto
    except Exception as e:
        return f"Erro: {str(e)}"

def registra_log(mensagem):
    app.logger.info(mensagem)

@app.route('/convert/pdf2txt', methods=['POST'])
def convert_pdf_to_txt():
    if 'file' not in request.files:
        registra_log('No file sent')
        return jsonify({'error': 'No file sent'}), 400

    arquivo = request.files['file']
    if arquivo.filename == '':
        registra_log('No file selected')
        return jsonify({'error': 'No file selected'}), 400

    if arquivo and arquivo_permitido(arquivo.filename):
        nome_arquivo = secure_filename(arquivo.filename)
        caminho_pdf = os.path.join(app.config['PASTA_UPLOAD'], nome_arquivo)
        os.makedirs(app.config['PASTA_UPLOAD'], exist_ok=True)
        arquivo.save(caminho_pdf)

        texto = pdf_para_texto(caminho_pdf)
        if texto.startswith("Erro"):
            registra_log(f'Error converting file {nome_arquivo}: {texto}')
            return jsonify({'error': texto}), 500

        nome_txt = nome_arquivo.rsplit('.', 1)[0] + '.txt'
        caminho_txt = os.path.join(app.config['PASTA_UPLOAD'], nome_txt)
        with open(caminho_txt, 'w', encoding='utf-8') as arquivo_txt:
            arquivo_txt.write(texto)

        registra_log(f'Conversion completed for file {nome_arquivo}, saved as {nome_txt}')
        return jsonify({
            'message': 'Conversion completed',
            'txt_file': nome_txt,
            'download_link': f'/download/{nome_txt}'
        }), 201
    else:
        registra_log(f'File not allowed: {arquivo.filename}')
        return jsonify({'error': 'File not allowed'}), 400

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(app.config['PASTA_UPLOAD'], filename)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
