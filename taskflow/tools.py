"""Ferramentas ADK com conexão centralizada e erros sem URLs ou segredos."""

from datetime import datetime
from functools import wraps
import os
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dotenv import load_dotenv
import requests
from trello import TrelloClient

from .core import TaskFlowError, TaskService

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=False)


class TimeoutSession(requests.Session):
    def request(self, method, url, **kwargs):
        kwargs.setdefault("timeout", 20)
        return super().request(method, url, **kwargs)


def get_service():
    required = ("TRELLO_API_KEY", "TRELLO_TOKEN")
    missing = [key for key in required if not os.getenv(key, "").strip()]
    if missing:
        raise TaskFlowError("Configure no .env: " + ", ".join(missing) + ".")
    client = TrelloClient(api_key=os.environ["TRELLO_API_KEY"],
                          api_secret=os.getenv("TRELLO_API_SECRET") or None,
                          token=os.environ["TRELLO_TOKEN"], http_service=TimeoutSession())
    return TaskService(client, os.getenv("TRELLO_BOARD_ID", "").strip(),
                       os.getenv("TRELLO_BOARD_NAME", "DIO TaskFlow").strip(),
                       os.getenv("APP_TIMEZONE", "America/Sao_Paulo"))


def safe_tool(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        try:
            return {"ok": True, "resultado": function(*args, **kwargs)}
        except TaskFlowError as error:
            return {"ok": False, "erro": str(error)}
        except ZoneInfoNotFoundError:
            return {"ok": False, "erro": "Fuso inválido. Confira APP_TIMEZONE e instale tzdata."}
        except Exception:
            # Exceções de HTTP podem incluir URL com token; não repassá-las ao modelo.
            return {"ok": False, "erro": "Não foi possível confirmar a operação. Confira conexão, credenciais e permissões. Antes de repetir uma criação ou mudança, liste as tarefas para verificar se ela ocorreu."}
    return wrapped


@safe_tool
def get_temporal_context() -> dict:
    """Obtém data e hora atuais no fuso configurado para interpretar hoje e amanhã."""
    zone = ZoneInfo(os.getenv("APP_TIMEZONE", "America/Sao_Paulo"))
    now = datetime.now(zone)
    return {"data": now.date().isoformat(), "data_formatada": now.strftime("%d/%m/%Y"),
            "hora": now.strftime("%H:%M"), "fuso": str(zone)}


@safe_tool
def adicionar_tarefa(nome: str, descricao: str, data: str, hora: str = "23:59") -> dict:
    """Cria uma tarefa em A fazer com vencimento no fuso local.

    Args:
        nome: Título da tarefa informado pelo usuário.
        descricao: Detalhes da tarefa, ou string vazia quando não houver.
        data: Dia de vencimento no formato AAAA-MM-DD, interpretado no fuso local.
        hora: Hora local HH:MM. Sem horário informado, usar 23:59.
    """
    return get_service().add(nome, descricao, data, hora)


@safe_tool
def listar_tarefas(status: str = "todas") -> dict:
    """Lista cards abertos do quadro configurado, com seus IDs.

    Args:
        status: Todas, A fazer, Em andamento ou Concluído (aceita acentos).
    """
    return get_service().list_tasks(status)


@safe_tool
def mudar_status_tarefa(id_da_tarefa: str, novo_status: str) -> dict:
    """Move um card pelo ID retornado na listagem, dentro do quadro configurado.

    Args:
        id_da_tarefa: ID exato obtido de listar_tarefas, nunca inventado.
        novo_status: A fazer, Em andamento ou Concluído.
    """
    return get_service().move(id_da_tarefa, novo_status)
