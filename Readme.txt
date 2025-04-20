Instale a versão 3.10.0 do Python no site: https://www.python.org/downloads/release/python-3100/

Pacotes a serem instalados antes de rodar o código:
    1. opencv-python
    2. dlib
    3. face_recognition
    4. psycopg2

Para instalar o Dlib é necessário ter o CMake e um compitaldor C++ instalados.
    Passo a passo de instalação do CMake:
        1. Acesse: https://cmake.org/download/
        2. Baixe a versão "cmake-windows-x86_64.msi"
        3. Durante a instalação marque a opção "add CMake to the PATH environment variable".

    Passo a passo de instalação do compilador C++:
        1. Após a instalação do CMake, acesse: https://visualstudio.microsoft.com/visual-cpp-build-tools/
        2. Selecione "Baixar Ferramentas de Compilação".
        3. Durante a instalação, selecione:
            Em Cargas de trabalho: 
                Desenvolvimento para desktop com C++.
                Ferramentas do C++ para desenvolvimento em Linux.
            Em "Componentes individuais":
                Todos SDK's do Windows 10 ou Windows 11 (Baseado na versão do seu sistema).

Passo a passo para instalar os pacotes:
    1. Pressione Win + R.
    2. Digite CMD e aperte Enter.
    3. Escreva "pip install opencv-python".
    7. Escreva "pip install dlib".
    4. Escreva "pip install face_recognition".
    5. Escreva "pip install psycopg2".