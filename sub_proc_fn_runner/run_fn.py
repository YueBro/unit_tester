import os
import os.path as osp
import sys
import subprocess

from .serialize_tool import serialize, unserialize
from . import _execute_entry
from ._execute_entry import RETURN_SIGNITURE_START_STR

from typing import Callable


class SubProcFnRunner:
    """
    Execute a function with a fully separated subprocess.

    Example:
    ```
        import os
        import numpy as np

        from sub_proc_run import SubProcFnRunner
        
        # First way of using (with certain configs):
        ret = SubProcFnRunner(python_exec="/home/y/anaconda3/bin/python3")(np.array, [1, 2, 3])
        print(ret)

        # Second way of using:
        ret = SubProcFnRunner.Run(np.array, [1, 2, 3])
        print(ret)
    ```
    """
    def __init__(self, python_exec="python3"):
        self.python_exec = python_exec

    def __call__(self, fn: Callable, *args, **kwargs):
        if fn.__module__ == "__main__":
            raise ValueError("Function from '__main__' not supported!")

        args = () if (args is None) else args
        kwargs = {} if (kwargs is None) else kwargs
        paths = list(set([osp.abspath(p) for p in sys.path]))

        argstr_sys_paths = '--sys-paths ' + ' '.join([f'"{p}"' for p in paths])
        argstr_import_path = f'--import-path "{fn.__module__}"'
        argstr_function = f'--function "{fn.__name__}"'
        argstr_args = '--args-and-kwargs "' + serialize([args, kwargs]).replace('"', '\\"') + '"'

        # '-u' option allows printings not being buffered
        cmd = f"{self.python_exec} -u {_execute_entry.__file__} " + \
              f"{argstr_sys_paths} {argstr_import_path} {argstr_function} {argstr_args}"

        ret_flag = False
        ret = None
        with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True, cwd=os.getcwd()
        ) as process:
            for line in process.stdout:     # Real-time output line-by-line
                if not line.startswith(RETURN_SIGNITURE_START_STR):
                    print(line, end="")
                else:
                    ret_flag = True
                    ret = unserialize(line[len(RETURN_SIGNITURE_START_STR):].strip())
        if ret_flag is False:
            raise RuntimeError

        return ret

    @classmethod
    def Run(cls, fn: Callable, *args, **kwargs):
        return cls()(fn, *args, **kwargs)
