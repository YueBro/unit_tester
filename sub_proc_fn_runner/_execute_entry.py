import os.path as osp
import sys
sys.path.append(osp.dirname(__file__))
import argparse
from copy import deepcopy

from _execute_main import execute_fn
from serialize_tool import unserialize, serialize


import builtins

class Returner:
    def __init__(self) -> None:
        self.orig_print = None
        self.last_print = None

    def __enter__(self):
        self.orig_print = deepcopy(print)
        builtins.print = self.print
        return self
    
    def __exit__(self, *args, **kwargs):
        builtins.print = self.orig_print

    def print(self, *vars, sep=" ", end="\n", **kwargs):
        if self.orig_print is None:
            raise RuntimeError
        s = sep.join([getattr(v, "__str__", "__repr__")() for v in vars]) + end
        self.last_print = s
        self.orig_print(s, end="", **kwargs)

    def return_arg(self, arg):
        if self.orig_print is None:
            raise RuntimeError
        if (self.last_print is not None) and (not self.last_print.endswith("\n")):
            self.orig_print()
        self.orig_print(RETURN_SIGNITURE_START_STR + serialize(arg), end="")
        exit()


RETURN_SIGNITURE_START_STR = ">>> execute_entry return: "


parser = argparse.ArgumentParser()
parser.add_argument("--sys-paths", nargs="+")
parser.add_argument("--import-path", required=True)
parser.add_argument("--function", required=True)
parser.add_argument("--args-and-kwargs", required=True)

if __name__ == "__main__":
    with Returner() as returner:
        parsed_args = parser.parse_args()

        sys_paths = parsed_args.sys_paths or []
        import_path = parsed_args.import_path
        function_name = parsed_args.function
        fn_args_and_kwargs = parsed_args.args_and_kwargs

        sys.path = sys_paths

        fn_args, fn_kwargs = unserialize(fn_args_and_kwargs)
        ret = execute_fn(import_path, function_name, fn_args, fn_kwargs)
        returner.return_arg(ret)
