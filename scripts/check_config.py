"""Diagnóstico local sem exibir valores e sem fazer chamadas de rede."""

from pathlib import Path
import os
import sys
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=False)


def main():
    missing = []
    for name in ("GOOGLE_API_KEY", "TRELLO_API_KEY", "TRELLO_TOKEN"):
        present = bool(os.getenv(name, "").strip())
        print(f"{name}: {'preenchida' if present else 'PENDENTE'}")
        if not present:
            missing.append(name)
    print("TRELLO_API_SECRET: " + ("preenchido" if os.getenv("TRELLO_API_SECRET") else "opcional no fluxo de token pessoal"))
    try:
        ZoneInfo(os.getenv("APP_TIMEZONE", "America/Sao_Paulo"))
    except ZoneInfoNotFoundError:
        print("APP_TIMEZONE: inválido")
        return 1
    print("Quadro: " + ("configurado por ID" if os.getenv("TRELLO_BOARD_ID") else "selecionado pelo nome do .env"))
    print("Nenhum segredo foi exibido. A presença de uma chave não confirma sua validade.")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
