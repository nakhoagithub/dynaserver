import os
import sys
import importlib
import inspect
from typing import Dict, List
from collections import defaultdict, deque
from dyna.tools import root_dir
from dyna.tools.file import read_json
from dyna.environment import env, apis, workers


modules: Dict[str, Dict] = {}

def build_dependency_graph(modules: Dict[str, dict]):
    graph = defaultdict(list)
    indegree = {k: 0 for k, v in modules.items()}

    for k, v in modules.items():
        dependents = v.get("dependents", [])
        if type(dependents) is list:
            for dep in v.get("dependents", []):
                graph[dep].append(k)
                indegree[k] += 1
    
    return graph, indegree


def topological_sort(graph: dict, indegree: dict, modules: Dict[str, dict]):
    queue = deque([node for node in indegree if indegree[node] == 0])
    sorted_modules = []

    while queue:
        node = queue.popleft()
        sorted_modules.append(modules[node])

        for neighbor in graph[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)
    
    return sorted_modules


def __read_module(path: str):
    file = os.path.normcase(path)
    if not os.path.exists(file): return
    return read_json(path)


def __list_modules(folder: str):
    # Module's directory
    module_folder = os.path.normcase(os.path.join(root_dir(), folder))
    sys.path.append(module_folder)
    dirs = os.listdir(module_folder)
    for d in dirs:
        addon_path = os.path.normcase(f"{root_dir()}/{folder}")
        init_file = os.path.join(addon_path, d, "__init__.py")
        module_file = os.path.join(addon_path, d, "__module__.json")
        module_path = os.path.join(addon_path, d)
        if os.path.isfile(init_file) and os.path.isfile(module_file):
            module_name = d
            module_json = read_json(module_file)
            if module_json:
                module_json["module_name"] = module_name
                module_json["module_path"] = module_path
                module = module_folder.replace(f"{root_dir()}", "").replace("\\", ".").replace("/", ".")
                module_json["import_path"] = f"{module[1:]}.{d}"
                modules[d] = module_json

def system_initialized():
    # Import
    paths = ["addons", "dyna/addons"]
    for path in paths:
        __list_modules(path)

    graph, indegree = build_dependency_graph(modules)
    sorted_modules = topological_sort(graph, indegree, modules)
    # import
    for i in sorted_modules:
        # module_name = i.get("module_name")
        import_path = i.get("import_path")
        importlib.import_module(import_path)

    # Create data
    collection_obj = env["Collection"]

    # Delete collection obj
    collection_obj.delete_where({"id": {"$nin": [k for k, _ in env.items()]}})

    active_module_paths = []

    module_items = [{**v, "key": k} for k, v in modules.items()]
    module_items = sorted(module_items, key=lambda x: x.get("active", False))

    # Data default
    for v in module_items:
        files_name = v.get("data", []) or []
        module_path = v.get("module_path")
        module_active = v.get("active", False)
        if module_active:
            active_module_paths.append(module_path)

        # Import collection obj
        for k, collection_ in env.items():
            collection_path = os.path.normcase(inspect.getfile(collection_.__class__))
            if collection_path.startswith(module_path):
                collection_obj.update({
                    "id": k,
                    "name": collection_.__class__.__name__,
                    "description": collection_._description,
                    "active": module_active,
                }, upsert=True)

        # Import data default
        for file_name in files_name:
            file_path = os.path.normcase(f"{module_path}/data/{file_name}")
            if not os.path.exists(file_path): continue

            json_data = read_json(file_path)

            if not isinstance(json_data, dict): continue

            data_active = json_data.get("active", False)
            no_update = json_data.get("no_update", False)

            document = json_data.get("document", None)
            obj = env.get(document, None)

            if obj is None: continue

            # Module active and data active
            if data_active and module_active:
                datas = json_data.get("data", []) or []
                for data in datas:
                    if isinstance(data, dict):
                        if not no_update:
                            obj.update(data, upsert=True)
                        elif obj.count() == 0:
                            obj.update(data, upsert=True)

            # Delete collection and data
            if not data_active or not module_active:
                datas = json_data.get("data", []) or []
                ids = [i['id'] for i in datas]
                obj.delete_where({"id": {"$in": ids}})
                
            if not module_active:
                obj.drop_collection()
        
    # Active API
    for k, v in apis.items():
        api_resource_obj = v.get("obj", None)
        if api_resource_obj is not None:
            api_path = os.path.normcase(inspect.getfile(api_resource_obj.__class__))
            for module_path in active_module_paths:
                if api_path.startswith(module_path):
                    v["active"] = True
            
    # Active Worker
    for k, v in workers.items():
        worker_obj = v.get("obj", None)
        if worker_obj is not None:
            worker_path = os.path.normcase(inspect.getfile(worker_obj.__class__))
            for module_path in active_module_paths:
                if worker_path.startswith(module_path):
                    v["active"] = True
                    worker_obj._start()