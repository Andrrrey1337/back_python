import xml.etree.ElementTree as ET

PROTOCOL_VERSION = 1
BYTE_ORDER = "little"

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 9020

REQ_HEADER_LEN = 5
RESP_HEADER_LEN = 7

OP_CREATE_PERSON = 1
OP_GET_PERSONS = 2
OP_GET_PERSON = 3
OP_CREATE_INSTRUCTION = 4
OP_GET_INSTRUCTIONS = 5
OP_GET_INSTRUCTION = 6
OP_CREATE_ANSWER = 7
OP_GET_ANSWERS = 8
OP_GET_ANSWER = 9
OP_GET_RECENT_ANSWERS = 10


def pack_request(op_code, xml_text):
    """Сборка заголовка из 5 байт и тела запроса в little endian"""
    body_bytes = xml_text.encode("utf-8")
    header = (
        PROTOCOL_VERSION.to_bytes(1, BYTE_ORDER)
        + op_code.to_bytes(1, BYTE_ORDER)
        + len(body_bytes).to_bytes(3, BYTE_ORDER)
    )
    return header + body_bytes


def unpack_request_header(header_bytes):
    """Извлечение версии кода операции и размера тела из заголовка запроса"""
    version = int.from_bytes(header_bytes[0:1], BYTE_ORDER)
    op_code = int.from_bytes(header_bytes[1:2], BYTE_ORDER)
    body_len = int.from_bytes(header_bytes[2:5], BYTE_ORDER)
    return version, op_code, body_len


def pack_response(op_code, xml_text):
    """Сборка заголовка ответа из 7 байт и тела в little endian"""
    body_bytes = xml_text.encode("utf-8")
    header = op_code.to_bytes(2, BYTE_ORDER) + len(body_bytes).to_bytes(
        5, BYTE_ORDER
    )
    return header + body_bytes


def unpack_response_header(header_bytes):
    """Извлечение кода операции и размера тела из заголовка ответа"""
    op_code = int.from_bytes(header_bytes[0:2], BYTE_ORDER)
    body_len = int.from_bytes(header_bytes[2:7], BYTE_ORDER)
    return op_code, body_len


def recv_exact(sock, count):
    """Чтение из сокета ровно указанного количества байт"""
    buf = bytearray()
    while len(buf) < count:
        chunk = sock.recv(count - len(buf))
        if not chunk:
            return None
        buf.extend(chunk)
    return bytes(buf)


def make_request_xml(params):
    """Формирование XML тела запроса из переданных параметров"""
    root = ET.Element("request")
    for key, value in params.items():
        child = ET.SubElement(root, key)
        child.text = str(value)
    return ET.tostring(root, encoding="unicode")


def parse_request_xml(xml_text):
    """Парсинг XML запроса в словарь аргументов"""
    root = ET.fromstring(xml_text)
    return {child.tag: child.text for child in root}


def make_response_xml(status, data=None, error=""):
    """Формирование XML ответа со статусом результатом или ошибкой"""
    root = ET.Element("response", {"status": status})
    if status == "error":
        err_node = ET.SubElement(root, "error")
        err_node.text = str(error)
    elif data is None:
        ET.SubElement(root, "null")
    elif isinstance(data, list) and (not data or isinstance(data[0], list)):
        list_node = ET.SubElement(root, "list")
        for row in data:
            row_node = ET.SubElement(list_node, "row")
            for item in row:
                col_node = ET.SubElement(row_node, "col")
                col_node.text = str(item)
    elif isinstance(data, list):
        row_node = ET.SubElement(root, "row")
        for item in data:
            col_node = ET.SubElement(row_node, "col")
            col_node.text = str(item)
    return ET.tostring(root, encoding="unicode")


def parse_response_xml(xml_text):
    """Парсинг XML ответа с преобразованием ошибки в исключение"""
    root = ET.fromstring(xml_text)
    if root.attrib.get("status") == "error":
        err_node = root.find("error")
        msg = err_node.text if err_node is not None else "Error"
        raise RuntimeError(msg)
    if root.find("null") is not None:
        return None
    list_node = root.find("list")
    if list_node is not None:
        rows = []
        for r in list_node.findall("row"):
            rows.append([c.text for c in r.findall("col")])
        return rows
    row_node = root.find("row")
    if row_node is not None:
        return [c.text for c in row_node.findall("col")]
    return None