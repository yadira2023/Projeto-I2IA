from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

def gerar_codigo(chave,df,prompt):
    
    prompt_template = PromptTemplate(
    input_variables=["prompt"],
    template="""
    Você é um agente programador Python.

    Você irá receber um pedido (prompt) para realizar uma análise em um DataFrame chamado `df_total`.
    ⚠️ NÃO crie dados fictícios. O DataFrame `df_total` já está carregado na memória.

    Sua tarefa é:
    - Criar o código em Python para atender ao prompt.
    - NÃO criar funções, testes ou explicações.
    - Apenas gere o código diretamente executável.
    - O código deve terminar com um `print()` que exibe a resposta final como uma **string**.
    - O print de retorno pode ser contextualizado.
    - Se for solicitado criar algum grafico pode obrigatoriamente plotar com o pandas ou matplotlib

    lista de colunas:
    {dados}

    Prompt:
    {prompt}
    """
    )
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=chave)
   
 

    chain = prompt_template | llm
    resposta = chain.invoke({"dados":df.columns,"prompt": prompt})
  

    return resposta.content

def agrupar_arquivos(chave,df):
    
    prompt_template = PromptTemplate(
    input_variables=["dados"],
    template="""
    Você é um agente programador Python.

    Você irá receber uma amostra de um conjunto de dataframes.
    ⚠️ NÃO crie dados fictícios. O DataFrame `lista_df` já está carregado na memória.

    Sua tarefa é:
    - Criar o código em Python para fazer o join ou concat dos dataframes.
    - Com a amostra que vou te enviar voce vai escolher a melhor forma de fazer o join de acordo com as colunas dos dataframes.
    - Na coluna indice_dataframe tem o indice do respectivo datadrame que esta em lista_df
    - NÃO criar funções, testes ou explicações.
    - Apenas gere o código diretamente executável.
    - O resultado da juncao tem que ir para a variavel df que esta na memoria.

    Informações sobre os DataFrames `lista_df`:
    {dados}

    """
    )
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=chave)

    chain = prompt_template | llm
    resposta = chain.invoke({"dados": df})
  

    return resposta.content