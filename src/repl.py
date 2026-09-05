import shlex
import model


HELP = '''Команды:
person:
    add ID IP PLATFORM
    all
    get ID
    
instruction: 
    add ID CONTENT PERSON DESCRIPTION STAGE SPAWNED
    all
    get ID

answer:
    add ID OUTPUT STAGE EXCEPTION INSTRUCTION CACHE_HIT
    all
    get ID
    
query
help
exit'''


print('Введите help для справки.')

while True:
    try:
        parts = shlex.split(input('command: '))

        if not parts:
            continue
        if parts[0] in ('exit', 'quit'):
            break
        if parts[0] == 'help':
            print(HELP)
            continue
        if parts[0] == 'query':
            for row in model.get_recent_answers():
                print(row)
            continue

        entity, command = parts[:2]
        args = [int(x) if x.isdigit() else x for x in parts[2:]]

        if entity == 'person':
            create = model.create_person
            get_all = model.get_persons
            get_one = model.get_person
        elif entity == 'instruction':
            create = model.create_instruction
            get_all = model.get_instructions
            get_one = model.get_instruction
        elif entity == 'answer':
            create = model.create_answer
            get_all = model.get_answers
            get_one = model.get_answer
        else:
            raise ValueError('Unknown entity')

        if command == 'add':
            create(*args)
            print('Запись добавлена')
        elif command == 'all':
            print(*get_all(), sep='\n')
        elif command == 'get':
            print(get_one(args[0]))
        else:
            raise ValueError('Unknown command')

    except (ValueError, EOFError, KeyboardInterrupt) as error:
        print(f'Ошибка: {error}')
