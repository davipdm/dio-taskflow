"""Testes offline com substituto em memória do Trello, sem Gemini ou rede."""

from datetime import datetime
import os
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from zoneinfo import ZoneInfo

from taskflow.core import TaskFlowError, TaskService, canonical_status, due_in_utc
from taskflow import tools


class FakeList:
    def __init__(self, name, identifier):
        self.name, self.id, self.cards = name, identifier, []

    def list_cards(self, card_filter="open"):
        return self.cards

    def add_card(self, name, desc, due):
        card = SimpleNamespace(id="card-" + str(len(self.cards) + 1), name=name,
                               desc=desc, due=due, short_url="https://trello.com/c/example")
        self.cards.append(card)
        return card


class FakeBoard:
    id, name, closed = "board-1", "DIO TaskFlow", False

    def __init__(self):
        self.items = [FakeList("A fazer", "l1"), FakeList("Em andamento", "l2"), FakeList("Concluído", "l3")]

    def list_lists(self, list_filter="open"):
        return self.items


class FakeClient:
    def __init__(self):
        self.target = FakeBoard()
        self.boards = [self.target]
        self.updates = []

    def list_boards(self, board_filter="open"):
        return self.boards

    def get_board(self, board_id):
        return self.target

    def fetch_json(self, path, http_method, post_args):
        self.updates.append(post_args)
        card_id = path.rsplit("/", 1)[-1]
        origin = next(item for item in self.target.items if any(c.id == card_id for c in item.cards))
        card = next(c for c in origin.cards if c.id == card_id)
        destination = next(item for item in self.target.items if item.id == post_args["idList"])
        origin.cards.remove(card)
        destination.cards.append(card)
        return {"id": card_id}


class DateTests(unittest.TestCase):
    def test_midnight_does_not_become_previous_local_day(self):
        zone = ZoneInfo("America/Sao_Paulo")
        utc = due_in_utc("2026-10-21", "00:00", zone)
        self.assertEqual(utc, "2026-10-21T03:00:00Z")
        self.assertEqual(datetime.fromisoformat(utc).astimezone(zone).date().isoformat(), "2026-10-21")

    def test_end_of_day_rolls_utc_forward_but_preserves_local_day(self):
        self.assertEqual(due_in_utc("2026-12-31", "23:59", ZoneInfo("America/Sao_Paulo")), "2027-01-01T02:59:00Z")

    def test_invalid_dates_and_hours(self):
        for day, hour in [("2026-02-30", "12:00"), ("21/10/2026", "12:00"), ("2026-10-21", "24:00")]:
            with self.subTest(day=day, hour=hour), self.assertRaises(TaskFlowError):
                due_in_utc(day, hour, ZoneInfo("America/Sao_Paulo"))

    def test_dst_gap_and_ambiguous_hour_rejected(self):
        for day in ("2026-03-08", "2026-11-01"):
            hour = "02:30" if "03-08" in day else "01:30"
            with self.subTest(day=day), self.assertRaises(TaskFlowError):
                due_in_utc(day, hour, ZoneInfo("America/New_York"))


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.client = FakeClient()
        self.service = TaskService(self.client)

    def test_create_list_move_and_reopen(self):
        card = self.service.add("Estudar Python", "ADK", "2026-10-21")
        self.assertEqual(card["vencimento_local"], "2026-10-21T23:59:00-03:00")
        self.assertEqual(len(self.service.list_tasks("a fazer")), 1)
        self.service.move(card["id"], "Em andamento")
        self.assertEqual(len(self.service.list_tasks("doing")), 1)
        self.service.move(card["id"], "CONCLUÍDO")
        self.assertTrue(self.client.updates[-1]["dueComplete"])
        self.assertEqual(len(self.service.list_tasks("concluído")), 1)
        self.service.move(card["id"], "a fazer")
        self.assertFalse(self.client.updates[-1]["dueComplete"])

    def test_accents_spaces_and_aliases(self):
        for status in ("concluído", "CONCLUIDO", "  Concluída ", "done"):
            self.assertEqual(canonical_status(status), "concluido")

    def test_invalid_status_is_not_silently_all(self):
        with self.assertRaises(TaskFlowError):
            self.service.list_tasks("cancelada")

    def test_missing_board(self):
        self.client.boards = []
        with self.assertRaises(TaskFlowError):
            self.service.list_tasks()

    def test_duplicate_board_names_require_id(self):
        self.client.boards.append(FakeBoard())
        with self.assertRaises(TaskFlowError):
            self.service.list_tasks()
        self.assertEqual(TaskService(self.client, board_id="board-1").list_tasks(), [])

    def test_missing_or_duplicate_status_lists(self):
        self.client.target.items.pop()
        with self.assertRaises(TaskFlowError):
            self.service.list_tasks()
        self.client.target.items.extend([FakeList("Done", "l3"), FakeList("Concluído", "l4")])
        with self.assertRaises(TaskFlowError):
            self.service.list_tasks()

    def test_card_outside_configured_board_is_not_moved(self):
        with self.assertRaises(TaskFlowError):
            self.service.move("outside-card", "Concluído")
        self.assertEqual(self.client.updates, [])

    def test_same_titles_can_be_selected_by_id(self):
        first = self.service.add("Estudar", "A", "2026-10-21")
        second = self.service.add("Estudar", "B", "2026-10-21")
        self.service.move(second["id"], "done")
        self.assertEqual(self.service.list_tasks("a fazer")[0]["id"], first["id"])

    def test_empty_title_rejected_before_network(self):
        with self.assertRaises(TaskFlowError):
            self.service.add(" ", "", "2026-10-21")


class ToolTests(unittest.TestCase):
    def test_missing_credentials_are_explained(self):
        with patch.dict(os.environ, {"TRELLO_API_KEY": "", "TRELLO_TOKEN": ""}):
            result = tools.listar_tarefas()
        self.assertFalse(result["ok"])
        self.assertIn("TRELLO_TOKEN", result["erro"])

    def test_external_errors_do_not_leak_secrets(self):
        with patch.object(tools, "get_service", side_effect=RuntimeError("https://example?token=SECRET")):
            result = tools.listar_tarefas()
        self.assertFalse(result["ok"])
        self.assertNotIn("SECRET", str(result))

    def test_temporal_context_has_configured_timezone(self):
        with patch.dict(os.environ, {"APP_TIMEZONE": "America/Sao_Paulo"}):
            result = tools.get_temporal_context()
        self.assertTrue(result["ok"])
        self.assertEqual(result["resultado"]["data"], datetime.now(ZoneInfo("America/Sao_Paulo")).date().isoformat())

    def test_wrapped_tool_preserves_parameters_for_adk(self):
        import inspect
        self.assertEqual(list(inspect.signature(tools.adicionar_tarefa).parameters), ["nome", "descricao", "data", "hora"])


if __name__ == "__main__":
    unittest.main()
