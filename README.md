# Click2call para Asterisk com Python

Este projeto disponibiliza uma API construída em python contendo uma rota para Click2call e listagem de ramais em tempo real. Ela pode ser integrada a qualquer servidor Asterisk.

<b><h3>Requisitos</h3></b>

1. Criar um usuário no Maganer do seu Asterisk conforme abaixo (lembre-se de ajustar para o IP da sua rede):

```
[click2call]
secret=click2callsecret
deny=0.0.0.0/0.0.0.0
permit=127.0.0.1/255.255.255.255
permit=192.168.100.0/255.255.255.0
write=originate,system
```

Você poderá alterar o usuário e senha também.


2. Recarregar o manager:

```bash
[root@server:/etc/asterisk]# rasterisk -x 'manager reload'
```


<b><h3>Deploy</h3></b>

1. Definir as variáveis de ambiente:

```bash
[root@serverapp:/]# cat .env
ASTERISK_IP=
ASTERISK_AMI_PORT=5038
ASTERISK_AMI_USER=
ASTERISK_AMI_PASSWORD=
ENVIRONMENT=dev
PORT=8000
HTTP_AUTH_USER=
HTTP_AUTH_PASSWORD=
```

| Variável | Valores
|-----------|-------|
|ASTERISK_IP|IP do seu servidor Asterisk|
|ASTERISK_AMI_PORT|Porta do manager do seu Asterisk|
|ASTERISK_AMI_USER|Usuário criado no manager|
|ASTERISK_AMI_PASSWORD|Senha do usuário criado no manager|
|ENVIRONMENT|dev ou prod. Quando em ```dev``` qualquer alteração do código é recarregada imediatamente durante a execução do serviço|
|PORT|Porta onde o serviço da API será executado|
|HTTP_AUTH_USER|Usuário de acesso à api|
|HTTP_AUTH_PASSWORD|Senha do usuário de acesso à api|


2. Fazer o build e a inicialização dos serviços:

```bash
docker-compose build
docker-compose up -d
```


<b><h3>Resquests</h3></b>

 - Click2call
  
```bash
curl --request POST \
  --url http://192.168.100.96:8000/click2call \
  --header 'Authorization: Basic c3VwZXJ1c2VyOnN1cGVyc2VjcmV0' \
  --header 'Content-Type: application/json' \
  --data '{
	"src":1000,
	"dst": 1001,
	"context":"from-internal"	
}'
```
Retorno:

```json
{
	"status": "Success",
	"keys": {
		"ActionID": "1",
		"Message": "Originate successfully queued"
	},
	"follows": []
}
```

 - Listagem de ramais e seus status

```bash
curl --request GET \
  --url http://192.168.100.96:8000/get_extensions \
  --header 'Authorization: Basic c3VwZXJ1c2VyOnN1cGVyc2VjcmV0'
```

Retorno


```json
[
	[
		{
			"Privilege": "System",
			"ChannelType": "SIP",
			"Peer": "SIP/1001",
			"PeerStatus": "Reachable",
			"Time": "9",
			"ActionID": "da32dd50-76ba-11ec-b872-0242ac150002"
		}
	],
	[
		{
			"Privilege": "System",
			"ChannelType": "SIP",
			"Peer": "SIP/1000",
			"PeerStatus": "Reachable",
			"Time": "1",
			"ActionID": "da32dd50-76ba-11ec-b872-0242ac150002"
		}
	]
]
```