import os
import io
import pandas as pd
# from agentes import agente_prompt as prompt,agente_programador as programador, agente_descompactador as descompactador, agente_validador as validador
from agentes import agente_prompt as prompt
from agentes import agente_programador as programador
from agentes import agente_descompactador as descompactador
from agentes import agente_descompactador_url as descompactador_url
from agentes import agente_processador_upload as processador_upload

class Agente:
    def __init__(self):
        self.chave=''
        self.df=None

    def carrega_arquivos(self, chave, url=None, arquivos_carregados=None):
        # 👉 Coloque sua chave da API Gemini aqui:
        os.environ["GOOGLE_API_KEY"] = chave

        arquivos = []
        if url: 
            print(f"Iniciando download da URL: {url}")
            arquivos=descompactador_url.descompactar_arquivos(url)
        elif arquivos_carregados:
            print(f"Iniciando processamento de arquivos carregados.")
            arquivos = arquivos = processador_upload.processar_arquivo_upload(arquivos_carregados)

        if not arquivos:
            raise ValueError("Nenhum arquivo CSV válido foi encontrado. Verifique a fonte dos dados e tente novamente.")
        
        amostras=descompactador_url.preparar_amostras_para_agente(arquivos)
        
        rest=programador.agrupar_arquivos(os.environ["GOOGLE_API_KEY"],amostras)
        codigo_limpo = rest.strip("```").replace("python", "").strip()

        exec_globals = {"pd": pd}
        exec_locals = {"lista_df": arquivos} # Passa 'lista_df' com os DataFrames completos
        exec(codigo_limpo, exec_globals, exec_locals)
        self.df = exec_locals.get("df")

    def pergunta(self,pergunta):
            prompt_gerado=prompt.gerar_prompt(pergunta,os.environ["GOOGLE_API_KEY"],self.df)
            print(prompt_gerado)
            resposta=programador.gerar_codigo(os.environ["GOOGLE_API_KEY"],self.df,prompt_gerado)
            print(resposta)
            codigo_limpo = resposta.strip("```").replace("python", "").strip()
            exec(codigo_limpo, {"df_total": self.df})
    
 