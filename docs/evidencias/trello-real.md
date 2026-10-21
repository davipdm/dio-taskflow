# Validação no Trello real

Data: 21/10/2026, America/Sao_Paulo.

Credenciais lidas exclusivamente do .env local, sem exposição dos valores.
O quadro configurado foi encontrado. As três listas exigidas estavam ausentes
e foram criadas: A fazer, Em andamento e Concluído.

Execução: `python scripts/smoke_trello.py --write`.

- Conexão, quadro e três listas: OK.
- Leitura inicial: OK, zero cards nas três listas.
- Card identificado com prefixo [TESTE TaskFlow] criado: OK.
- Movimento para Em andamento e confirmação por releitura: OK.
- Movimento para Concluído e confirmação por releitura: OK.
- Vencimento local retornado: 2026-10-21T23:59:00-03:00.

O card ficou em Concluído como evidência. Pode ser arquivado manualmente.
Este teste exercita as funções Python e a API real; não comprova a escolha
correta de ferramentas pelo Gemini. A chamada de conversa via ADK foi tentada
duas vezes e retornou HTTP 503 UNAVAILABLE por alta demanda do modelo.
Nenhum card adicional foi criado nessas tentativas de conversa.
