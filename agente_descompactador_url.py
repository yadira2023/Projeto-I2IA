'''
Este agente é responsável por baixar contedo do .zip a partir de uma URL, descompactar os arquivos e carregar os CSVs em DataFrames do Pandas.
Ler o conteúdo dos arquivos CSV em memória, sem salvar no disco, e retornar uma lista de DataFrames.
Decompactar os arquivos CSV de dentro do .zip e carregar os dados em DataFrames.
Retorna uma lista de DataFrames contendo os dados dos arquivos CSV encontrados.
'''
import os
import zipfile
import tarfile
import requests
import pandas as pd
from io import BytesIO # Para ler dados binários em memória como um arquivo
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

def descompactar_arquivos(file_url: str):
    """
    Baixai um arquivo .zip em uma URl, descompacta os arquivos CSV em memoria e retorna como lsita de DF pandas
    """
    dataframes_csv = []

    print(f"Buscando arquivos compactados em: {file_url}")

    try:
        # Baixa o arquivo compactado da URL
        response = requests.get(file_url)
        response.raise_for_status()  # Verifica se a requisição foi bem-sucedida

        # Abrir o arquivo .zip a partir do conteúdo em memória
        with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
            # Itera sobre cada arquivo dentro do ZIP
            for info in zip_ref.infolist():
                # verifica se nao nao é um diretório
                if info.filename.lower().endswith('.csv') and not info.is_dir():
                    print(f"  ✅ Encontrado CSV no ZIP: {info.filename}")
                    # Abre o arquivo CSV dentro do ZIP e addiciona ao DataFrame
                    with zip_ref.open(info.filename) as file:
                        df = pd.read_csv(file)
                        dataframes_csv.append(df)
                        print(f"    - Carregado {info.filename} (linhas: {len(df)})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao baixar o arquivo da URL: {e}")
        return [] # Retorna lista vazia em caso de erro de download
    except zipfile.BadZipFile:
        print(f"❌ O arquivo na URL não é um ZIP válido ou está corrompido.")
        return []
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado ao processar o arquivo: {e}")
        return []

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