import socket

import model
import protocol


def dispatch(op_code, p):
    """Вызов нужной функции в зависимости от кода операции"""
    if op_code == protocol.OP_CREATE_PERSON:
        return model.create_person(p["identifier"], p["ip"], p["platform"])
    if op_code == protocol.OP_GET_PERSONS:
        return model.get_persons()
    if op_code == protocol.OP_GET_PERSON:
        return model.get_person(p["identifier"])
    if op_code == protocol.OP_CREATE_INSTRUCTION:
        return model.create_instruction(
            p["identifier"],
            p["content"],
            p["person"],
            p["description"],
            p["stage"],
            p["spawned"],
        )
    if op_code == protocol.OP_GET_INSTRUCTIONS:
        return model.get_instructions()
    if op_code == protocol.OP_GET_INSTRUCTION:
        return model.get_instruction(p["identifier"])
    if op_code == protocol.OP_CREATE_ANSWER:
        return model.create_answer(
            p["identifier"],
            p["output"],
            p["stage"],
            p["exception"],
            p["instruction"],
            p["cache_hit"],
        )
    if op_code == protocol.OP_GET_ANSWERS:
        return model.get_answers()
    if op_code == protocol.OP_GET_ANSWER:
        return model.get_answer(p["identifier"])
    if op_code == protocol.OP_GET_RECENT_ANSWERS:
        return model.get_recent_answers()
    raise ValueError("Unknown op_code")


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
        f"Сервер запущен на {protocol.DEFAULT_HOST}:{protocol.DEFAULT_PORT}",
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