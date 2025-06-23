# Desafio 2 – Agentes de Inteligência Artificial (i2a2)

Este projeto foi desenvolvido como parte do **Desafio 2** do curso da plataforma [i2a2](https://i2a2.com.br), com foco na criação de agentes de inteligência artificial.

## Objetivo

Criar um sistema com **agentes de IA** capazes de descompactar arquivos e responder, de forma inteligente, às perguntas dos usuários referente aos arquivos descompactados.

## Framework

* Interface Web: Streamlit
* Orquestração de Agentes e LLM: LangChaing
* Modelo de Linguagem (LLM): Google Gemini
* Manipulação de Dados: Pandas

## Estrutura do Projeto

O sistema é modularizado em multiplos agentes com responsabilidades específicas, orquestrados por um agente executor central. A interação do usuário é feita através de uma interface web construóda com Streamlit.

## Interface de Usuário (`app.py`)

Aplicação web feita com Streamlit que permite ao usuário:

1. Inserir a chave de API do Google Gemini.
2. Fornecer os dados para análise, seja através de uma URL de um arquivo .zip ou fazendo o upload de arquivos .csv ou .zip diretamente.
3. Inicializar e interagir com o sistema de agentes através de uma interface de chat.
4. Visualizar e baixar o histórico da conversa.

## Controlador da Aplicação (`agente.py`)

Atua como uma ponte entre a interface do usuário (Streamlit) e o back-end (agentes de IA). Ele gerencia o ciclo de vida do agente executor, tratando da sua inicialização, envio de perguntas e recebimento de respostas.

## Agentes

### 1. Agente executor (`agente_executor.py`)
Orquestrador central. Não responde perguntas diretamente, mas coordena o fluxo de execução da tarefa entre os agentes.

Responsável por:
- Guarda os dados do dataset e chaves/
- Recebe requisição (url/csv)
- Ao receber uma pergunta:
  - cria a classe agente
  - Envia o prompt ao agente de prompt que refina a pergunta.
  - Envia os comandos para os outros agentes
  - Recebe o código python gerado e executa.

### 2. Agente de Processamento de Dados
* Agente URL (`agente_descompactador_url.py`)
  - Receber o link URL do arquivo compactado
  - Baixar o arquivo .zip da URL
  - Descompacta os arquivos em memória.
  - Carregar os CSVs em DataFrames.

* Agente de Upload (`agente_processador_upload.py`): Processa arquivos .csv ou .zip carregados diretametne pelo usuário, também carregando-os em DFs.

### 3. Agentes de Inteligência
* Agente de Prompt (`agente_prompt.py`)
  - Recebe a pergunta do usuário e uma amostra do DataFrame.
  - Gerar um prompt estruturado com o passo a passo necessário para encontrar a resposta

* Agente Programador (`agente_programador.py`)
  - Recebe o prompt técnico e o esquema do DataFrame.
  - Gera o código em python para agrupar os arquivos
  - Retorna o código para ser executado
  - Gerar código para visualizações e gráficos.

## Estrutura de Arquivos
```
├── dataset/
│ ├── 202401_NFs_Cabecalho.csv
│ └── 202401_NFs_Itens.csv
├── agentes/
│   ├── agente_descompactador.py
│   ├── agente_descompactador_url.py
│   ├── agente_processador_upload.py
│   ├── agente_executor.py
│   ├── agente_programador.py
│   └── agente_prompt.py
├── agente.py
├── app.py
├── requirements.txt
└── README.md
```

## Como Executar

1. Clone o repositório:
    ```bash
    git clone https://github.com/ThiagoDFMaia/projeto_i2a2.git
    ```

    1. Acesse a pasta do projeto
    ```bash
    cd projeto_i2a2
    ```

2. Configuração do ambiente virtual do programa
   1. Crie o ambiente
        ```bash
        python -m venv venv
        ```
   2. Ative o ambiente
       * Windows
            ```bash
            .\venv\Scripts\activate
            ```
      * Linux/Mac
            ```bash
            python -m venv venv
            ```
   
3. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

4. Executea a aplicação streamlit:
    ```bash
    streamlit run app.py
    ```

5. Acesse a interface:
    Abra o navegador no endereço fornecido pelo Streamlit durante a execução do código.

## Publicar

### Pré-requisitos.
1. Publique o projeto no github.
2. Certifique-se que o `requirements.txt` esteja atualizado e presente no seu projeto.
3. Retire a chave API do seu código e bloqueie o BYOK (Bring Your Own Key).
   Em `app.py` substitua:
   ```python
   api_key = st.text_input(
        "Chave da API GEMINI",
        type="password",
        placeholder="Insira sua chave de API aqui"
    )
   ```
   por:
   ```python
   api_key = st.secrets.get("GEMINI_API_KEY")
   ```

### Publicação.
1. Acesse o Streamlit Community Cloud
   - Vá para [share.streamlit.io](https://share.streamlit.io/).
   - Faça login utilizando sua conta do GitHub.

2. Crie um Novo Aplicativo (New App)
    No painel principal, clique no botão "New app" para iniciar o processo de configuração.

3. Siga o processo de instalação disponívenl no site.

4. Adicione sua Chave de API (Secrets)
    Para garantir que sua chave de API permaneça segura e não seja exposta publicamente.
   - Clique em `"Advanced settings..."`.
   - Na seção `"Secrets"`, cole sua chave da API do Gemini no formato TOML, como no exemplo abaixo:
        ```Ini, TOML
        GEMINI_API_KEY = "SUA_CHAVE_DE_API_SECRETA_VAI_AQUI"
        ```

    O nome da variável (GEMINI_API_KEY) deve ser exatamente o mesmo que você usou no seu código (st.secrets.get("GEMINI_API_KEY")) para que o Streamlit possa encontrá-la.
   - Clique em "Save" para armazenar o segredo.

5. Publique a Aplicação (Deploy!)

## Próximos Passos
* Tornar os agentes independentes e reutilizáveis
  * Melhorar a arquitetura para que os agentes (especialmente o Programador e o de Prompt) sejam mais independentes e reutilizáveis, reduzindo o acoplamento com o Agente Executor.

* Permitir o uso de outros modelos de LLMS
  * Abstrair a lógica de chamada do modelo de linguagem para permitir a troca fácil entre diferentes LLMs (ex: GPT, Claude) sem alterar o código dos agentes.

* Persistência de Contexto
  * Implementar memória de conversação para que os agentes possam responder a perguntas de acompanhamento que dependem do contexto de interações anteriores.

* Segurança na Execução de Código
  * Substituir o uso de exec() por um ambiente de execução mais seguro e isolado (sandboxed) para mitigar riscos de segurança ao executar código gerado por IA.

## Contribuição
* Contribuições são bem-vindas!
* Sinta-se à vontade para abrir issues ou enviar pull requests.
