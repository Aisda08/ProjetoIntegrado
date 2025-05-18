import os
import base64
import face_recognition
import numpy
from PIL import Image
from io import BytesIO
from database import db
from datetime import datetime
from fastapi import FastAPI, HTTPException
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
    foto_base64: str
    email: str
    tel_cel: str


    def validar_cpf(self):
        if not self.cpf.isdigit() or len(self.cpf) != 11:
            raise HTTPException(status_code=400, detail="CPF inválido.")    

        return 

    def validar_email(self):
        if not self.dt_nasc:
            raise HTTPException(status_code=400, detail="Campo obrigatório faltando: Email")

        return

    def validar_tel_celular(self):
        return
    
    def validar_foto(self):
        return

    def validar(self):
        if not self.nome or not self.cpf or not self.foto_base64 or not self.email or not self.tel_celular:
            raise HTTPException(status_code=400, detail="Preencha todos os campos Obrigatórios!")
    
        self.validar_cpf()
        self.validar_email()
        self.validar_tel_celular()



    def processar_imagem(self):
        header, encode64 = self.foto_base64.split(",", 1) # Separa cabeçalho da string base64.

        img_bin = base64.b64decode(encode64) # Transforma encode_base64 em dados binários.
        img_rgb = Image.open(BytesIO(img_bin)).convert("RGB") # Converte para RBG.
        img = numpy.array(img_rgb) # Converte imagem para array.

        faces_encodings = face_recognition.face_encodings(img) # códifica rostos na imagem.
        if len(faces_encodings) != 1:
            raise HTTPException(status_code=400, detail="A imagem deve conter exatamente um rosto.")
        face_encode = faces_encodings[0].tolist() # Tranforma rosto em array.

        return img_bin, face_encode


    def inserir_bd(self, foto_path:str, face_encode):
        # Executa query SQL.
        query = "INSERT INTO funcionario (cpf, nome, foto_path, face_encode) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (self.cpf, self.nome, foto_path, face_encode))
        conn.commit()


# Cadastra dados na base.
@app.post("/inserir")
async def cadastrar(f: Funcionario):
    f.validar()

    PASTA_IMAGENS = os.path.join("src", "img")
    os.makedirs(PASTA_IMAGENS, exist_ok=True)

    try:
        img_bin, face_encode = f.processar_imagem()

        # Criar nome único para a imagem
        cpf, = f.cpf
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"{cpf}_{timestamp}.png"
        caminho_arquivo = os.path.join(PASTA_IMAGENS, nome_arquivo)

        f.inserir_bd(caminho_arquivo, face_encode, img_bin)

        # Salva a imagem.
        with open(caminho_arquivo, "wb") as f:
            f.write(img_bin)

        return {"message": "Inserido com sucesso!"}
    except Exception as e:
        detail = str(e).split(":", 1)[1].strip()
        print("Erro:", detail)
        raise HTTPException(status_code=500, detail=detail)


# Serve a pasta static como arquivos estáticos
current_dir = os.path.dirname(__file__)
STATIC_DIR = os.path.join(current_dir, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

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

@app.get("/editar_usuario")
def get_editar_usuario():
    index_dir = os.path.join(STATIC_DIR, "editar_usuario.html")
    return FileResponse(index_dir)

@app.get("/api/usuario")
def buscar_usuario(cpf: str):
    try:
        query = "SELECT cpf, nome, email, celular FROM funcionario WHERE cpf = %s"
        cursor.execute(query, (cpf,))
        row = cursor.fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        return {
            "cpf": row[0],
            "nome": row[1],
            "email": row[2],
            "celular": row[3],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
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

@app.put("/api/usuarios/{cpf}")
def atualizar_usuario(cpf: str, dados: dict):
    try:
        query = """
            UPDATE funcionario 
            SET nome = %s, email = %s, celular = %s 
            WHERE cpf = %s
        """
        cursor.execute(query, (dados["nome"], dados["email"], dados["celular"], cpf))
        conn.commit()
        return {"message": "Usuário atualizado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))