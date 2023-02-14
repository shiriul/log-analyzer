import click
import requests
from PyInquirer import style_from_dict, Token, prompt
from prettytable import PrettyTable

API_URL = "http://localhost:8000/targets"
answer_style = style_from_dict({
        Token.QuestionMark: '#E91E63 bold',
        Token.Selected: '#673AB7 bold',
        Token.Instruction: '',  # default
        Token.Answer: '#2196f3 bold',
        Token.Question: '',
})

@click.group()
def cli():
    pass

def get_input_questions():
    questions = [
        {
            'type': 'list',
            'name': 'target_system',
            'message': 'Choose the target system:',
            'choices': ['HDFS', 'OpenStack']
        },
        {
            'type': 'input',
            'name': 'target_server_list',
            'message': 'Enter the target server list (comma-separated):',
        },
        {
            'type': 'input',
            'name': 'target_log_path',
            'message': 'Enter the log_path of target system:',
        }
    ]
    return questions

def get_target_system_id(url):
    targets = requests.get(url).json()

    id_list = []
    for target in targets:
        id_list.append(target["id"])

    questions = [
        {
            'type': 'list',
            'name': 'target_system_id',
            'message': 'Choose the target system id:',
            'choices': id_list
        }
    ]
    return questions

@cli.command()
def create_target():
    questions = get_input_questions()
    answers = prompt(questions, style=answer_style)

    target_server_list = answers['target_server_list'].split(',')

    url = API_URL
    data = {
        'target_system': answers['target_system'],
        'server_list': target_server_list,
        'log_path': answers['target_log_path']
    }
    response = requests.post(url, json=data)

    if response.status_code == 200:
        click.echo(f'Successfully created target for {answers["target_system"]} with servers: {target_server_list}')
    else:
        click.echo(f'Failed to create target. Response code: {response.status_code}')

@cli.command()
def list_targets():
    url = API_URL
    response = requests.get(url)

    if response.status_code == 200:
        table = PrettyTable(header_style='upper', field_names=['ID', 'Target System', 'Server List', 'Log Path'])
        table.align['Target System'] = "l"
        table.align['Server List'] = "l"
        targets = response.json()
        for target in targets:
            id = target["id"]
            target_system = target["target_system"]
            server_list = target["server_list"]
            log_path = target["log_path"]
            table.add_row([id, target_system, server_list, log_path])

        print(table)

    else:
        click.echo(f'Failed to retrieve targets. Response code: {response.status_code}')

@cli.command()
def get_target():
    url = API_URL

    questions = get_target_system_id(url)
    answers = prompt(questions, style=answer_style)

    url = url + "/" + answers["target_system_id"]
    response = requests.get(url)

    if response.status_code == 200:
        table = PrettyTable(header_style='upper', field_names=['ID', 'Target System', 'Server List', 'Log Path'])
        table.align['Target System'] = "l"
        table.align['Server List'] = "l"
        target = response.json()
        
        id = target["id"]
        target_system = target["target_system"]
        server_list = target["server_list"]
        log_path = target["log_path"]
        table.add_row([id, target_system, server_list, log_path])

        print(table)

    else:
        click.echo(f'Failed to retrieve targets. Response code: {response.status_code}')

@cli.command()
def update_target():
    print("hello")

@cli.command()
def delete_target():
    url = API_URL

    questions = get_target_system_id(url)
    answers = prompt(questions, style=answer_style)

    url = url + "/" + answers["target_system_id"]
    response = requests.delete(url)

    if response.status_code == 200:
        click.echo(f'Successfully delete target {answers["target_system_id"]}')
    else:
        click.echo(f'Failed to delete target. Response code: {response.status_code}')


if __name__ == '__main__':
    cli()
