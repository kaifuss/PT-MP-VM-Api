import glob

# Поиск файлов по маске
file_paths = glob.glob('/var/lib/deployer/role_instances/core*/params.yaml')

# Вывод найденных файлов
for file_path in file_paths:
    with open(file_path, 'r') as file:
        for line in file:
            if 'ClientSecret' in line:
                client_secret = line.split(':')[1].strip()
                print(client_secret)