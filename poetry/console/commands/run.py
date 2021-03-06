import sys

from cleo import argument

from .env_command import EnvCommand


class RunCommand(EnvCommand):

    name = "run"
    description = "Runs a command in the appropriate environment."

    arguments = [
        argument("args", "The command and arguments/options to run.", multiple=True)
    ]

    def __init__(self):  # type: () -> None
        from poetry.console.args.run_args_parser import RunArgsParser

        super(RunCommand, self).__init__()

        self.config.set_args_parser(RunArgsParser())

    def handle(self):
        args = self.argument("args")
        script = args[0]
        scripts = self.poetry.local_config.get("scripts")

        if scripts and script in scripts:
            return self.run_script(scripts[script], args)

        return self.env.execute(*args)

    def run_script(self, script, args):
        if isinstance(script, dict):
            script = script["callable"]

        module, callable_ = script.split(":")

        # TODO Check during PR if this is necessary or if we can drop the whole block use of self._module
        src_in_sys_path = ""
        if hasattr(self, "_module") and self._module.is_in_src():
            src_in_sys_path = "sys.path.append('src'); "

        python_executable = sys.executable or "python"
        cmd = [python_executable, "-c"]

        cmd += [
            "import sys; "
            "from importlib import import_module; "
            "sys.argv = {!r}; {}"
            "import_module('{}').{}()".format(args, src_in_sys_path, module, callable_)
        ]

        return self.env.execute(*cmd)
