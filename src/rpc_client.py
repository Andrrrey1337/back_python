"""Класс клиента RPC с методами повторяющими функции DAL"""

import socket

import protocol


class RPCClient:
    """Клиент для взаимодействия с сервером по протоколу TCP"""

    def __init__(self, host=protocol.DEFAULT_HOST, port=protocol.DEFAULT_PORT):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def close(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None

    def _call(self, op_code, params):
        """Отправка двоичного запроса и получение результата ответа"""
        xml_req = protocol.make_request_xml(params)
        req_pkt = protocol.pack_request(op_code, xml_req)
        self.sock.sendall(req_pkt)
        resp_hdr = protocol.recv_exact(self.sock, protocol.RESP_HEADER_LEN)
        if not resp_hdr:
            raise ConnectionError("Server disconnected")
        _, body_len = protocol.unpack_response_header(resp_hdr)
        body_bytes = protocol.recv_exact(self.sock, body_len)
        return protocol.parse_response_xml(body_bytes.decode("utf-8"))

    def create_person(self, identifier, ip, platform):
        params = {"identifier": identifier, "ip": ip, "platform": platform}
        return self._call(protocol.OP_CREATE_PERSON, params)

    def get_persons(self):
        return self._call(protocol.OP_GET_PERSONS, {})

    def get_person(self, identifier):
        params = {"identifier": identifier}
        return self._call(protocol.OP_GET_PERSON, params)

    def create_instruction(
        self, identifier, content, person, description, stage, spawned
    ):
        params = {
            "identifier": identifier,
            "content": content,
            "person": person,
            "description": description,
            "stage": stage,
            "spawned": spawned,
        }
        return self._call(protocol.OP_CREATE_INSTRUCTION, params)

    def get_instructions(self):
        return self._call(protocol.OP_GET_INSTRUCTIONS, {})

    def get_instruction(self, identifier):
        params = {"identifier": identifier}
        return self._call(protocol.OP_GET_INSTRUCTION, params)

    def create_answer(
        self, identifier, output, stage, exception, instruction, cache_hit
    ):
        params = {
            "identifier": identifier,
            "output": output,
            "stage": stage,
            "exception": exception,
            "instruction": instruction,
            "cache_hit": cache_hit,
        }
        return self._call(protocol.OP_CREATE_ANSWER, params)

    def get_answers(self):
        return self._call(protocol.OP_GET_ANSWERS, {})

    def get_answer(self, identifier):
        params = {"identifier": identifier}
        return self._call(protocol.OP_GET_ANSWER, params)

    def get_recent_answers(self):
        return self._call(protocol.OP_GET_RECENT_ANSWERS, {})