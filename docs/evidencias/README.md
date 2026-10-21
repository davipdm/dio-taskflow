# Evidências

Data de preparação: 21/10/2026, America/Sao_Paulo.

| Verificação | Situação |
| --- | --- |
| Ambiente virtual e dependências | Instalados localmente |
| Carregamento do agente e quatro ferramentas | Verificado sem chamada ao modelo |
| Integridade das dependências (`pip check`) | Sem dependências quebradas |
| ADK Web em localhost | Interface aberta, taskflow reconhecido; [captura real](adk-web.jpg) |
| Testes offline | Saída em [testes.txt](testes.txt) |
| Trello real: criar, listar e mover | Validado; [registro](trello-real.md) |
| Conversa com Gemini | Duas tentativas retornaram HTTP 503; [registro](gemini.txt) |
| Prints da integração real | Pendentes |

O código pode ser revisado e testado offline. O Trello real foi validado. Ainda falta
a conversa completa no ADK Web com Gemini, indisponível nas duas tentativas. Nenhuma chave foi solicitada pelo
chat e nenhuma integração real foi simulada como se tivesse sido executada.

A captura mostra somente a interface carregada, antes das credenciais. Não
representa conversa com Gemini nem operação no Trello.
