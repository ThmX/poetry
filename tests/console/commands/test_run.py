import sys

import pytest


@pytest.fixture
def tester(command_tester_factory):
    return command_tester_factory("run")


@pytest.fixture(autouse=True)
def patches(mocker, env):
    mocker.patch("poetry.utils.env.EnvManager.get", return_value=env)


def test_run_passes_all_args(tester, env):
    tester.execute("python -V")
    assert [["python", "-V"]] == env.executed


def test_run_script_uses_current_python_executable(tester, env):
    status_code = tester.execute("foo")
    assert status_code == 0
    assert env.executed == [
        [
            sys.executable,
            "-c",
            "import sys; "
            "from importlib import import_module; "
            "sys.argv = ['foo']; "
            "import_module('foo').bar()",
        ]
    ]
