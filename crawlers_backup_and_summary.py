import glob
import subprocess
import os
import json
import pandas as pd
import datetime
from tqdm import tqdm
import argparse

# PARÂMETROS -----------------------------------------------------

# pasta onde os backups são salvos
backups_folder_path = '/dados01/workspace/ufmg_2021_c01/backup_crawlers/'

# Caminho para o novo arquivo gerado listando as coletas já feitas
csv_filepath = '/dados01/workspace/ufmg_2021_c01/backup_crawlers/crawlers_summary.csv'

# Caminho para o arquivo do sqlite com os dados das coletas
sqlite_filepath = '/dados01/workspace/ufmg_2021_c01/C01/db.sqlite3'

# qtde de dias de backup que serão mantidos
days_to_keep = 3

# padrões de path até os arquivos instances.json
instance_path_patterns = [
    '/datalake/ufmg/webcrawlerc01/*/instances.json', 
    '/datalake/ufmg/webcrawlerc01/*/*/instances.json', 
    '/datalake/ufmg/webcrawlerc01/realizacaof01/*/*/instances.json'
]

# padrões de path até os json com as configurações das coletas
config_path_patterns = [
    '/datalake/ufmg/webcrawlerc01/*/config/*.json', 
    '/datalake/ufmg/webcrawlerc01/*/*/config/*.json', 
    '/datalake/ufmg/webcrawlerc01/realizacaof01/*/*/config/*.json'
]

# padrões de path até os diretórios "data" com o conteúdo das coletas
data_path_patterns = [
    '/datalake/ufmg/webcrawlerc01/*/data', 
    '/datalake/ufmg/webcrawlerc01/*/*/data', 
    '/datalake/ufmg/webcrawlerc01/realizacaof01/*/*/data',
]

# -------------------------------------------------------------------

def process_instances_datetimes(instance_path_patterns):
    '''
    Varre os arquivos "instances.json" para obter uma lista com as
    instâncias e suas respectivas data de início e fim.
    Retorna um dict com ID da instância como chave e "started_at" e
    "finished_at" como valores.
    '''
    print('Processando a data das instâncias...')
    filepaths_list = []
    for path_pattern in instance_path_patterns:
        for filepath in glob.glob(path_pattern):
            filepaths_list.append(filepath)
    
    instances_start_end_dates = {}
    for filepath in tqdm(filepaths_list, ncols=100):
        instances_list_json = json.load(open(filepath))
        for instance_id in instances_list_json.keys():
            instances_start_end_dates[instance_id] = instances_list_json[instance_id]

    return instances_start_end_dates


def process_crawler_data_sizes(data_path_patterns):
    print('Processando o tamanho de cada coleta...')
    # monta uma lista com o caminho de todos os diretórios "data"
    data_dir_list = []
    for path_pattern in data_path_patterns:
        for dirpath in glob.glob(path_pattern):
            data_dir_list.append(dirpath)

    # computa o tamanho de cada pasta "data"
    data_sizes = {}
    for dir_path in tqdm(data_dir_list, ncols=100):
        command_output = subprocess.run(["du "+dir_path+" -d 0"], shell=True, stdout=subprocess.PIPE)
        line = command_output.stdout.decode('utf-8').strip('\n')
        parts = line.split('\t')
        size_bytes = int(parts[0])
        dir_path = os.path.dirname(dir_path) # tira o "/data" do path
        data_sizes[dir_path] = size_bytes
    return data_sizes


def process_instances_config(config_path_patterns, instances_start_end_dates, data_sizes):
    all_data = []
    
    print('Processando as configurações de cada instância...')
    filepaths_list = []
    for path_pattern in config_path_patterns:
        for filepath in glob.glob(path_pattern):
            filepaths_list.append(filepath)
            
    for filepath in tqdm(filepaths_list, ncols=100):
        instance_json = json.load(open(filepath))
        try:
            all_data.append({
                'crawler_id': instance_json['crawler_id'], 
                'instance_id': instance_json['instance_id'], 
                'source_name': instance_json['source_name'], 
                'base_url': instance_json['base_url'], 
                'data_path': instance_json['data_path'],
                'started_at': instances_start_end_dates[instance_json['instance_id']]['started_at'],
                'finished_at': instances_start_end_dates[instance_json['instance_id']]['finished_at'],
                'data_size_kbytes': 0
            })
            try:
                all_data[-1]['data_size_kbytes'] = data_sizes[all_data[-1]['data_path']]
            except:
                None
        except:
            # print('ERRO:', filepath)
            None
    return all_data


def summarize_and_save_csv(all_data, csv_filepath=None):
    print('Sumarizando...')
    df = pd.DataFrame(all_data)
    df['started_at'] = df.apply(lambda row: to_datetime(row['started_at']), axis=1)
    df['finished_at'] = df.apply(lambda row: to_datetime(row['finished_at']), axis=1)
    df['duration_seconds'] = df.apply(lambda row: compute_duration(row['started_at'], row['finished_at']), axis=1)
    df['duration_readable'] = df.apply(lambda row: human_readable_duration(row['duration_seconds']), axis=1)
    df['data_size_readable'] = df.apply(lambda row: human_readable_size(row['data_size_kbytes']), axis=1)
    df['category'] = df.apply(lambda row: find_category(row), axis=1)
    
    if csv_filepath != None:
        df.to_csv(csv_filepath, index=False)
    return df


