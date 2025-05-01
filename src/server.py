import os
import base64
import face_recognition
import numpy
from PIL import Image
from io import BytesIO
from database import db
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conecta ao banco de dados.
conn = db.conectar()
cursor = conn.cursor()


class Funcionario(BaseModel):
    nome: str
    cpf: str
    foto: str


def validar_cpf(cpf):
    if not cpf.isdigit() or len(cpf) != 11:
        raise HTTPException(status_code=400, detail="CPF inválido.")    
    
    return 


def processar_imagem(img_base64):
    header, encode64 = img_base64.split(",", 1) # Separa cabeçalho da string base64.

    img_bin = base64.b64decode(encode64) # Transforma encode_base64 em dados binários.
    img_rgb = Image.open(BytesIO(img_bin)).convert("RGB") # Converte para RBG.
    img = numpy.array(img_rgb) # Converte imagem para array.

    faces_encodings = face_recognition.face_encodings(img) # códifica rostos na imagem.
    if len(faces_encodings) != 1:
        raise HTTPException(status_code=400, detail="A imagem deve conter exatamente um rosto.")
    face_encode = faces_encodings[0].tolist() # Tranforma rosto em array.

    return img_bin, face_encode


def inserir_bd(cpf, nome, foto_path, face_encode, img):
    # Executa query SQL.
    query = "INSERT INTO funcionario (cpf, nome, foto_path, face_encode) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (cpf, nome, foto_path, face_encode))
    conn.commit()

    # Salva a imagem.
    with open(foto_path, "wb") as f:
        f.write(img)


# Cadastra dados na base.
@app.post("/inserir")
async def cadastrar(f: Funcionario):
    cpf, nome, foto = f.cpf, f.nome, f.foto

    if not nome or not cpf or not foto:
        raise HTTPException(status_code=400, detail="Campos obrigatórios faltando.")

    validar_cpf(cpf)
    
    PASTA_IMAGENS = os.path.join("src", "img")
    os.makedirs(PASTA_IMAGENS, exist_ok=True)

    try:
        img, face_encode = processar_imagem(f.foto)

        # Criar nome único para a imagem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"{cpf}_{timestamp}.png"
        caminho_arquivo = os.path.join(PASTA_IMAGENS, nome_arquivo)

        inserir_bd(cpf, nome, caminho_arquivo, face_encode, img)

        return {"message": "Inserido com sucesso!"}
    except Exception as e:
        detail = str(e).split(":", 1)[1].strip()
        print("Erro:", detail)
        raise HTTPException(status_code=500, detail=detail)


# Serve a pasta static como arquivos estáticos
current_dir = os.path.dirname(__file__)
STATIC_DIR = os.path.join(current_dir, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Rota para acessar o index.html na raiz do navegador
@app.get("/")
def get_index():
    index_dir = os.path.join(STATIC_DIR, "index.html")
    return FileResponse(index_dir)