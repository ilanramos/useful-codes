import requests
import json

# Url de API da build que estiver sendo executada
url = f"$(System.CollectionUri)$(System.TeamProject)/_apis/build/builds/$(Build.BuildID)/timeline?api-version=6.0"

response = (json.loads(requests.get(url, auth=("Bearer", "$(System.AccessToken)"))._content))["records"]

# Loop com a intenção de procurar a seção que extrai os dados do estágio atual, que serão os dados que precisamos dos aprovadores
for item in response:
    if item["identifier"] == "$(System.Stagename)":
        stageID = item["id"]

# API de consulta da Microsoft, esta Url direciona para a consulta do projeto em específico
url = "$(System.CollectionUri)_apis/Contribution/HierarchyQuery/project/$(System.TeamProject)?api-version=6.1-preview.1"

# Aqui considera os dados que serão enviados para o post dentro do projeto que estamos
# É necessário enviar o BuildID (especifica a pipe em execução) e o StageID (especifica o estágio que estamos procurando)
payload = {
    "contributionIds": [
        "ms.vss-build-web.checks-panel-data-provider"
    ],
    "dataProviderContext": {
        "properties": {
            "buildId": "$(Build.BuildID)", # determina a pipeline
            "stageIds": f"{stageID}", # determina o estágio
            "checkListItemType": 1,
            "sourcePage": {
                "url": f"$(System.CollectionUri)$(System.TeamProject)/_build/results?buildId=$(Build.BuildID)&view=results",
                "routeId": "ms.vss-build-web.ci-results-hub-route",
                "routeValues": {
                    "project": "$(System.TeamProject)",
                    "viewname": "build-results",
                    "controller": "ContributedPage",
                    "action": "Execute"
                }
            }
        }
    }
}

data = json.dumps(payload)
headers = {"Content-Type": "application/json", "Accept": "text/plain"}

# Preenche com os dados do payload o query da Microsoft em específico para este projeto
response = json.loads(requests.post(url, auth=("Basic", "$(System.AccessToken)"), data=data, headers=headers)._content)

# No corpo de resposta do post encontramos quem foram os aprovadores do estágio atual
aprovadores = response["dataProviders"]["ms.vss-build-web.checks-panel-data-provider"][0]["approvals"][0]["steps"]

msg = ""
for aprovador in aprovadores:
    temp = f"Aprovador: {aprovador['actualApprover']['displayName']}; Email: {aprovador['actualApprover']['uniqueName']}; Responsável: {aprovador['assignedApprover']['displayName']}; Comentário: {aprovador['comment']}\n"
    msg += temp