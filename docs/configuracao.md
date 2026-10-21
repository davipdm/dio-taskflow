# Configurar Trello e Gemini

## 1. Criar o quadro

Acesse [Trello](https://trello.com/) e entre na sua conta. Crie um quadro
privado chamado **DIO TaskFlow**, com três listas abertas: **A fazer**,
**Em andamento** e **Concluído**. Não são necessários cards iniciais.

## 2. Registrar o aplicativo e obter chave/token

1. Abra o [portal de aplicativos Trello](https://trello.com/apps/admin).
2. Crie um Power-Up para seu workspace, preenchendo nome, contato e autor.
3. Abra a área de autenticação Trello e gere a API Key.
4. Use o link **Token** ao lado da chave para autorizar o aplicativo.
5. Confira se a autorização permite leitura e escrita; copie o token para
   `TRELLO_TOKEN` no `.env` local. Coloque a API Key em `TRELLO_API_KEY`.

O portal pode mudar os nomes das abas. A [documentação da Atlassian](https://developer.atlassian.com/cloud/trello/guides/rest-api/api-introduction/)
é a referência para o fluxo atual. No fluxo de token pessoal, chave e token
são suficientes; não é necessário inventar um segredo OAuth. Se houver um
segredo para seu aplicativo, pode preencher `TRELLO_API_SECRET` localmente.
Não é necessário instalar ou publicar um Power-Up na loja para usar este script.

Não copie tokens para o chat, commits ou prints. Verifique alcance e duração
da autorização no Trello; revogue o token quando não precisar mais dele.

## 3. Chave Gemini

Abra [Google AI Studio — API Keys](https://aistudio.google.com/apikey), entre
com sua conta Google e crie uma chave em um projeto permitido pela sua conta.
Preencha `GOOGLE_API_KEY` no `.env`. Mantenha
`GOOGLE_GENAI_USE_VERTEXAI=FALSE` para usar este fluxo de AI Studio.
Confira os modelos disponíveis na sua conta e ajuste `GEMINI_MODEL` se necessário.
Não ative cobrança por conta deste tutorial; se não houver cota gratuita
disponível, os testes locais continuam funcionando sem o Gemini.

## 4. Arquivo local

O `.env` preparado nesta máquina tem as mesmas variáveis do `.env.exemplo`,
com os campos de chave/token vazios. Preencha-o no editor local e salve.

```dotenv
GOOGLE_API_KEY=
TRELLO_API_KEY=
TRELLO_TOKEN=
TRELLO_BOARD_NAME=DIO TaskFlow
APP_TIMEZONE=America/Sao_Paulo
```

O programa lê o `.env` da raiz usando caminho absoluto. Variáveis já exportadas
no ambiente têm prioridade. Reinicie `adk web` após mudar a configuração.
Para conferir sem expor os valores:

```powershell
.\.venv\Scripts\python.exe scripts/check_config.py
```

Se o quadro tiver nome duplicado, use seu ID em `TRELLO_BOARD_ID`. Para obtê-lo,
abra o quadro no navegador e consulte sua exportação JSON, quando disponível,
sem compartilhar o conteúdo completo (pode conter dados pessoais). Também é
possível consultá-lo pela API conforme a documentação Trello.

## 5. Próximo passo

Execute o teste somente de leitura e siga [o roteiro de validação](validacao.md).
Se uma falha ocorrer, confira quadro/listas, permissões, cota e conexão.
O programa omite mensagens técnicas que poderiam conter URLs com tokens.
