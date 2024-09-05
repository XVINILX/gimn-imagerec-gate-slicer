# Ferramenta Python para 3D Slicer

Este projeto contém scripts Python que utilizam bibliotecas específicas para trabalhar com reconstrução de imagens médicas no software 3D Slicer. Abaixo estão as instruções para instalar as dependências necessárias em um ambiente virtual Python e como adicionar a ferramenta ao 3D Slicer.

## Pré-requisitos

- **Python 3.x**: Certifique-se de ter o Python 3.x instalado em seu sistema.
- **3D Slicer**: Baixe e instale o [3D Slicer](https://www.slicer.org/), que será utilizado para rodar esta ferramenta.

## Passo 1: Criar e ativar um ambiente virtual

1. Abra um terminal ou prompt de comando.

2. Navegue até o diretório do projeto onde o código está localizado.

3. Crie um ambiente virtual utilizando o comando:

    ```bash
    python -m venv slicer_env
    ```

4. Ative o ambiente virtual:

   - No **Windows**:

      ```bash
      slicer_env\Scripts\activate
      ```

   - No **Linux** ou **macOS**:

      ```bash
      source slicer_env/bin/activate
      ```

## Passo 2: Instalar as dependências

Após ativar o ambiente virtual, execute o seguinte comando para instalar as dependências listadas no arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```


To ensure that all the dependencies are correctly installed, including itk, matplotlib, and the local package gimnREC, here’s an updated approach and corresponding instructions for installation.

Updated requirements.txt
txt
Copiar código
numpy
matplotlib
itk
numba
PyQt5
vtk
slicer  # slicer is managed internally by 3D Slicer, no need to install via pip
Instructions in the README.md
markdown
Copiar código
# Ferramenta Python para 3D Slicer

Este projeto contém scripts Python que utilizam bibliotecas específicas para trabalhar com reconstrução de imagens médicas no software 3D Slicer. Abaixo estão as instruções para instalar as dependências necessárias em um ambiente virtual Python e como adicionar a ferramenta ao 3D Slicer.

## Pré-requisitos

- **Python 3.x**: Certifique-se de ter o Python 3.x instalado em seu sistema.
- **3D Slicer**: Baixe e instale o [3D Slicer](https://www.slicer.org/), que será utilizado para rodar esta ferramenta.

## Passo 1: Criar e ativar um ambiente virtual

1. Abra um terminal ou prompt de comando.

2. Navegue até o diretório do projeto onde o código está localizado.

3. Crie um ambiente virtual utilizando o comando:

    ```bash
    python -m venv slicer_env
    ```

4. Ative o ambiente virtual:

   - No **Windows**:

      ```bash
      slicer_env\Scripts\activate
      ```

   - No **Linux** ou **macOS**:

      ```bash
      source slicer_env/bin/activate
      ```

## Passo 2: Instalar as dependências

Após ativar o ambiente virtual, execute o seguinte comando para instalar as dependências listadas no arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

Isso instalará as bibliotecas necessárias, como numpy, matplotlib, itk, numba, entre outras.

## Passo 3: Configurar o ambiente Python no 3D Slicer
Abrir o 3D Slicer: Inicie o 3D Slicer no seu computador.

Acessar o Python Interactor: No menu principal, vá para View > Python Interactor para abrir o terminal Python integrado.

Configurar o ambiente virtual no 3D Slicer:

No terminal Python do 3D Slicer, configure o ambiente virtual criado anteriormente para que o Slicer utilize as dependências instaladas no ambiente.

Execute o seguinte comando, substituindo o caminho pelo caminho absoluto do seu ambiente virtual:

```bash
slicer.util.pip_install('--no-warn-script-location --prefix "<CAMINHO_ABSOLUTO>/slicer_env" -r requirements.txt')
```

Isso garantirá que as bibliotecas Python do ambiente virtual sejam acessíveis no Slicer.


## Passo 4: Criando a aplicação a ser utilizada 
No 3D Slicer, vá para o menu Edit > Application Settings > Modules, e adicione o diretório onde sua ferramenta está localizada em "Additional Module Paths". Isso fará com que o Slicer reconheça sua ferramenta como um módulo adicional.

Reinicie o 3D Slicer.

Agora, a ferramenta deve aparecer no 3D Slicer como um módulo adicional. Você pode acessá-la pelo menu de módulos do Slicer.

Utilize o teste para ver o projeto funcionando e siga as instruções para reconstrução correta dos sinogramas