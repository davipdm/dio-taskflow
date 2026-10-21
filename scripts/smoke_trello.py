"""Validação real: leitura por padrão; escrita somente com --write."""

import argparse
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from taskflow.tools import get_service


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Cria um card de teste e o move até Concluído; deixa-o como evidência.")
    args = parser.parse_args()
    try:
        service = get_service()
        board = service.board()
        service.lists(board)
        print("Conexão, quadro e três listas: OK")
        print("Leitura de tarefas: OK; quantidade:", len(service.list_tasks()))
        if args.write:
            now = datetime.now(service.zone)
            card = service.add("[TESTE TaskFlow] " + now.isoformat(timespec="seconds"),
                               "Card criado pela validação de integração. Pode ser arquivado manualmente.",
                               now.date().isoformat())
            print("Criação: OK; card:", card["id"])
            for status in ("Em andamento", "Concluído"):
                service.move(card["id"], status)
                listed = service.list_tasks(status)
                if not any(item["id"] == card["id"] for item in listed):
                    raise RuntimeError("Movimentação não confirmada")
                print("Movimentação e releitura:", status, "OK")
            print("Vencimento local:", card["vencimento_local"])
        return 0
    except Exception:
        print("Falha de integração. Confira .env, permissões, quadro e listas. Nenhum segredo será exibido.")
        print("Se houve escrita, confira o quadro antes de repetir: uma falha de rede pode ocorrer após a criação.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
