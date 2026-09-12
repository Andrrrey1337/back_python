import socket

import model
import protocol


OPERATION_HANDLERS = {
    protocol.OP_CREATE_PERSON: (
        model.create_person,
        ("identifier", "ip", "platform"),
    ),
    protocol.OP_GET_PERSONS: (model.get_persons, ()),
    protocol.OP_GET_PERSON: (model.get_person, ("identifier",)),
    protocol.OP_CREATE_INSTRUCTION: (
        model.create_instruction,
        ("identifier", "content", "person", "description", "stage", "spawned"),
    ),
    protocol.OP_GET_INSTRUCTIONS: (model.get_instructions, ()),
    protocol.OP_GET_INSTRUCTION: (model.get_instruction, ("identifier",)),
    protocol.OP_CREATE_ANSWER: (
        model.create_answer,
        (
            "identifier",
            "output",
            "stage",
            "exception",
            "instruction",
            "cache_hit",
        ),
    ),
    protocol.OP_GET_ANSWERS: (model.get_answers, ()),
    protocol.OP_GET_ANSWER: (model.get_answer, ("identifier",)),
    protocol.OP_GET_RECENT_ANSWERS: (model.get_recent_answers, ()),
}


def dispatch(op_code, params):
    """Вызов нужной функции в зависимости от кода операции"""
    try:
        handler, argument_names = OPERATION_HANDLERS[op_code]
    except KeyError as exc:
        raise ValueError("Unknown op_code") from exc
    return handler(*(params[name] for name in argument_names))


def handle_client(sock, addr):
    """Прием бинарных пакетов от клиента и отправка XML ответа"""
    while True:
        hdr = protocol.recv_exact(sock, protocol.REQ_HEADER_LEN)
        if not hdr:
            break
        version, op_code, body_len = protocol.unpack_request_header(hdr)
        body_bytes = protocol.recv_exact(sock, body_len)
        xml_text = body_bytes.decode("utf-8")
        print(f"[СЕРВЕР] Запрос (код {op_code}): {xml_text}", flush=True)
        if version != protocol.PROTOCOL_VERSION:
            resp_xml = protocol.make_response_xml(
                "error", error="Bad protocol version"
            )
        else:
            try:
                params = protocol.parse_request_xml(xml_text)
                res = dispatch(op_code, params)
                resp_xml = protocol.make_response_xml("success", data=res)
            except Exception as exc:
                resp_xml = protocol.make_response_xml("error", error=str(exc))
        sock.sendall(protocol.pack_response(op_code, resp_xml))


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if hasattr(socket, "SO_REUSEPORT"):
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    server.bind((protocol.DEFAULT_HOST, protocol.DEFAULT_PORT))
    server.listen(5)
    print(
        f"Сервер запущен на {protocol.DEFAULT_HOST}: {protocol.DEFAULT_PORT}",
        flush=True,
    )
    try:
        while True:
            client_sock, addr = server.accept()
            try:
                handle_client(client_sock, addr)
            finally:
                client_sock.close()
    finally:
        server.close()


if __name__ == "__main__":
    main()
