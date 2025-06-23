import os
import zipfile
import tarfile
import pandas as pd
from io import BytesIO # Para ler dados binários em memória como um arquivo
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

def descompactar_arquivos(diretorio_origem):
    
    dataframes_csv = []

    print(f"Buscando arquivos compactados em: {diretorio_origem}")

    # Cria o diretório de origem se não existir para evitar erro de listdir
    if not os.path.exists(diretorio_origem):
        print(f"❌ Diretório de origem não encontrado: {diretorio_origem}")
        return pd.DataFrame()

    for nome_arquivo_compactado in os.listdir(diretorio_origem):
        caminho_arquivo_compactado = os.path.join(diretorio_origem, nome_arquivo_compactado)

        if not os.path.isfile(caminho_arquivo_compactado):
            continue

        print(f"\nProcessando arquivo: {nome_arquivo_compactado}")

        try:
            # --- Lógica para .zip ---
            if zipfile.is_zipfile(caminho_arquivo_compactado):
                with zipfile.ZipFile(caminho_arquivo_compactado, 'r') as zip_ref:
                    # Itera sobre cada arquivo dentro do ZIP
                    for info in zip_ref.infolist():
                        if info.filename.lower().endswith('.csv'):
                            print(f"  ✅ Encontrado CSV no ZIP: {info.filename}")
                            with zip_ref.open(info.filename) as file:
                                # Lê o conteúdo do CSV em memória
                                df = pd.read_csv(BytesIO(file.read()))
                                dataframes_csv.append(df)
                                print(f"    - Carregado {info.filename} (linhas: {len(df)})")

            # --- Lógica para .tar.gz ou .tgz ---
            elif tarfile.is_tarfile(caminho_arquivo_compactado):
                with tarfile.open(caminho_arquivo_compactado, 'r:*') as tar_ref:
                    # Itera sobre cada membro dentro do TAR
                    for member in tar_ref.getmembers():
                        # Certifica-se de que é um arquivo regular e é um CSV
                        if member.isfile() and member.name.lower().endswith('.csv'):
                            print(f"  ✅ Encontrado CSV no TAR: {member.name}")
                            with tar_ref.extractfile(member) as file:
                                # Lê o conteúdo do CSV em memória
                                if file: # Garante que o arquivo foi extraído corretamente (não None)
                                    df = pd.read_csv(BytesIO(file.read()))
                                    dataframes_csv.append(df)
                                    print(f"    - Carregado {member.name} (linhas: {len(df)})")
                                else:
                                    print(f"    - ⚠️ Não foi possível ler {member.name} do arquivo tar.")

            else:
                print(f"  ❌ Tipo de arquivo não suportado ou arquivo não compactado: {nome_arquivo_compactado}")

        except Exception as e:
            print(f"❌ Erro ao processar {nome_arquivo_compactado}: {e}")

 
    return dataframes_csv

def preparar_amostras_para_agente(lista_de_dataframes):
    
    amostras_para_agente = []
    
    for i, df in enumerate(lista_de_dataframes):
        # Convertendo as 5 primeiras linhas para string.
        # Você pode usar .to_dict('records') para JSON ou .to_markdown() para texto formatado.
        primeiras_linhas_str = df.head(2).to_string(index=False) # Ou .to_string(index=False)

        amostra_info = {
            'indice_dataframe':i, # Identificador único para cada DF
            'colunas': df.columns.tolist(),
            'total_linhas': len(df),
            'primeiras_5_linhas': primeiras_linhas_str,
           
        }
        amostras_para_agente.append(amostra_info)
        
    return amostras_para_agente



def agrupar_arquivos(chave,df):
 
    prompt_template = PromptTemplate(
        input_variables=["dados"],
        template="""
        Você é um agente agrupador de arquivos.

        Vai receber algumas uma lista das primeiras linhas de um conjunto de dados.
        Você vai desenvolver o codigo python para fazer um join entre os arquivos.
        Na coluna indice_dataframe tem o indice de cada dataframe
        Se não achar colunas iguais em todos arquivos para fazer o join voce pode só concatenar eles.
        
        O codigo deve necessariamente retornar um dataframe com o resultado do join ou do concant.
        
        Aqui esta os  dataframes:

        {dados}

        O nome da variavel da lista de datafremes é: lista_df


        """
        )
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=chave)

    chain = prompt_template | llm
    resposta = chain.invoke({"dados": df})
  

    return resposta.content
'''

import os
import zipfile
import tarfile

def descompactar_arquivos(diretorio_origem, diretorio_destino):
    arquivos_descompactados = []

    for nome_arquivo in os.listdir(diretorio_origem):
        caminho_arquivo = os.path.join(diretorio_origem, nome_arquivo)

        # Ignora se não for arquivo
        if not os.path.isfile(caminho_arquivo):
            continue

        try:
            # .zip
            if zipfile.is_zipfile(caminho_arquivo):
                with zipfile.ZipFile(caminho_arquivo, 'r') as zip_ref:
                    zip_ref.extractall(diretorio_destino)
                    arquivos_descompactados.extend(zip_ref.namelist())

            # .tar.gz ou .tgz
            elif tarfile.is_tarfile(caminho_arquivo):
                with tarfile.open(caminho_arquivo, 'r:*') as tar_ref:
                    tar_ref.extractall(diretorio_destino)
                    arquivos_descompactados.extend(tar_ref.getnames())

            else:
                print(f"❌ Tipo de arquivo não suportado ou arquivo não compactado: {nome_arquivo}")

        except Exception as e:
            print(f"❌ Erro ao descompactar {nome_arquivo}: {e}")

    return arquivos_descompactados
'''