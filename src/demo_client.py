from rpc_client import RPCClient


def test_persons_and_instructions(client):
    print("\n1. create_person:")
    print(client.create_person(1, "192.168.1.1", "linux"))
    print(client.create_person(2, "192.168.1.2", "windows"))

    print("\n2. get_persons:")
    print(client.get_persons())

    print("\n3. get_person:")
    print("Успешный поиск (id=1):", client.get_person(1))
    try:
        client.get_person(999)
    except RuntimeError as exc:
        print("Поиск несуществующего (id=999):", exc)

    print("\n4. create_instruction:")
    print(client.create_instruction(10, "task 1", 1, "desc 1", "new", 1))
    print(client.create_instruction(20, "task 2", 2, "desc 2", "done", 0))

    print("\n5. get_instructions:")
    print(client.get_instructions())

    print("\n6. get_instruction:")
    print(client.get_instruction(10))


def test_answers(client):
    print("\n7. create_answer:")
    print(client.create_answer(100, "ok", "done", "none", 10, 1))
    print(client.create_answer(200, "fail", "err", "timeout", 20, 0))

    print("\n8. get_answers:")
    print(client.get_answers())

    print("\n9. get_answer:")
    print(client.get_answer(100))

    print("\n10. get_recent_answers:")
    print(client.get_recent_answers())


def main():
    client = RPCClient()
    client.connect()
    try:
        test_persons_and_instructions(client)
        test_answers(client)
    finally:
        client.close()


if __name__ == "__main__":
    main()