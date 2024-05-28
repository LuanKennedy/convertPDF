"# convertPDF"

Esse projeto teve como intuito realizar a conversão de arquivos em pdf para txt, utilizando algumas métricas pré-estabelecidas no escopo do projeto, e em decorrência disso fo criada uma api que garante esses princípios.

Configuração

as configurações da API foram definidas no arquivo app.py que utiliza do flask para criar a estratégia de manipulação e envio do arquivo pdf para txt, da lib logging que gera os logs e a werkzeug que serve como ponte entre o app.py com o webserver.

app.config['UPLOAD_FOLDER'] = './uploads' = cria um folder quando o usuário faz o upload do arquivo pdf
app.config['ALLOWED_EXTENSIONS'] = {'pdf'} = aceita apenas arquivos com a extensão .pdf
app.config['LOG_FOLDER'] = './logs' = insere os logs na pasta adequada
app.config['SERVICE_TOKEN'] = 'SIMULATED_TOKEN' = simula um token para acessar a rota de download do arquivo

Rotas

/convert/pdf2txt = responsável por converter o arquivo
'/' = rota inicial
'/download/<filename> = responsável por fazer o download do arquivo

docker

Crie a imagem da docker
docker build -t image_name

execute o docker
docker run -p 5000:5000 image_name

vai estar disponível na rota http://0.0.0.0:5000

execute a aplicação
python app.py

# estrutura do projeto

/conversorPdf
├── app.py
|---printsExec
├── venv
├── static
│ ├── styles.css
│ └── favicon.ico
└── templates
└── index.html

# Prints

Todos os prints serão disponibilizado no folder printsExec
