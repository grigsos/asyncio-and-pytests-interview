import asyncio
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import json
import os

async def main():
    input_data, schema = jsonschema_import_and_validate()
    relevant_data = {key: input_data[key] for key in schema['properties'].keys()} # only keep relevant data
    dependencies = get_deps(input_data) # get dependencies

    completion_list = [""] * len(dependencies) # list of completion statuses

    events = [asyncio.Event() for _ in range(len(dependencies))] 

    tasks = {}
    completed = set()
    for i, task in enumerate(relevant_data['tasks']): # create tasks and add them to the task list
        tasks[i] = asyncio.create_task(task_coro(i, dependencies, task, completion_list, completed))

    while len(completed) < len(tasks): # wait for all tasks to complete
        for task_num, task in tasks.items():
            if task_num not in completed and dependencies[task_num].issubset(completed):
                events[task_num].set()  # signal the event to allow the task to start
                await task
                completed.add(task_num)

    print(completion_list)

    with open("output.txt", "w") as f: # write completion list to output file
        for i in range(len(completion_list)):
            f.write(f"task {i+1}: {completion_list[i]}\n")


##################### coruoutine functions #####################


async def task_coro(cur_task, dependencies, current_task, completion_list, completed):
    #import data from current task
    task_name = current_task['name']
    task_type = current_task['type']
    task_args = current_task['arguments']

    while not all(dep in completed for dep in dependencies[cur_task]): # wait for dependencies to complete
        await asyncio.sleep(0.1)

    for dep in dependencies[cur_task]: # check if dependencies have failed or been skipped
        if completion_list[dep] == "failed" or completion_list[dep] == "":
            completion_list[cur_task] = "skipped"
            print(f"Skipping {task_name} because dependency {dep+1} has failed or was skipped")
            return None

    print(f'Started ' + task_name)

    try:
        if task_type == 'eval':
            await asyncio.to_thread(exec, task_args) # run eval in a separate thread
        elif task_type == 'exec':
            proc = await asyncio.create_subprocess_shell(task_args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE) # run exec in a subprocess
            stdout, stderr = await proc.communicate() 
            print(stdout.decode().strip())
            if proc.returncode != 0: #
                raise Exception(f"Command exited with code {proc.returncode}: {task_args}")
    except Exception as e: # if task fails, print error and exit
        completion_list[cur_task] = "failed"
        print(f'Ended {task_name} with exception: {e}')
        return None
    else: # if task succeeds, print success and exit
        completion_list[cur_task] = "OK"
        print(f'Ended ' + task_name)
        return None

#################### initialisation ####################

def get_deps(inputJson): # returns a dict of dependencies
    task_names = []
    for task in inputJson['tasks']:
        task_names.append(task['name'])
    
    dependencies = {}
    for i, task in enumerate(inputJson['tasks']):
        task_name = task['name']
        task_dependencies = set()
        for dependency_name in task.get('dependencies', []):
            if dependency_name not in task_names:
                raise ValueError(f"Task {task_name} has invalid dependency {dependency_name}")
            dependency_index = task_names.index(dependency_name)
            task_dependencies.add(dependency_index)
        dependencies[i] = task_dependencies
        
    return dependencies

def get_jsons(fileName): # returns a dict of the json file from data folder
    data_path = os.path.join(os.path.dirname(__file__), 'data', fileName)
    with open(data_path) as f:
        dataJson = json.load(f)
    return dataJson

def jsonschema_import_and_validate(): # returns  input and schema jsons
    input_data = get_jsons('input1.json')
    schema = get_jsons('schema.json')
    try:
        validate(input_data, schema)
        print("Validation successful")
        return input_data, schema
    except ValidationError as e: # if validation fails, print error and exit
        print(f"Validation error: {e}") 
        raise

if __name__ == '__main__': 
    try:
        asyncio.run(main())
    except Exception as e: # if validation fails, print error and exit
        print(f"Error: {e}") 
        raise