'''
Refatorado.
Gerencia ciclo de vida da interação com o agente de IA.
Loop console removido, agora é executado em app.py.
'''
import pandas as pd
import io
import matplotlib as mlt
from agentes import  agente_executor as executor
from contextlib import redirect_stdout, redirect_stderr

# # Exemplo de uso do Agente
# chave='coloque aqui sua chave do gemini studio'
# url='endereco do arquivo compactado'
# agente=executor.Agente()
# agente.carrega_arquivos(url=url, chave=chave)
# agente.df.info()

# # Loop interativo para perguntas
# while True:
#     pergunta = input("Digite sua pergunta ou dados (ou 'sair' para encerrar): ")
#     if pergunta.strip().lower() in ["sair", "exit", "quit"]:
#         print("👋 Encerrando o agente.")
#         break

#     agente.pergunta(pergunta)

class AgenteController:
    """
    Controlador para gerenciar ciclo de vida da interação com o agente de IA.
    Usado por interface Streamlit para interagir com o agente.
    """
    def __init__(self):
        """
        Inicializa o controlador.
        """
        self.agente = None # Agente é instanciado sob demanda
 
    def initialize_agente(self, api_key:str, file_url:str = None, uploaded_files: list = None) -> str:
        """
        Cria instancia do agente sob uso.
        Carrega e procesa arquivos da url
    
        ✅,⚠️,❌ são usados para lidos pelo app.py para checar o status da operação.
        
        Args:
            api_key (str): Chave de API para autenticação.
            file_url (str): URL do arquivo .zip compactado com os dados.
        
        Returns:
            str: Mensagem de status com sucesso ou erro.
        """
        try:
            if not file_url and not uploaded_files:
                return "⚠️ Por favor, forneça uma URL ou carregue um arquivo."
            
            # Baixa, descompacta e carrega os CSVs no agente
            self.agente = executor.Agente()
            self.agente.carrega_arquivos(chave=api_key, url=file_url, arquivos_carregados=uploaded_files)
            # garante que df existe
            if hasattr(self.agente, 'df') and isinstance(self.agente.df, pd.DataFrame) and not self.agente.df.empty:
                return "✅ Agente inicializado e dados carregados com sucesso!"
            else:
                return "⚠️ Dados não carregados corretamente. Verifique o arquivo ou a chave da API."
        except FileNotFoundError as fnf_error:
            return f"❌ Erro ao carregar arquivo: {str(fnf_error)}"
        except Exception as e:
            return f"❌ Erro ao inicializar agente: {str(e)}"
    
    def ask_question(self, question: str) -> str:
        """
        Envia uma pergunta ao agente e retorna a resposta.
        Redireciona saída padrão (console out) e retorna como string
        
        Args:
            question (str): Pergunta a ser enviada ao agente.
        
        Returns:
            str: Resposta do agente (ou erro!).
        """
        if not self.agente:
            return "Agente não inicializado. Por favor, configure o agente e carregue os dados primeiro."
        output_capture = io.StringIO()        
        try:
            with redirect_stdout(output_capture), redirect_stderr(output_capture):
                # Processa entrada e imprime saída
                self.agente.pergunta(question)
            answer = output_capture.getvalue()
            
            if not answer.strip():
                return "O agente processou a solicitação, mas não gerou uma resposta em texto."
            return answer
        except Exception as e:
            return f"Ocorreu um erro ao processar a pergunta: {e}\n\n{output_capture.getvalue()}"
