# Validação no quadro real

Esta etapa exige as contas e credenciais do proprietário. Testes offline não
substituem a demonstração Trello + Gemini.

1. Preencha `.env` e execute `scripts/check_config.py`.
2. Execute `scripts/smoke_trello.py`, somente leitura. Deve confirmar quadro
   e três listas. Essa etapa não chama o Gemini.
3. Execute `scripts/smoke_trello.py --write` para criar um card de teste e
   verificar as mudanças nas três listas. O card fica em Concluído.
4. Na raiz, execute `.venv\Scripts\adk.exe web --host 127.0.0.1 --port 8000`.
5. Selecione `taskflow`, envie “Oi” e confira a data da primeira resposta.
6. Peça “Crie Revisar projeto, descrição Conferir README, para hoje às 18:00”.
   Confira título, descrição e dia/hora no Trello.
7. Peça para listar A fazer, começar Revisar projeto e depois concluí-la.
   Compare o resultado com o quadro e o indicador de vencimento concluído.
8. Teste também “concluído” com acento e um nome ambíguo. O agente não deve
   escolher arbitrariamente entre cards de mesmo nome.

## Evidências para portfólio

Capture a conversa ao lado do quadro, mostrando criação, listagem e mudança
de status. Não inclua `.env`, páginas de tokens, chaves ou dados pessoais.
Registre data, modelo selecionado e resultado observado. Se a cota acabar,
registre a limitação e continue apenas os testes offline.

Atualize `docs/evidencias/README.md` somente após executar a integração real.
Não apresente captura montada nem resultado esperado como teste executado.
