# Encerramento do projeto

Data: 21/10/2026 (America/Sao_Paulo).

- ADK 2.12.0 carregou o agente e suas quatro ferramentas.
- 17 testes offline aprovados; dependências verificadas com pip check.
- Trello real: quadro encontrado, listas criadas, card de teste criado,
  listado e movido para Em andamento e Concluído, com confirmação por releitura.
- Vencimento local conferido em America/Sao_Paulo.
- Gemini: duas tentativas de conversa retornaram HTTP 503 por alta demanda.
  A conversa completa com o modelo não foi validada; essa limitação foi mantida.
- Configuração e credenciais pessoais não integram o repositório público.

O código e as evidências permanecem no GitHub. A limpeza local autorizada
remove a pasta do projeto, seu ambiente virtual e o .env; não revoga tokens
no Trello ou no Google. O card de teste permanece no quadro como evidência.

## Reproduzir depois da limpeza

```powershell
git clone https://github.com/davipdm/dio-taskflow.git
cd dio-taskflow
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
Copy-Item .env.exemplo .env
```

Use Python 3.11 ou superior (ambiente validado com 3.12). Preencha novamente
as credenciais localmente e confira o nome ou ID do seu quadro. Depois:

```powershell
.\.venv\Scripts\python.exe scripts/check_config.py
.\.venv\Scripts\python.exe scripts/smoke_trello.py
.\.venv\Scripts\adk.exe web --host 127.0.0.1 --port 8000
```

Siga [o roteiro de validação](validacao.md) para registrar uma conversa com
Gemini quando o modelo estiver disponível. Não trate os testes offline ou a
validação direta da API como evidência dessa conversa.
