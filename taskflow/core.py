"""Regras de tarefas independentes do modelo; todas as datas têm fuso explícito."""

from datetime import date, datetime, time, timezone
import re
import unicodedata
from zoneinfo import ZoneInfo


class TaskFlowError(ValueError):
    """Erro de domínio com mensagem pública, sem credenciais."""


def normalize(value):
    text = unicodedata.normalize("NFKD", value.strip().casefold())
    return " ".join("".join(c for c in text if not unicodedata.combining(c)).split())


ALIASES = {
    "a fazer": "a fazer", "todo": "a fazer", "to do": "a fazer",
    "em andamento": "em andamento", "doing": "em andamento",
    "concluido": "concluido", "concluida": "concluido", "done": "concluido",
}
LABELS = {"a fazer": "A fazer", "em andamento": "Em andamento", "concluido": "Concluído"}


def canonical_status(value, allow_all=False):
    key = normalize(value)
    if allow_all and key in {"todas", "todos", "all"}:
        return "todas"
    if key not in ALIASES:
        raise TaskFlowError("Status inválido. Use A fazer, Em andamento ou Concluído.")
    return ALIASES[key]


def due_in_utc(day, hour, zone):
    """Converte data e hora locais para UTC sem deslocar o dia local desejado."""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
        raise TaskFlowError("Data inválida. Use AAAA-MM-DD.")
    if not re.fullmatch(r"\d{2}:\d{2}", hour):
        raise TaskFlowError("Hora inválida. Use HH:MM.")
    try:
        local = datetime.combine(date.fromisoformat(day), time.fromisoformat(hour), zone)
    except ValueError:
        raise TaskFlowError("Data ou hora inexistente. Confira o calendário e use HH:MM.") from None
    # Evita atribuir silenciosamente um horário local inexistente em transições de DST.
    utc = local.astimezone(timezone.utc)
    if utc.astimezone(zone).replace(tzinfo=None) != local.replace(tzinfo=None):
        raise TaskFlowError("Horário inexistente neste fuso. Escolha outro horário.")
    if local.replace(fold=1).utcoffset() != local.utcoffset():
        raise TaskFlowError("Horário ambíguo neste fuso. Escolha outro horário.")
    return utc.isoformat().replace("+00:00", "Z")


class TaskService:
    def __init__(self, client, board_id="", board_name="DIO TaskFlow", timezone_name="America/Sao_Paulo"):
        self.client = client
        self.board_id = board_id
        self.board_name = board_name
        self.zone = ZoneInfo(timezone_name)

    def board(self):
        if self.board_id:
            board = self.client.get_board(self.board_id)
            if board.closed:
                raise TaskFlowError("O quadro configurado está arquivado.")
            return board
        matches = [b for b in self.client.list_boards(board_filter="open") if b.name == self.board_name]
        if not matches:
            raise TaskFlowError("Quadro não encontrado. Confira TRELLO_BOARD_ID ou TRELLO_BOARD_NAME.")
        if len(matches) > 1:
            raise TaskFlowError("Há quadros com o mesmo nome. Configure TRELLO_BOARD_ID.")
        return matches[0]

    def lists(self, board):
        result = {}
        for item in board.list_lists(list_filter="open"):
            key = ALIASES.get(normalize(item.name))
            if key:
                if key in result:
                    raise TaskFlowError("Listas de status duplicadas. Mantenha uma lista para cada status.")
                result[key] = item
        missing = [LABELS[key] for key in LABELS if key not in result]
        if missing:
            raise TaskFlowError("Crie as listas que faltam: " + ", ".join(missing) + ".")
        return result

    def serialize(self, card, status):
        raw = card.due
        if raw:
            parsed = raw if isinstance(raw, datetime) else datetime.fromisoformat(raw.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            raw = parsed.astimezone(self.zone).isoformat()
        return {"id": card.id, "nome": card.name, "descricao": card.desc,
                "vencimento_local": raw or None, "fuso": str(self.zone),
                "status": LABELS[status], "url": getattr(card, "short_url", "")}

    def add(self, name, description, day, hour="23:59"):
        if not name.strip():
            raise TaskFlowError("Informe um nome para a tarefa.")
        due = due_in_utc(day, hour, self.zone)
        board = self.board()
        todo = self.lists(board)["a fazer"]
        card = todo.add_card(name=name.strip(), desc=description.strip(), due=due)
        return self.serialize(card, "a fazer")

    def list_tasks(self, status="todas"):
        key = canonical_status(status, allow_all=True)
        lists = self.lists(self.board())
        return [self.serialize(card, current)
                for current, item in lists.items() if key in {"todas", current}
                for card in item.list_cards(card_filter="open")]

    def move(self, card_id, status):
        target = canonical_status(status)
        if not card_id.strip():
            raise TaskFlowError("Informe o ID da tarefa, obtido pela listagem.")
        lists = self.lists(self.board())
        found = [(card, current) for current, item in lists.items()
                 for card in item.list_cards(card_filter="open") if card.id == card_id]
        if not found:
            raise TaskFlowError("Tarefa não encontrada nas listas deste quadro. Liste as tarefas novamente.")
        card, current = found[0]
        # Uma requisição para mover e sincronizar o indicador de conclusão.
        self.client.fetch_json("/cards/" + card.id, http_method="PUT",
                               post_args={"idList": lists[target].id,
                                          "dueComplete": target == "concluido"})
        result = self.serialize(card, target)
        result["status_anterior"] = LABELS[current]
        return result
