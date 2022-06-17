import requests
import json

pat = "tesq37sf63rsuilmzadoeuxo2lguloiwj5xlwifbjv3rhmub2tkq"

# Url de API da build que estiver sendo executada
url = f"https://dev.azure.com/alelo/PrePagos-2.0/_apis/build/builds/141942/timeline?api-version=6.0"

response = (json.loads(requests.get(url, auth=("Basic", pat))._content))["records"]

# Loop com a intenção de procurar a seção que extrai os dados do estágio atual (PRD ou PR), que serão os dados que precisamos dos aprovadores
for item in response:
    if item["identifier"] == "deploy_hml":
        stageID = item["id"]

print(stageID)

# API de consulta da Microsoft, esta Url direciona para a consulta do projeto em específico
url = "https://dev.azure.com/alelo/_apis/Contribution/HierarchyQuery/project/PrePagos-2.0?api-version=6.1-preview.1"

# Aqui considera os dados que serão enviados para o post dentro do projeto que estamos
# É necessário enviar o BuildID (especifica a pipe em execução) e o StageID (especifica o estágio que estamos procurando)
payload = {
    "contributionIds": [
        "ms.vss-build-web.checks-panel-data-provider"
    ],
    "dataProviderContext": {
        "properties": {
            "buildId": "141942", # determina a pipeline
            "stageIds": f"{stageID}", # determina o estágio
            "checkListItemType": 1,
            "sourcePage": {
                "url": f"https://dev.azure.com/alelo/PrePagos-2.0/_build/results?buildId=141942&view=results",
                "routeId": "ms.vss-build-web.ci-results-hub-route",
                "routeValues": {
                    "project": "PrePagos-2.0",
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
response = json.loads(requests.post(url, auth=("Basic", pat), data=data, headers=headers)._content)

# No corpo de resposta do post encontramos quem foram os aprovadores do estágio atual (PRD ou PR)
aprovadores = response["dataProviders"]["ms.vss-build-web.checks-panel-data-provider"][0]["approvals"][0]["steps"]

print(aprovadores[0])

msg = ""
for aprovador in aprovadores:
    temp = f"Aprovador: {aprovador['actualApprover']['displayName']}; Email: {aprovador['actualApprover']['uniqueName']}; Responsável: {aprovador['assignedApprover']['displayName']}; Comentário: {aprovador['comment']}\n"
    msg += temp
