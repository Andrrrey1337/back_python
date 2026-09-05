import time

persons = []
instructions = []
answers = []


def create_person(identifier, ip, platform):
    persons.append([identifier, int(time.time()), ip, platform])


def get_persons():
    return persons


def get_person(identifier):
    for person in persons:
        if person[0] == identifier:
            return person
    raise ValueError('Person not found')


def create_instruction(
    identifier, content, person, description, stage, spawned
):
    instructions.append([
        identifier,
        int(time.time()),
        content,
        person,
        description,
        stage,
        spawned,
    ])


def get_instructions():
    return instructions


def get_instruction(identifier):
    for instruction in instructions:
        if instruction[0] == identifier:
            return instruction
    raise ValueError('Instruction not found')


def create_answer(
    identifier, output, stage, exception, instruction, cache_hit
):
    answers.append([
        identifier,
        int(time.time()),
        output,
        stage,
        exception,
        instruction,
        cache_hit,
    ])


def get_answers():
    return answers


def get_answer(identifier):
    for answer in answers:
        if answer[0] == identifier:
            return answer
    raise ValueError('Answer not found')


def get_recent_answers():
    limit = int(time.time()) - 8 * 60
    result = []

    for answer in answers:
        if answer[1] < limit:
            continue
        for instruction in instructions:
            if instruction[0] == answer[5]:
                result.append((answer[2], instruction[4]))

    return result
