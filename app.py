'''
Cria interface web do usuário para o projeto i2a2 usando Streamlit.
Permite inserir credenciais de API da IA, carregar dados e interagir com o agente em fomato de chat
Permite a funcionalidade de log na barra lateral com opção de download das conversa anteriores.
Atualmente cada pergunta é considerada como uma nova interação, não há persistência de estado entre perguntas.
'''
import streamlit as st
from agente import AgenteController

# Tamanho dos arquivos lidos
MAX_FILE_SIZE_MB = 10  # Limite por arquivo
MAX_TOTAL_SIZE_MB = 50 # Limite para a soma de todos os arquivos
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MAX_TOTAL_SIZE_BYTES = MAX_TOTAL_SIZE_MB * 1024 * 1024

# Configurações da página
st.set_page_config(
    page_title="i2a2 - Análise de CSV com Agentes de IA",
    page_icon=":robot:",
    layout="wide"
)

# Título da aplicação
st.title("i2a2 - Agente de IA para Análise de Arquivos CSV")
st.markdown("""**Como usar:**

1.  **Acesse a Barra Lateral** pela seta no canto superior esquerdo da sua tela.
1.  **Adicione a base de dados no agente** colocando a URL do arquivo .zip contendo os arquivos CSV com os dados a serem lidos.
2.  **Inicialize o Agente** clicando no botão "Inicializar Agente".
3.  **Converse com o Agente** na área de chat principal.
4.  **Veja o Histórico** e baixe os logs de conversa na barra lateral.
""")

# LOGS DE CONVERSA
def formatar_logs_para_dowload(log_history):
    """
    Formata o histórico de mensagens para download como texto.
    
    Args:
        log_history (list): Lista de dicionários com mensagens do chat.
        
    Returns:
        str: String formatada com as mensagens do chat.
    """
    log_text = "Histórico de Logs da Sessão:\n\n"
    log_text += "="*30 + "\n\n"
    
    for i, entry in enumerate(log_history):
        log_text += f"--- Interação {i+1} ---\n"
        log_text += f"Pergunta: {entry['pergunta']}\n\n"
        log_text += f"Resposta: {entry['resposta']}\n\n"
        log_text += "="*30 + "\n\n"
                
    return log_text

# Gerenciamento do Estado da Sessão
# Inicializa o controlador e o estado do chat se não existirem
if 'agente_controller' not in st.session_state:
    st.session_state.agente_controller = AgenteController()
if 'agent_initialized' not in st.session_state:
    st.session_state.agent_initialized = False
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'log_history' not in st.session_state:
    st.session_state.log_history = []
    
# Barra Lateral para Configuração do Agente
with st.sidebar:
    st.header("Configuração do Agente")
    
    # Use quando em ambiente de desenvolvimento
    # # Campo para inserir a chave da API
    api_key = st.text_input(
        "Chave da API GEMINI",
        type="password",
        placeholder="Insira sua chave de API aqui"
    )
    # Use quando em ambiente de produção
    # A chave de API será lida dos segredos do Streamlit
    # api_key = st.secrets.get("GEMINI_API_KEY")

    st.header("Fonte de Dados")
    
    input_method = st.radio(
        "Escolha o metódo de entrada de dados:",
        ("URL de arquivo .zip","Fazer upload de arquivos.")
    )
    
    file_url = None
    uploaded_files = None
    
    if input_method == "URL de arquivo .zip":
        default_url = "https://github.com/grupo274/pre-projeto-i2a2/raw/refs/heads/thiago/projeto_i2a2_thiago/dataset/compactado/202401_NFs.zip"
        file_url = st.text_input(
            "URL do arquivo .zip",
            help="Insira uma URL pública publicada em outro site contendo uma base de dados com arquivo CSV aqui",
            value = default_url
        )
    else:
        uploaded_files = st.file_uploader(
            "Carregue seus arquivos (.csv ou .zip)",
            type=['csv', 'zip'],
            accept_multiple_files=True
        )
        
    if st.button("Inicializar Agente", use_container_width=True):
        if not api_key:
            st.error("Chave API não encontrada\nPor favor, contate a equipe de desenvolvimento.")
        elif not file_url and not uploaded_files:
            st.error("Por favor, insira a URL do arquivo CSV na barra lateral.")
        else:
            files_are_valid = True
            
            if uploaded_files:
                total_size = 0
                
                for file in uploaded_files:
                    total_size += file.size
                    if file.size > MAX_FILE_SIZE_BYTES:
                        files_are_valid = False
                        st.error(f"❌ Erro: O arquivo '{file.name}' ({file.size / 1024 / 1024:.2f} MB) excede o limite de {MAX_FILE_SIZE_MB} MB por arquivo.")
            
                if total_size > MAX_TOTAL_SIZE_BYTES:
                    files_are_valid = False
                    st.error(f"❌ Erro: O tamanho total dos arquivos ({total_size / 1024 / 1024:.2f} MB) excede o limite total de {MAX_TOTAL_SIZE_MB} MB.")              
            
            if files_are_valid:
                with st.spinner("Conectando ao agente e carregando dados..."):
                    controller = st.session_state.agente_controller
                    status_message = controller.initialize_agente(
                        api_key=api_key,
                        file_url=file_url,
                        uploaded_files=uploaded_files
                    )
                    
                    if "✅" in status_message:
                        st.session_state.agent_initialized = True
                        st.success(status_message)
                        st.session_state.messages = [
                            {"role": "assistant", "content": "Olá! Estou pronto para responder suas perguntas sobre os dados carregados."}
                        ]
                        st.session_state.log_history = []
                    else:
                        st.session_state.agent_initialized = False
                        st.error(status_message)
                    
    # Histórico de Conversa
    st.header("Histórico de Conversa")
    if st.session_state.agent_initialized:       
        # Exibe os últimos 5 logs de conversa
        display_logs = st.session_state.log_history[-5:]
        # Blocos de Log
        for log in reversed(display_logs):
            with st.expander(f"P: {log['pergunta'][:30]}"):
                st.markdown(f"**Você:**\n> {log['pergunta']}")
                st.markdown(f"**Agente:**\n> {log['resposta']}")
        log_data_download = formatar_logs_para_dowload(st.session_state.log_history)
        # Botão download
        if st.session_state.log_history:
            st.download_button(
            label="📥 Baixar Histórico de Conversa (.txt)",
            data=log_data_download.encode('utf-8'),
            file_name="historico_conversa.txt",
            mime="text/plain",
            use_container_width=True
            )
        else:
            st.info("Nenhum histórico de conversa disponível para download.")
    else:
        st.info("O histórico da conversa aparecerá aqui.")
                      
# Interface de Chat Principal
st.header("Converse com o Agente")

if not st.session_state.agent_initialized:
    st.warning("Por favor, inicialize o agente na barra lateral antes de fazer perguntas.")
else:
    # Exibe mensagens anteriores
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Campo de entrada para perguntas
    user_input = st.chat_input("Faça uma pergunta sobre os dados...")
        
    if user_input:
        # Adiciona a pergunta do usuário às mensagens
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                # Processa a pergunta através do controlador
                controller = st.session_state.agente_controller
                
                response = controller.ask_question(user_input)
                
                # St.markdown renderiza texto e blocos de código formatados
                st.markdown(response)
        
        # Adiciona a resposta do agente ao histórico
        st.session_state.messages.append({"role": "assistant", "content": response})
        # Salva mensagem no histórico de logs
        st.session_state.log_history.append({
            "pergunta": user_input,
            "resposta": response
        })
        # Atualiza a página para atualizar o historico de mensagens na barra lateral
        st.rerun()

