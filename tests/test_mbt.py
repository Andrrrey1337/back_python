"""Тестирование RPC на основе модели с библиотекой hypothesis"""

import importlib
import sys
from pathlib import Path
import threading
import time

from hypothesis import settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule

SRC_DIR = str(Path(__file__).resolve().parent.parent / "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

model = importlib.import_module("model")
rpc_server = importlib.import_module("rpc_server")
RPCClient = importlib.import_module("rpc_client").RPCClient

server_started = False


def start_test_server():
    """Запуск TCP сервера в фоновом потоке для тестирования"""
    global server_started
    if not server_started:
        thread = threading.Thread(target=rpc_server.main, daemon=True)
        thread.start()
        time.sleep(0.3)
        server_started = True


class RPCStateMachine(RuleBasedStateMachine):
    """Модель конечного автомата для сравнения RPC сервера с моделью"""

    def __init__(self):
        super().__init__()
        start_test_server()
        model.persons.clear()
        model.instructions.clear()
        model.answers.clear()
        self.model_persons = []
        self.model_instructions = []
        self.model_answers = []
        self.client = RPCClient()
        self.client.connect()

    def teardown(self):
        """Закрытие сетевого сокета после каждого теста"""
        self.client.close()

    @rule(
        ident=st.integers(min_value=1, max_value=50),
        ip=st.sampled_from(["127.0.0.1", "192.168.1.1"]),
        platform=st.sampled_from(["linux", "windows"]),
    )
    def create_person(self, ident, ip, platform):
        """Создание Person через RPC и сохранение в модель"""
        self.client.create_person(ident, ip, platform)
        self.model_persons.append([str(ident), ip, platform])

    @rule()
    def get_persons(self):
        """Сравнение списка всех Person с моделью"""
        res = self.client.get_persons()
        assert len(res) == len(self.model_persons)

    @rule(ident=st.integers(min_value=1, max_value=50))
    def get_person(self, ident):
        """Поиск Person по идентификатору или проверка ошибки"""
        ident_str = str(ident)
        found = any(p[0] == ident_str for p in self.model_persons)
        if found:
            res = self.client.get_person(ident)
            assert res[0] == ident_str
        else:
            try:
                self.client.get_person(ident)
            except RuntimeError:
                return
            raise AssertionError("Expected error")

    @rule(
        ident=st.integers(min_value=1, max_value=50),
        content=st.text(alphabet="abc", min_size=1, max_size=5),
        person=st.integers(min_value=1, max_value=50),
        desc=st.text(alphabet="xyz", min_size=1, max_size=5),
        stage=st.sampled_from(["new", "done"]),
        spawned=st.integers(min_value=0, max_value=1),
    )
    def create_instruction(
        self, ident, content, person, desc, stage, spawned
    ):
        """Создание Instruction через RPC и сохранение в модель"""
        self.client.create_instruction(
            ident, content, person, desc, stage, spawned
        )
        self.model_instructions.append([str(ident), str(person), desc])

    @rule()
    def get_instructions(self):
        """Сравнение списка всех Instruction с моделью"""
        res = self.client.get_instructions()
        assert len(res) == len(self.model_instructions)

    @rule(ident=st.integers(min_value=1, max_value=50))
    def get_instruction(self, ident):
        """Поиск Instruction по идентификатору или проверка ошибки"""
        ident_str = str(ident)
        found = any(
            item[0] == ident_str for item in self.model_instructions
        )
        if found:
            res = self.client.get_instruction(ident)
            assert res[0] == ident_str
        else:
            try:
                self.client.get_instruction(ident)
            except RuntimeError:
                return
            raise AssertionError("Expected error")

    @rule(
        ident=st.integers(min_value=1, max_value=50),
        output=st.text(alphabet="out", min_size=1, max_size=5),
        stage=st.sampled_from(["ok", "fail"]),
        exc=st.sampled_from(["none", "err"]),
        inst=st.integers(min_value=1, max_value=50),
        cache_hit=st.integers(min_value=0, max_value=1),
    )
    def create_answer(self, ident, output, stage, exc, inst, cache_hit):
        """Создание Answer через RPC и сохранение в модель"""
        self.client.create_answer(
            ident, output, stage, exc, inst, cache_hit
        )
        self.model_answers.append([str(ident), output, str(inst)])

    @rule()
    def get_answers(self):
        """Сравнение списка всех Answer с моделью"""
        res = self.client.get_answers()
        assert len(res) == len(self.model_answers)

    @rule(ident=st.integers(min_value=1, max_value=50))
    def get_answer(self, ident):
        """Поиск Answer по идентификатору или проверка ошибки"""
        ident_str = str(ident)
        found = any(
            item[0] == ident_str for item in self.model_answers
        )
        if found:
            res = self.client.get_answer(ident)
            assert res[0] == ident_str
        else:
            try:
                self.client.get_answer(ident)
            except RuntimeError:
                return
            raise AssertionError("Expected error")

    @rule()
    def get_recent_answers(self):
        """Проверка вызова реляционной выборки за последние 8 минут"""
        res = self.client.get_recent_answers()
        expected = []
        for answer in self.model_answers:
            descriptions = [
                instruction[2]
                for instruction in self.model_instructions
                if instruction[0] == answer[2]
            ]
            for description in descriptions or [None]:
                expected.append([answer[1], description])
        assert res == expected


TestRPCModel = RPCStateMachine.TestCase
TestRPCModel.settings = settings(
    max_examples=15, stateful_step_count=15, deadline=None
)
