'''
Lida com arquivos carregados pelo usuário, processa e executa perguntas sobre os dados.
Procesa .csv individuais ou aquivos compactados (.zip) contendo múltiplos .csv.
Todo o processamento é feito em memória, sem salvar arquivos intermediários no disco.
'''

import pandas as pd
import zipfile
from io import BytesIO

def processar_arquivo_upload(lista_de_arquivos_upload):
    """
    Processa uma lista de arquivos CSV ou ZIP carregados pelo usuário.
    
    Args:
        lista_de_arquivos_upload (list): Lista de arquivos carregados pelo usuário.
        
    Returns:
        list: Uma lista de DataFrames do Pandas, um para cada arquivo CSV encontrado.
    """
    dataframes_csv = []
    if not lista_de_arquivos_upload:
        print("Nenhum arquivo carregado.")
        return []

    for uploaded_file in lista_de_arquivos_upload:
        file_name = uploaded_file.name
        print(f"Processando arquivo: {file_name}")
        
        try:
            # Verifica se o arquivo é um ZIP
            if file_name.lower().endswith('.zip'):
                with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                    for info in zip_ref.infolist():
                        # Pega todos os .csv em pastas e subpastas
                        if info.filename.lower().endswith('.csv') and not info.is_dir():
                            print(f" ✅ Encontrado CSV no ZIP: {info.filename}")
                            with zip_ref.open(info.filename) as file_in_zip:
                                df = pd.read_csv(file_in_zip)
                                dataframes_csv.append(df)
                                print(f"    - Carregando {info.filename} (linhas: {len(df)})")
            elif file_name.lower().endswith('.csv'):
                print(f"    ✅ Lendo arquivo CSV: {file_name}")
                df=pd.read_csv(uploaded_file)
                dataframes_csv.append(df)
                print(f"    - Carregado {file_name} (linhas: {len(df)})")
        except Exception as e:
            print(f"❌ Erro ao processar o arquivo {file_name}: {e}")
            raise e
        
    return dataframes_csv