import requests, json, os
from git import Repo

GIT_DIRECTORY = "./modules"


def get_json_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_and_store_module_list():

    modules = []
    starting_url = "https://registry.terraform.io/v1/modules?limit=100"
    response = get_json_from_url(starting_url)

    modules.extend(response['modules'])
    with open('data/modules-offset-0.json', 'w') as fout:
        json.dump(modules, fout)



    while response['meta']['next_offset']:
        offset = response['meta']['next_offset']
        url = response['meta']['next_url']
        print(url)
        response = get_json_from_url(url)

        modules.extend(response['modules'])

        filename = f"data/modules-offset-{offset}.json"
        with open(filename, 'w') as fout:
            json.dump(response['modules'], fout)

    with open('data/modules.json', 'w') as fout:
        json.dump(modules, fout)


def parse_file(modules, completed):
    for module in modules:
        id = module['id'].replace('/', '-')

        if id in completed:
            continue

        if module['verified']:
            try:
                os.mkdir(f'{GIT_DIRECTORY}/verified/{id}')
            except FileExistsError:
                pass

            try:
                Repo.clone_from(module['source'], f'{GIT_DIRECTORY}/verified/{id}')
                with open('./modules/progress.txt', 'a') as file:
                    file.write(id + '\n')
            except Exception as e:
                print(e)
                print("id = " + id)
                continue

        else:
            try:
                os.mkdir(f'{GIT_DIRECTORY}/unverified/{id}')
            except FileExistsError:
                pass

            try:
                Repo.clone_from(module['source'], f'{GIT_DIRECTORY}/unverified/{id}')
                with open('./modules/progress.txt', 'a') as file:
                    file.write(id + '\n')
            except Exception as e:
                print(e)
                print("id = " + id)
                continue


def read_modules_json():
    directory = 'data/'
    files = [pos_json for pos_json in os.listdir(directory) if pos_json.endswith('.json')]

    with open('./modules/progress.txt') as completed:
        completed = completed.read()

    for file in files:
        with open(f'{directory}{file}', 'r') as f:
            data = json.load(f)
            parse_file(data, completed)


if __name__ == "__main__":
    # get_and_store_module_list()
    read_modules_json()
