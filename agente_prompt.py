from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

def gerar_prompt(pergunta,chave,df):
    dados_texto = df.head(10).to_string(index=False)
    prompt_template = PromptTemplate(
        input_variables=["dados"],
        template="""
        Você é um engenheiro de prompt.

        Vai receber algumas linhas de um conjunto de dados e fazer o melhor prompt para responder a pergunta do usuario.
        Você não vai criar nenhum codigo.
        Vai só criar o melhor prompt para responder a pergunta.
        O prompt vai ser enviado para um agente programador python para fazer um codigo python.

        O agente programador deve ser capaz de elabora um codigo com o prompt que voce descreveu para responder a pergunta.
 
        

        Aqui esta o conjunto de dados:

        {dados}


        Pergunta:

        {pergunta}
        """
        )
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=chave)

    chain = prompt_template | llm
    resposta = chain.invoke({"dados": dados_texto, "pergunta": pergunta})
  

    return resposta.content