# uvicorn src.server:app --reload --port 5000

import os
import base64
import face_recognition
import numpy
import re
from PIL import Image
from io import BytesIO
from database import db
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db.criar_bdd()

conn = db.conectar()
cursor = conn.cursor()


class Funcionario(BaseModel):
    nome: str
    cpf: str
    foto_base64: str
    email: str
    celular: str
    face_encode: Optional[List[float]] = None
    foto_path: Optional[str] = None


    def validar_cpf(self):
        if not self.cpf.isdigit() or len(self.cpf) != 11:
            raise HTTPException(status_code=400, detail="CPF inválido.")    

        return 

    def validar_email(self):
        regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(regex, self.email):
            raise HTTPException(status_code=400, detail="Email inválido.")

    def validar_celular(self):
        celular_limpo = re.sub(r'\D', '', self.celular)
        if not re.fullmatch(r'\d{2}9\d{8}', celular_limpo):
            raise HTTPException(status_code=400, detail="Número de celular inválido.")

    def validar(self):
        if not self.nome or not self.cpf or not self.foto_base64 or not self.email or not self.celular:
            raise HTTPException(status_code=400, detail="Preencha todos os campos Obrigatórios!")
    
        self.validar_cpf()
        self.validar_email()
        self.validar_celular()

    def processar_imagem(self):
        header, encode64 = self.foto_base64.split(",", 1)
        img_bin = base64.b64decode(encode64)
        img_rgb = Image.open(BytesIO(img_bin)).convert("RGB")
        img = numpy.array(img_rgb)

        faces = face_recognition.face_locations(img)
        if not faces:
            raise HTTPException(status_code=400, detail="Nenhum rosto detectado.")

        maior_rosto = max(faces, key=lambda rect: (rect[2] - rect[0]) * (rect[1] - rect[3]))
        faces_encodings = face_recognition.face_encodings(img, [maior_rosto])

        if len(faces_encodings) != 1:
            raise HTTPException(status_code=400, detail="A imagem deve conter exatamente um rosto.")

        self.face_encode = faces_encodings[0].tolist()
        return img_bin     

    def salvar_imagem(self):
        PASTA_IMAGENS = os.path.join("src", "img")
        os.makedirs(PASTA_IMAGENS, exist_ok=True)
        img_bin = self.processar_imagem()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"{self.cpf}_{timestamp}.png"
        self.foto_path = os.path.join(PASTA_IMAGENS, nome_arquivo)

        with open(self.foto_path, "wb") as fp:
            fp.write(img_bin)

    def inserir_bd(self):
        self.salvar_imagem()

        query = "INSERT INTO funcionario (cpf, nome, foto_path, face_encode, email, celular) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (self.cpf, self.nome, self.foto_path, self.face_encode, self.email, self.celular))
        conn.commit()


# CREATE USUÁRIO.
@app.post("/inserirUsuario")
async def cadastrar(f: Funcionario):
    f.validar()

    try:
        f.inserir_bd()
        return {"message": "Inserido com sucesso!"}
    except Exception as e:
        detail = str(e).split(":", 1)[1].strip()
        raise HTTPException(status_code=500, detail=detail)


# READ USUÁRIOS.
@app.get("/api/usuarios")
def listar_usuarios():
    try:
        query = "SELECT cpf, nome, email, celular FROM funcionario"
        cursor.execute(query)
        rows = cursor.fetchall()

        usuarios = []
        for row in rows:
            usuarios.append({
                "cpf": row[0],
                "nome": row[1],
                "email": row[2],
                "celular": row[3],
            })

        return usuarios

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# UPDATE USUÁRIO.
@app.get("/api/usuario")
def buscar_usuario(cpf: str):
    try:
        query = "SELECT cpf, nome, email, celular, foto_path FROM funcionario WHERE cpf = %s"
        cursor.execute(query, (cpf,))
        row = cursor.fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        foto_filename = os.path.basename(row[4]) if row[4] else None
        foto_url = f"/fotos/{foto_filename}" if foto_filename else None

        return {
            "cpf": row[0],
            "nome": row[1],
            "email": row[2],
            "celular": row[3],
            "foto_path": foto_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Validar atualização.
class UsuarioAtualizacao(BaseModel):
    nome: str
    email: EmailStr
    celular: str
    foto_base64: Optional[str] = None

    @field_validator('celular')
    def validar_celular(cls, v):
        numero = re.sub(r'\D', '', v)
        if not re.match(r'^\d{2}9\d{8}$', numero):
            raise ValueError("Número de celular inválido. Deve conter DDD + 9 dígitos (ex: 11991234567)")
        return numero

@app.put("/api/usuarios/{cpf}")
def atualizar_usuario(cpf: str, dados: UsuarioAtualizacao):
    try:
        query = """
            UPDATE funcionario 
            SET nome = %s, email = %s, celular = %s 
            WHERE cpf = %s
        """
        cursor.execute(query, (dados.nome, dados.email, dados.celular, cpf))

        if dados.foto_base64:
            funcionario_temp = Funcionario(
                nome=dados.nome,
                cpf=cpf,
                foto_base64=dados.foto_base64,
                email=dados.email,
                celular=dados.celular
            )
            funcionario_temp.validar()
            funcionario_temp.salvar_imagem()

            update_foto_query = """
                UPDATE funcionario
                SET foto_path = %s, face_encode = %s
                WHERE cpf = %s
            """
            cursor.execute(update_foto_query, (funcionario_temp.foto_path, funcionario_temp.face_encode, cpf))

        conn.commit()
        return {"message": "Usuário atualizado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# DELETAR USUÁRIO
@app.delete("/api/usuarios/{cpf}")
def deletar_usuario(cpf:str):
    try:
        query = "DELETE FROM funcionario WHERE cpf = %s"
        cursor.execute(query, (cpf,))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        return {"message": "Usuário deletado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


current_dir = os.path.dirname(__file__)

STATIC_DIR = os.path.join(current_dir, "static")
IMAGENS_DIR = os.path.join("src", "img")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(IMAGENS_DIR, exist_ok=True)

app.mount("/fotos", StaticFiles(directory=IMAGENS_DIR), name="fotos")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# PÁGINAS.
@app.get("/")
def get_home():
    index_dir = os.path.join(STATIC_DIR, "home.html")
    return FileResponse(index_dir)

@app.get("/cadastrar_usuario")
def get_cadastrar_usuario():
    index_dir = os.path.join(STATIC_DIR, "cadastrar_usuario.html")
    return FileResponse(index_dir)

@app.get("/gerenciar_usuarios")
def get_gerenciar_usuario():
    index_dir = os.path.join(STATIC_DIR, "gerenciar_usuarios.html")
    return FileResponse(index_dir)

@app.get("/editar_usuario")
def get_editar_usuario():
    index_dir = os.path.join(STATIC_DIR, "editar_usuario.html")
    return FileResponse(index_dir)