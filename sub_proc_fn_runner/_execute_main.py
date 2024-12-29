import importlib


def execute_fn(import_path, function_name, fn_args, fn_kwargs):
    module = importlib.import_module(import_path)
    fn = getattr(module, function_name)
    return fn(*fn_args, **fn_kwargs)
