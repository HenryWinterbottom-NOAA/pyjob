__author__ = 'Felix Simkovic'

import os
import pytest
import time

from pyjob.local import CPU_COUNT, LocalTask
from pyjob.script import Script

TEMPLATE = """
def fib(n):
    cache = [0, 1]
    for i in range(n):
        tmp = cache[0]
        cache[0] = cache[1]
        cache[1] += tmp 
    return cache[1]
n = {}; print('%dth fib is: %d' % (n, fib(n)))
"""


def get_py_script(i, target):
    script = Script(
        shebang='#!/usr/bin/env python',
        prefix='pyjob',
        stem='test{}'.format(i),
        suffix='.py')
    script.content.extend(TEMPLATE.format(target).split(os.linesep))
    return script


class TestLocalTaskTermination(object):
    def test_terminate_1(self):
        scripts = [get_py_script(i, 10000) for i in range(4)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        logs = [s.path.replace('.py', '.log') for s in scripts]
        task = LocalTask(paths, processes=CPU_COUNT)
        task.run()
        task.wait()
        assert all(os.path.isfile(f) for f in logs)
        for f in paths + logs:
            os.unlink(f)

    def test_terminate_2(self):
        scripts = [get_py_script(i, 10000) for i in range(4)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        logs = [s.path.replace('.py', '.log') for s in scripts]
        task = LocalTask(paths, processes=CPU_COUNT)
        task.run()
        task.close()
        assert all(os.path.isfile(f) for f in logs)
        for f in paths + logs:
            os.unlink(f)

    def test_terminate_3(self):
        scripts = [get_py_script(i, 10000) for i in range(10)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        logs = [s.path.replace('.py', '.log') for s in scripts]
        task = LocalTask(paths, processes=CPU_COUNT)
        task.run()
        with pytest.raises(AssertionError):
            assert all(os.path.isfile(f) for f in logs)
        task.close()
        for f in paths + logs:
            os.unlink(f)

    # ----- This test fails to wait for full job completion ----- #
    #  def test_terminate_4(self):
    #      scripts = [get_py_script(i, 1000000) for i in range(1000)]
    #      [s.write() for s in scripts]
    #      paths = [s.path for s in scripts]
    #      logs = [s.path.replace('.py', '.log') for s in scripts]
    #      task = LocalTask(paths, processes=1)
    #      task.run()

    # ----- This test causes a deadlock ----- #
    #  def test_terminate_5(self):
    #      scripts = [get_py_script(i, 1000000) for i in range(1000)]
    #      [s.write() for s in scripts]
    #      paths = [s.path for s in scripts]
    #      logs = [s.path.replace('.py', '.log') for s in scripts]
    #      task = LocalTask(paths, processes=CPU_COUNT)
    #      task.run()
    #      for path in paths[800:]:
    #          os.unlink(path)

    def test_terminate_6(self):
        scripts = [get_py_script(i, 10000) for i in range(100)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        logs = [s.path.replace('.py', '.log') for s in scripts]
        with LocalTask(paths, processes=CPU_COUNT) as task:
            task.run()
            task.kill()
        assert all(os.path.isfile(path) for path in paths)
        assert any(os.path.isfile(log) for log in logs)
        assert not all(os.path.isfile(log) for log in logs)
        for f in paths + logs:
            if os.path.isfile(f):
                os.unlink(f)

    def test_terminate_7(self):
        scripts = [get_py_script(i, 10000) for i in range(10000)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        logs = [s.path.replace('.py', '.log') for s in scripts]
        with LocalTask(paths, processes=CPU_COUNT) as task:
            task.run()
            time.sleep(5)
            task.kill()
        assert all(os.path.isfile(path) for path in paths)
        assert any(os.path.isfile(log) for log in logs)
        assert not all(os.path.isfile(log) for log in logs)
        for f in paths + logs:
            if os.path.isfile(f):
                os.unlink(f)


class TestLocalPerformance(object):
    def test_performance_1(self):
        scripts = [get_py_script(i, 1000) for i in range(4)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        logs = [s.path.replace('.py', '.log') for s in scripts]
        with LocalTask(paths, processes=CPU_COUNT) as task:
            task.run()
        for path, log in zip(paths, logs):
            assert os.path.isfile(log)
        for f in paths + logs:
            os.unlink(f)

    def test_performance_2(self):
        scripts = [get_py_script(i, 1000) for i in range(16)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        logs = [s.path.replace('.py', '.log') for s in scripts]
        with LocalTask(paths, processes=CPU_COUNT) as task:
            task.run()
        assert all(os.path.isfile(f) for f in logs)
        for f in paths + logs:
            os.unlink(f)

    def test_performance_3(self):
        scripts = [get_py_script(i, 1000) for i in range(32)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        logs = [s.path.replace('.py', '.log') for s in scripts]
        with LocalTask(paths, processes=CPU_COUNT) as task:
            task.run()
        assert all(os.path.isfile(f) for f in logs)
        for f in paths + logs:
            os.unlink(f)

    def test_performance_4(self):
        scripts = [get_py_script(i, 10000) for i in range(64)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        logs = [s.path.replace('.py', '.log') for s in scripts]
        with LocalTask(paths, processes=CPU_COUNT) as task:
            task.run()
        assert all(os.path.isfile(f) for f in logs)
        for f in paths + logs:
            os.unlink(f)