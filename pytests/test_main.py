import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import os
import pytest
import asyncio
from main import main, get_jsons, get_deps, task_coro

@pytest.fixture 
def input_data(): 
    return get_jsons('input1.json')

@pytest.fixture
def schema():
    return get_jsons('schema.json')

def test_jsonschema_validation(input_data, schema): # test if validation is successful
    assert validate(input_data, schema) is None

def test_get_usecase_deps(input_data): # test if usecase dependency import are correct
    dependencies = get_deps(input_data)
    assert dependencies == {0: set(), 1: {2, 4}, 2: {0}, 3: set(), 4: {3}, 5: {4}, 6: set(), 7: {1}, 8: {1, 5}}


def test_get_deps_more(): # test if more dependency import are correct
    input_data = {
        "tasks": [
            {"name": "A", "dependencies": ["B"]},
            {"name": "B", "dependencies": []}
        ]
    }
    dependencies = get_deps(input_data)
    assert dependencies == {0: {1}, 1: set()}



def test_main_output_usecase(): # test if usecase output is correct
    expected_output = "task 1: OK\ntask 2: OK\ntask 3: OK\ntask 4: OK\ntask 5: OK\ntask 6: failed\ntask 7: OK\ntask 8: OK\ntask 9: skipped\n"
    input_data = get_jsons('input1.json')
    schema = get_jsons('schema.json')
    os.remove("output.txt")
    asyncio.run(main())
    with open("output.txt", "r") as f:
        assert f.read() == expected_output


@pytest.mark.asyncio
async def test_main_make_up(): # test if made up input is correct
    input_data = {
        "tasks": [
            {"name": "A", "type": "exec", "arguments": "echo 'Task A'"},
            {"name": "B", "type": "exec", "arguments": "echo 'Task B'"},
            {"name": "C", "type": "exec", "arguments": "echo 'Task C'"},
            {"name": "D", "type": "eval", "arguments": "print('Task D')"},
            {"name": "E", "type": "eval", "arguments": "print('Task E')"}
        ]
    }

    completion_list = [""] * len(input_data["tasks"])

    events = [asyncio.Event() for _ in range(len(input_data["tasks"]))]

    dependencies = {0: set(), 1: {0}, 2: {1}, 3: {2}, 4: {2}}

    tasks = {}
    completed = set()
    for i, task in enumerate(input_data["tasks"]):
        tasks[i] = asyncio.create_task(task_coro(i, dependencies, task, completion_list, completed))

    while len(completed) < len(tasks):
        for task_num, task in tasks.items():
            if task_num not in completed and dependencies[task_num].issubset(completed):
                events[task_num].set()  # signal the event to allow the task to start
                await task
                completed.add(task_num)

    assert completion_list == ["OK"] * len(input_data["tasks"])