def do_backup(instance_path_patterns, config_path_patterns, backups_folder_path, backup_date_string, days_to_keep, sqlite_filepath):
    print('Realizando backup...')
    # cria o diretório
    current_backup_folder = backups_folder_path+'/backup_'+backup_date_string
    os.system('mkdir '+current_backup_folder)
    
    # copia o sqlite
    os.system('cp '+sqlite_filepath+' '+current_backup_folder)

    # copia os JSONs
    for path_pattern in instance_path_patterns + config_path_patterns:
        os.system('cp --parents '+path_pattern+' '+current_backup_folder)

    # comprime
    new_tar_filepath = os.path.join(backups_folder_path,'backup_'+backup_date_string+'.tar.gz')
    os.system('tar -zcf '+new_tar_filepath+' '+current_backup_folder)

    # remove a pasta que ficou
    os.system('rm -r '+current_backup_folder)

    # remove backups muito antigos
    bk_filenames = list(glob.glob(backups_folder_path+'*.tar.gz'))
    bk_filenames = sorted(bk_filenames, reverse=True)
    for i, filename in enumerate(bk_filenames):
        if i >= days_to_keep:
            os.system('rm '+filename)



def human_readable_size(size, decimal_places=2):
    for unit in ['K','M','G','T']:
        if size < 1000.0:
            break
        size /= 1000.0
    return f"{size:.{decimal_places}f}{unit}"


def human_readable_duration(seconds):
    return str(datetime.timedelta(seconds=seconds))


def find_category(row):
    if 'licitações' in row['source_name'].lower() or \
       'licitação' in row['source_name'].lower() or \
       'licitacoes' in row['source_name'].lower() or \
       'licitaçoes' in row['source_name'].lower() or \
       'licitacao' in row['source_name'].lower():
        return 'Licitações'
    
    if 'contratos' in row['source_name'].lower():
        return 'Contratos'
    
    if 'diários' in row['source_name'].lower() or \
       'diário' in row['source_name'].lower() or \
       'diarios' in row['source_name'].lower() or \
       'diario' in row['source_name'].lower():
        return 'Diários'
    
    if 'transparência' in row['source_name'].lower() or \
       'transparencia' in row['source_name'].lower():
        return 'Transparência'
    
    if 'orçamentária' in row['source_name'].lower() or \
       'orçamentaria' in row['source_name'].lower() or \
       'orcamentaria' in row['source_name'].lower() or \
       'orcamentária' in row['source_name'].lower():
        return 'Leis Orçamentárias'
    
    return 'Outro'


def compute_duration(start_datetime, end_datetime):
    # Computa a duração em segundos entre duas datas
    # start e finish precisam ser do tipo datimetime
    # se necessário converta usando a função to_datetime abaixo
    
    if pd.isnull(start_datetime) or pd.isnull(end_datetime):
        return 0

    start_timestamp = datetime.datetime.timestamp(start_datetime)
    end_timestamp = datetime.datetime.timestamp(end_datetime)
    
    return end_timestamp - start_timestamp


def to_datetime(value):
    if value == None:
        return None
    return datetime.datetime.strptime(value.split('.')[0], '%Y-%m-%d %H:%M:%S')


def main(backups_folder_path, days_to_keep, instance_path_patterns, config_path_patterns, data_path_patterns, csv_filepath, sqlite_filepath):
    backup_date = datetime.datetime.now()
    backup_date_string = backup_date.strftime('%Y-%m-%d')
    
    instances_start_end_dates = process_instances_datetimes(instance_path_patterns)
    data_sizes = process_crawler_data_sizes(data_path_patterns)
    all_data = process_instances_config(config_path_patterns, instances_start_end_dates, data_sizes)
    
    summarize_and_save_csv(all_data, csv_filepath)
    do_backup(instance_path_patterns, config_path_patterns, backups_folder_path, backup_date_string, days_to_keep, sqlite_filepath)

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Varre o diretório das coletas e cria um CSV listando as coletas existentes e faz backup das configurações')
    parser.add_argument('-backups_folder_path', type=str, default=backups_folder_path, help='Caminho para a pasta onde ficam os backups')
    parser.add_argument('-csv_filepath', type=str, default=csv_filepath, help='Path para o arquivo CSV que será criado.')
    parser.add_argument('-sqlite_filepath', type=str, default=sqlite_filepath, help='Path para o arquivo sqlite com os dados dos coletores')

    args = parser.parse_args()
    
    main(args.backups_folder_path, days_to_keep, instance_path_patterns, config_path_patterns, data_path_patterns, args.csv_filepath, args.sqlite_filepath)
    print('Processo concluído.')
