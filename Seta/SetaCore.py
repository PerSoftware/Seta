# -*- coding:utf-8 -*-

"""
PerSoftware Seta Calculation Tool Language (Seta) Copyright (c)2022.
Seta is a tool programming language by PerSoftware Foundation to calculate the expressions in math and physics.
"""

from typing import Union, Iterable, Optional
from io import StringIO
import sys
import os
import operator as sys_operator
import seta_operator

VARIABLE_NUMERIC = 1  # Numeric values
VARIABLE_STRING_CONST = 2  # Constant strings

RUNTIME_STATUS_RUNNING = 0
RUNTIME_STATUS_PREPARING = 1
RUNTIME_STATUS_QUITED = 2
RUNTIME_STATUS_ERROR = 3

TYPEHINT_NUMERIC = Union[int, float]

SETA_SOC = 1

EOF = None

OPERATION_ADD = 'add'  # +
OPERATION_SUB = 'sub'  # -
OPERATION_MUL = 'mul'  # *
OPERATION_DIV = 'div'  # /
OPERATION_POWER = 'power'  # ^ (operator ** in Python)
COMPARISON_ABOVE = '>'
COMPARISON_BELOW = '<'
COMPARISON_EQUAL = '='
COMPARISON_NOTABOVE = '<='
COMPARISON_NOTBELOW = '>='
COMPARISON_NOTEQUAL = '!='


def VARIABLE_TYPE_FORMAT(typeCode: int):
    types = {
        VARIABLE_NUMERIC: 'numeric',
        VARIABLE_STRING_CONST: 'cstring',
    }
    return types.get(typeCode, 'UNKNOWN-TYPE')


class SetaException:
    def __init__(self, clsname: str, msg: str, lineno: int, file: str, code: Union[None, str] = None):
        self.clsname = clsname
        self.msg = msg
        self.lineno = lineno
        self.code = code
        self.file = file

    def format(self) -> str:
        return f"""seta.env.SetaCore.SetaException at line {self.lineno}:
    In file {self.file}, line {self.lineno}:
        {' '.join([self.code[0], *self.code[1]]) if self.code else "[No Code Record]"}
{self.clsname}: {self.msg}
"""


class Variable:
    def __init__(self, name, env, vType: int = VARIABLE_NUMERIC):
        self.__type = vType
        self.__env: SetaRuntime = env
        self.__value = None
        self.__name = name

    @property
    def name(self):
        return self.__name

    @property
    def type(self) -> int:
        return self.__type

    @property
    def defined(self) -> bool:
        return self.__value is not None

    @property
    def undefined(self) -> bool:
        return self.__value is None

    @property
    def value(self) -> Union[str, TYPEHINT_NUMERIC]:
        return self.__value

    @property
    def numeric(self) -> bool:
        return self.__type == VARIABLE_NUMERIC

    @property
    def string(self) -> bool:
        return self.__type == VARIABLE_STRING_CONST

    def set(self, value: Union[str, TYPEHINT_NUMERIC]) -> bool:
        if isinstance(value, str):
            if self.__type == VARIABLE_STRING_CONST:
                self.__value = value
                return True
            else:
                self.__env.error(SetaException(
                    clsname='ValueException',
                    msg=f'Variable "{self.__name}" expected type {VARIABLE_TYPE_FORMAT(self.__type)},'
                        f' but an unexpected type was given.',
                    lineno=self.__env.current['lineno'],
                    file=self.__env.current['file'],
                    code=self.__env.current['code']
                ))
                return False
        else:
            if self.__type == VARIABLE_NUMERIC:
                self.__value = value
                return True
            else:
                self.__env.error(SetaException(
                    clsname='ValueException',
                    msg=f'Variable "{self.__name}" expected type {VARIABLE_TYPE_FORMAT(self.__type)},'
                        f' but an unexpected type was given.',
                    lineno=self.__env.current['lineno'],
                    file=self.__env.current['file'],
                    code=self.__env.current['code']
                ))
                return False

    @property
    def positive(self) -> Union[bool, None]:
        if self.numeric:
            return self.value > 0
        return

    @property
    def negative(self) -> Union[bool, None]:
        if self.numeric:
            return self.value < 0
        return

    @property
    def zero(self) -> Union[bool, None]:
        if self.numeric:
            return self.value == 0
        return


class StandardIO:
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[36m'
    DEFAULT = '\033[0m'

    def __init__(self):
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.stderr = sys.stderr

    def input(self, msg: Union[str, bytes, None]):
        return input(msg)

    def output(self, msg: str):
        print(msg, end='')

    def print(self, msg: str, end: str = '\n'):
        print(msg, end=end)

    def setColor(self, color: str):
        print(color, end='')


class Package:
    def __init__(self, runtime, name: str):
        self.runtime: SetaRuntime = runtime
        self.pool = dict()
        self.name= name

    def ObjectAppend(self, key: str, obj: object) -> bool:  # Return if the key already existed before
        ex = key in self.pool
        self.pool[key] = obj
        return ex

    def ObjectSearch(self, key: str) -> Union[object, None]:
        return self.pool.get(key, None)

    def ObjectRemove(self, key: str) -> bool:  # Return if succeeded
        if key in self.pool:
            del self.pool[key]
            return True
        return False


class BuiltinsPackage(Package):
    def __init__(self, runtime):
        super(BuiltinsPackage, self).__init__(runtime, 'builtins')
        self.ObjectAppend('display', self.display)
        self.ObjectAppend('ftc', self.ftc)
        self.ObjectAppend('wrap', self.wrap)
        self.ObjectAppend('nInput', self.nInput)
        self.ObjectAppend('breakpoint', self.breakpoint)

    def breakpoint(self):
        npf = ''
        for var in self.runtime.namespace.values():
            npf += f'\tVariable:\t{var.name}\n\tType:\t\t{self.runtime.stdio.BLUE}{VARIABLE_TYPE_FORMAT(var.type)}{self.runtime.stdio.YELLOW}\n\tValue:\t\t{var.value}\n\n'
        self.runtime.stdio.setColor(self.runtime.stdio.YELLOW)
        self.runtime.stdio.output(f'\n\n{"=" * 30}\nBreakpoint at line {self.runtime.current["lineno"]}:\n'
                                  f'    File {self.runtime.current["file"]}, line {self.runtime.current["lineno"]}:\n'
                                  f'        {" ".join([self.runtime.current["code"][0], *self.runtime.current["code"][1]])}\n'
                                  f'Program debug information:\n'
                                  f'Runtime Status: {self.runtime.status}\n'
                                  f'Calculation Result Cathe: {self.runtime.ams}\n'
                                  f'Unreachable If-Comparison Stack Length: {self.runtime.ifs}\n'
                                  f'Packages: \n\t' + "\n\t".join(self.runtime.packages.keys()) + '\n' + \
                                  f'Namespace: \n' + npf + \
                                  f'Here is the end of the breakpoint debug information.\n{"=" * 30}\n\n')
        self.runtime.stdio.setColor(self.runtime.stdio.DEFAULT)

    def nInput(self, arg: str, *msg: str):
        if not Seta.requireIdentifier(arg):
            self.runtime.error(SetaException(
                clsname='ArgumentException',
                msg='Force type change expected an identifier name, but an invalid argument appeared.',
                lineno=self.runtime.current['lineno'],
                file=self.runtime.support.f.name,
                code=self.runtime.current['code']
            ))
            return
        var = self.runtime.NamespaceSearch(arg)
        if var is None:
            self.runtime.error(SetaException(
                clsname='VariableException',
                msg=f'Cannot find variable {arg}.',
                lineno=self.runtime.current['lineno'],
                file=self.runtime.support.f.name,
                code=self.runtime.current['code']
            ))
            return
        if var.type != VARIABLE_NUMERIC:
            self.runtime.error(SetaException(
                clsname='TypeException',
                msg=f'Force type change expected a numeric variable, but {VARIABLE_TYPE_FORMAT(var.type)} was given.',
                lineno=self.runtime.current['lineno'],
                file=self.runtime.support.f.name,
                code=self.runtime.current['code']
            ))
            return
        if not msg:
            msg = 'Input requires to be numeric, please enter again:'.split(' ')
        msg = ' '.join(msg)
        num = 0
        while True:
            i = self.runtime.stdio.input('')
            num = Seta.requireReal(i)
            if num is None:
                self.runtime.stdio.output(msg)
            else:
                break
        var.set(num)

    def wrap(self, lines: str = '1'):
        lines = Seta.requireInt(lines)
        if lines is None:
            self.runtime.error(SetaException(
                clsname='ArgumentException',
                msg='Argument 1 "lines" expected a positive integer.',
                lineno=self.runtime.current['lineno'],
                file=self.runtime.support.f.name,
                code=self.runtime.current['code']
            ))
            return
        if lines <= 0:
            self.runtime.error(SetaException(
                clsname='ArgumentException',
                msg='Argument 1 "lines" expected a positive integer.',
                lineno=self.runtime.current['lineno'],
                file=self.runtime.support.f.name,
                code=self.runtime.current['code']
            ))
            return
        self.runtime.stdio.output('\n' * lines)

    def ftc(self, arg: str, tar: str):
        """
        Force type changing.
        :param arg: the variable name
        :param tar: target numeric type (choices: integer, float)
        :return: None
        """
        if not Seta.requireIdentifier(arg):
            self.runtime.error(SetaException(
                clsname='ArgumentException',
                msg='Force type change expected an identifier name, but an invalid argument appeared.',
                lineno=self.runtime.current['lineno'],
                file=self.runtime.support.f.name,
                code=self.runtime.current['code']
            ))
            return
        var = self.runtime.NamespaceSearch(arg)
        if var is None:
            self.runtime.error(SetaException(
                clsname='VariableException',
                msg=f'Cannot find variable {arg}.',
                lineno=self.runtime.current['lineno'],
                file=self.runtime.support.f.name,
                code=self.runtime.current['code']
            ))
            return
        if var.type != VARIABLE_NUMERIC:
            self.runtime.error(SetaException(
                clsname='TypeException',
                msg=f'Force type change expected a numeric variable, but {VARIABLE_TYPE_FORMAT(var.type)} was given.',
                lineno=self.runtime.current['lineno'],
                file=self.runtime.support.f.name,
                code=self.runtime.current['code']
            ))
            return
        func = {
            'integer': int,
            'float': float,
        }.get(tar, None)
        if func is None:
            self.runtime.error(SetaException(
                clsname='ArgumentException',
                msg=f'Invalid numeric type was given. Possible choices: integer, float.',
                lineno=self.runtime.current['lineno'],
                file=self.runtime.support.f.name,
                code=self.runtime.current['code']
            ))
            return
        var.set(func(var.value))

    def display(self, var: str):
        if not Seta.requireIdentifier(var):
            self.runtime.error(SetaException(
                clsname='ArgumentException',
                msg=f'Argument 1 "var" expected a variable.',
                lineno=self.runtime.current['lineno'],
                file=self.runtime.support.f.name,
                code=self.runtime.current['code']
            ))
            return
        v = self.runtime.NamespaceSearch(var)
        if v is None:
            self.runtime.error(SetaException(
                clsname='ArgumentException',
                msg=f'Argument 1 "var" expected a variable, but variable {var} was not found.',
                lineno=self.runtime.current['lineno'],
                file=self.runtime.support.f.name,
                code=self.runtime.current['code']
            ))
            return
        self.runtime.stdio.output(v.value)


class SetaRuntime:
    def __init__(self):
        self.status = RUNTIME_STATUS_PREPARING
        self.namespace = dict()
        self.stdio = StandardIO()
        self.status = RUNTIME_STATUS_RUNNING
        self.current = {
            'lineno': 0,
            'file': '<stdin>',
            'code': None,
        }
        self.operation = self.Operation(self)
        self.support = None
        self.ams = 0
        self.ifs = 0  # Count the "if" instructions in an unreachable if-comparison block
        self.ptr = self.NullPointerTraceback
        self.packages = {
            'builtins': BuiltinsPackage(self),
        }

    def NullPointerTraceback(self):
        self.error(SetaException(
            clsname='NullPointerException',
            msg='Cannot call the program pointer before setting the pointer address.',
            lineno=self.current['lineno'],
            file=self.support.f.name,
            code=self.current['code']
        ))

    def setSupport(self, support):
        support: Union[SetaStringOperationCode]
        self.support = support
        self.current = {
            'lineno': 2,
            'file': self.support.f.name,
            'code': self.support.instruction,
        }

    @property
    def instruction(self):
        l = self.current['code']
        self.current['lineno'] += 1
        self.current['code'] = self.support.instruction
        return l

    def error(self, exc: SetaException):
        self.stdio.setColor(self.stdio.RED)
        self.stdio.print(f"""

{exc.format()}""")
        self.status = RUNTIME_STATUS_ERROR
        self.stdio.setColor(self.stdio.DEFAULT)

    class Operation:
        def __init__(self, env):
            self.__env: SetaRuntime = env

        def add(self, arg1: Variable, arg2: Variable) -> Union[TYPEHINT_NUMERIC, None]:
            if not arg1.numeric:
                self.__env.error(SetaException(
                    clsname='TypeException',
                    msg=f'Operation ADD needs variable "{arg1.name}" to be numeric.',
                    lineno=self.__env.current['lineno'],
                    file=self.__env.current['file'],
                    code=self.__env.current['code']
                ))
                return None
            if not arg2.numeric:
                self.__env.error(SetaException(
                    clsname='TypeException',
                    msg=f'Operation ADD needs variable "{arg1.name}" to be numeric.',
                    lineno=self.__env.current['lineno'],
                    file=self.__env.current['file'],
                    code=self.__env.current['code']
                ))
                return None
            return arg1.value + arg2.value

        def sub(self, arg1: Variable, arg2: Variable) -> Union[TYPEHINT_NUMERIC, None]:
            if not arg1.numeric:
                self.__env.error(SetaException(
                    clsname='TypeException',
                    msg=f'Operation SUB needs variable "{arg1.name}" to be numeric.',
                    lineno=self.__env.current['lineno'],
                    file=self.__env.current['file'],
                    code=self.__env.current['code']
                ))
                return None
            if not arg2.numeric:
                self.__env.error(SetaException(
                    clsname='TypeException',
                    msg=f'Operation SUB needs variable "{arg1.name}" to be numeric.',
                    lineno=self.__env.current['lineno'],
                    file=self.__env.current['file'],
                    code=self.__env.current['code']
                ))
                return None
            return arg1.value - arg2.value

        def mul(self, arg1: Variable, arg2: Variable) -> Union[TYPEHINT_NUMERIC, None]:
            if not arg1.numeric:
                self.__env.error(SetaException(
                    clsname='TypeException',
                    msg=f'Operation MUL needs variable "{arg1.name}" to be numeric.',
                    lineno=self.__env.current['lineno'],
                    file=self.__env.current['file'],
                    code=self.__env.current['code']
                ))
                return None
            if not arg2.numeric:
                self.__env.error(SetaException(
                    clsname='TypeException',
                    msg=f'Operation MUL needs variable "{arg1.name}" to be numeric.',
                    lineno=self.__env.current['lineno'],
                    file=self.__env.current['file'],
                    code=self.__env.current['code']
                ))
                return None
            return arg1.value * arg2.value

        def div(self, arg1: Variable, arg2: Variable) -> Union[TYPEHINT_NUMERIC, None]:
            if not arg1.numeric:
                self.__env.error(SetaException(
                    clsname='TypeException',
                    msg=f'Operation DIV needs variable "{arg1.name}" to be numeric.',
                    lineno=self.__env.current['lineno'],
                    file=self.__env.current['file'],
                    code=self.__env.current['code']
                ))
                return None
            if not arg2.numeric:
                self.__env.error(SetaException(
                    clsname='TypeException',
                    msg=f'Operation DIV needs variable "{arg1.name}" to be numeric.',
                    lineno=self.__env.current['lineno'],
                    file=self.__env.current['file'],
                    code=self.__env.current['code']
                ))
                return None
            if arg2.value == 0:
                self.__env.error(SetaException(
                    clsname='MathException',
                    msg=f'Variable {arg1.name} is divided by zero.',
                    lineno=self.__env.current['lineno'],
                    file=self.__env.current['file'],
                    code=self.__env.current['code']
                ))
                return None
            return arg1.value / arg2.value

        def power(self, arg1: Variable, arg2: Variable) -> Union[TYPEHINT_NUMERIC, None]:
            if not arg1.numeric:
                self.__env.error(SetaException(
                    clsname='TypeException',
                    msg=f'Operation DIV needs variable "{arg1.name}" to be numeric.',
                    lineno=self.__env.current['lineno'],
                    file=self.__env.current['file'],
                    code=self.__env.current['code']
                ))
                return None
            if not arg2.numeric:
                self.__env.error(SetaException(
                    clsname='TypeException',
                    msg=f'Operation DIV needs variable "{arg1.name}" to be numeric.',
                    lineno=self.__env.current['lineno'],
                    file=self.__env.current['file'],
                    code=self.__env.current['code']
                ))
                return None
            if arg1.value == arg2.value == 0:
                self.__env.error(SetaException(
                    clsname='MathException',
                    msg=f'The base of a zero exponential cannot be zero.',
                    lineno=self.__env.current['lineno'],
                    file=self.__env.current['file'],
                    code=self.__env.current['code']
                ))
                return None
            return arg1.value ** arg2.value

        @staticmethod
        def equal(arg1: Variable, arg2: Variable) -> bool:
            return arg1.value == arg2.value

        @staticmethod
        def above(arg1: Variable, arg2: Variable) -> bool:
            return arg1.value > arg2.value

        @staticmethod
        def below(arg1: Variable, arg2: Variable) -> bool:
            return arg1.value < arg2.value

        @staticmethod
        def notAbove(arg1: Variable, arg2: Variable) -> bool:
            return arg1.value <= arg2.value

        @staticmethod
        def notBelow(arg1: Variable, arg2: Variable) -> bool:
            return arg1.value >= arg2.value

        @staticmethod
        def notEqual(arg1: Variable, arg2: Variable) -> bool:
            return arg1.value != arg2.value

    def NamespaceSearch(self, name: str) -> Union[Variable, None]:
        return self.namespace.get(name, None)

    def NamespaceInput(self, value: Variable) -> bool:  # Return if the variable has already existed before.
        ex = value.name in self.namespace
        self.namespace[value.name] = value
        return ex

    def PackageSearch(self, name: str) -> Union[Package, None]:
        return self.packages.get(name, None)

    def PackageInput(self, pack: Package) -> bool:  # Return if the package has already existed before.
        ex = pack.name in self.packages
        self.packages[pack.name] = pack
        return ex

    def run(self):
        while True:
            if self.status:
                sys.exit()
            if self.current['code'] == EOF:
                if self.ifs:
                    self.error(SetaException(
                        clsname='BlockException',
                        msg='If-comparison block is not closed at the end of the program.',
                        lineno=self.current['lineno'],
                        file=self.support.f.name,
                        code=self.current['code']
                    ))
                sys.exit()
            com: str = self.current['code'][0]
            args = self.current['code'][1]
            if com.lower() == 'endif':
                try:
                    self.com_endif(*args)
                except TypeError:
                    self.error(SetaException(
                        clsname='ArgumentException',
                        msg='Invalid number of the arguments.',
                        lineno=self.current['lineno'],
                        file=self.support.f.name,
                        code=self.current['code']
                    ))
                self.current['lineno'] += 1
                self.current['code'] = self.support.instruction
                continue

            # Here skip the unreachable instructions caused by if-comparison.
            if self.ifs:
                if com.lower() == 'if':  # Increase the if-comparison block counter
                    self.ifs = self.ifs + 1  # It'll be cleared by endif instruction
                self.current['lineno'] += 1
                self.current['code'] = self.support.instruction
                continue

            if com.lower() == 'set':
                try:
                    self.com_set(*args)
                except TypeError:
                    self.error(SetaException(
                        clsname='ArgumentException',
                        msg='Invalid number of the arguments.',
                        lineno=self.current['lineno'],
                        file=self.support.f.name,
                        code=self.current['code']
                    ))
            elif com.lower() == 'calc':
                try:
                    self.com_calc(*args)
                except TypeError:
                    self.error(SetaException(
                        clsname='ArgumentException',
                        msg='Invalid number of the arguments.',
                        lineno=self.current['lineno'],
                        file=self.support.f.name,
                        code=self.current['code']
                    ))
            elif com.lower() == 'load':
                try:
                    self.com_load(*args)
                except TypeError:
                    self.error(SetaException(
                        clsname='ArgumentException',
                        msg='Invalid number of the arguments.',
                        lineno=self.current['lineno'],
                        file=self.support.f.name,
                        code=self.current['code']
                    ))
            elif com.lower() == 'emp':
                try:
                    self.com_emp(*args)
                except TypeError:
                    self.error(SetaException(
                        clsname='ArgumentException',
                        msg='Invalid number of the arguments.',
                        lineno=self.current['lineno'],
                        file=self.support.f.name,
                        code=self.current['code']
                    ))
            elif com.lower() == 'if':
                try:
                    self.com_if(*args)
                except TypeError:
                    self.error(SetaException(
                        clsname='ArgumentException',
                        msg='Invalid number of the arguments.',
                        lineno=self.current['lineno'],
                        file=self.support.f.name,
                        code=self.current['code']
                    ))
            elif com.lower() == 'call':
                try:
                    self.com_call(*args)
                except TypeError:
                    self.error(SetaException(
                        clsname='ArgumentException',
                        msg='Invalid number of the arguments.',
                        lineno=self.current['lineno'],
                        file=self.support.f.name,
                        code=self.current['code']
                    ))
            else:
                self.error(SetaException(
                    clsname='UnsupportedOperationException',
                    msg=f'Unsupported operation {com}.',
                    lineno=self.current['lineno'],
                    file=self.support.f.name,
                    code=self.current['code']
                ))
            self.current['lineno'] += 1
            self.current['code'] = self.support.instruction

    def com_call(self, *args):
        if self.ptr is None:
            self.error(SetaException(
                clsname='NullPointerException',
                msg=f'Cannot call the program pointer before setting the pointer address.',
                lineno=self.current['lineno'],
                file=self.support.f.name,
                code=self.current['code']
            ))
            return
        if not callable(self.ptr):
            self.error(SetaException(
                clsname='ArgumentException',
                msg=f'The target of the calling is not callable.',
                lineno=self.current['lineno'],
                file=self.support.f.name,
                code=self.current['code']
            ))
            return
        self.ptr(*args)

    def com_load(self, package: str, identifier: Union[str, None] = None):
        """
        Load an object and make the program pointer point to it.
        :param package: the package name (default `builtins`)
        :param identifier: the target object
        :return: None
        """
        if identifier is None:  # The package name "builtins" is ignored.
            identifier = package
            package = 'builtins'
        pack = self.PackageSearch(package)
        if pack is None:
            self.error(SetaException(
                clsname='PackageException',
                msg=f'Cannot find package {package}.',
                lineno=self.current['lineno'],
                file=self.support.f.name,
                code=self.current['code']
            ))
            return
        obj: Union[object, None] = pack.ObjectSearch(identifier)
        if obj is None:
            self.error(SetaException(
                clsname='PackageException',
                msg=f'Cannot find object {identifier} in package {package}.',
                lineno=self.current['lineno'],
                file=self.support.f.name,
                code=self.current['code']
            ))
            return
        self.ptr = obj

    def com_endif(self):
        self.ifs = self.ifs - 1 if self.ifs else 0

    def com_if(self, arg1, cmp, arg2):
        var1 = Seta.requireReal(arg1)
        if arg1 == '@AMS':
            var1 = self.ams
        if var1 is None:
            var1 = self.NamespaceSearch(arg1)
        if var1 is None:
            self.error(SetaException(
                clsname='VariableException',
                msg=f'Undeclared variable {arg1} cannot be resolved.',
                lineno=self.current['lineno'],
                file=self.support.f.name,
                code=self.current['code']
            ))
            return
        else:
            var1 = var1.value if isinstance(var1, Variable) else var1
        var2 = Seta.requireReal(arg2)
        if arg2 == '@AMS':
            var2 = self.ams
        if var2 is None:
            var2 = self.NamespaceSearch(arg2)
        if var2 is None:
            self.error(SetaException(
                clsname='VariableException',
                msg=f'Undeclared variable {arg2} cannot be resolved.',
                lineno=self.current['lineno'],
                file=self.support.f.name,
                code=self.current['code']
            ))
            return
        else:
            var2 = var2.value if isinstance(var2, Variable) else var2
        oper = {
            COMPARISON_ABOVE: seta_operator.above,
            COMPARISON_BELOW: seta_operator.below,
            COMPARISON_EQUAL: seta_operator.equal,
            COMPARISON_NOTABOVE: seta_operator.notabove,
            COMPARISON_NOTBELOW: seta_operator.notbelow,
            COMPARISON_NOTEQUAL: seta_operator.notequal,
        }.get(cmp, None)
        if oper is None:
            self.error(SetaException(
                clsname='OperatorException',
                msg=f'Unresolved operator {cmp} appeared at argument 2 "cmp".',
                lineno=self.current['lineno'],
                file=self.support.f.name,
                code=self.current['code']
            ))
            return
        try:
            res: bool = oper(var1, var2)
        except Exception:
            self.error(SetaException(
                clsname='ComparisonException',
                msg=f'Cannot compare value {arg1} with value {arg2}.',
                lineno=self.current['lineno'],
                file=self.support.f.name,
                code=self.current['code']
            ))
            return
        if not res:
            self.ifs = 1

    def com_emp(self):
        pass

    def com_calc(self, operation: str, arg1: str, arg2: str, res: str):
        oper = {
            OPERATION_ADD: sys_operator.add,
            OPERATION_SUB: sys_operator.sub,
            OPERATION_MUL: sys_operator.mul,
            OPERATION_DIV: sys_operator.truediv,
            OPERATION_POWER: sys_operator.pow,
        }.get(operation, None)
        if oper is None:
            self.error(SetaException(
                clsname='ArgumentException',
                msg='Invalid operation. Possible operations: add, sub, mul, div, power.',
                lineno=self.current['lineno'],
                file=self.support.f.name,
                code=self.current['code']
            ))
            return
        var1 = Seta.requireReal(arg1)
        if arg1 == '@AMS':
            var1 = self.ams
        if var1 is None:
            var1 = self.NamespaceSearch(arg1)
        if var1 is None:
            self.error(SetaException(
                clsname='VariableException',
                msg=f'Undeclared variable {arg1} cannot be resolved.',
                lineno=self.current['lineno'],
                file=self.support.f.name,
                code=self.current['code']
            ))
            return
        else:
            var1 = var1.value if isinstance(var1, Variable) else var1
        var2 = Seta.requireReal(arg2)
        if arg2 == '@AMS':
            var2 = self.ams
        if var2 is None:
            var2 = self.NamespaceSearch(arg2)
        if var2 is None:
            self.error(SetaException(
                clsname='VariableException',
                msg=f'Undeclared variable {arg2} cannot be resolved.',
                lineno=self.current['lineno'],
                file=self.support.f.name,
                code=self.current['code']
            ))
            return
        else:
            var2 = var2.value if isinstance(var2, Variable) else var2
        if operation == OPERATION_DIV and var2 == 0:
            self.error(SetaException(
                clsname='MathException',
                msg=f'A numeric value cannot be divided by zero.',
                lineno=self.current['lineno'],
                file=self.support.f.name,
                code=self.current['code']
            ))
            return
        if operation == OPERATION_POWER and var1 == var2 == 0:
            self.error(SetaException(
                clsname='MathException',
                msg=f'The base of a zero exponential cannot be zero.',
                lineno=self.current['lineno'],
                file=self.support.f.name,
                code=self.current['code']
            ))
            return
        if not Seta.requireIdentifier(res):
            self.error(SetaException(
                clsname='ArgumentException',
                msg=f'Argument 3 "res" must be a valid identifier name.',
                lineno=self.current['lineno'],
                file=self.support.f.name,
                code=self.current['code']
            ))
            return
        r = oper(var1, var2)
        self.ams = r
        var = self.NamespaceSearch(res)
        if var is None:
            var = Variable(res, self, VARIABLE_NUMERIC)
            self.NamespaceInput(var)
        var.set(r)

    def com_set(self, vType: str, name: str, value: str, *texts):
        if not Seta.requireIdentifier(name):
            self.error(SetaException(
                clsname='ArgumentException',
                msg='Argument 2 "name" must be a valid identifier name.',
                lineno=self.current['lineno'],
                file=self.support.f.name,
                code=self.current['code']
            ))
            return
        if vType == 'numeric':
            value = Seta.requireReal(value)
            if value is None:
                self.error(SetaException(
                    clsname='TypeException',
                    msg=f'Variable {name} is declared as numeric type, but non-numeric value is given.',
                    lineno=self.current['lineno'],
                    file=self.support.f.name,
                    code=self.current['code']
                ))
                return
            if texts.__len__():
                self.error(SetaException(
                    clsname='ArgumentException',
                    msg=f'Invalid number of the arguments: numeric setting operation expected 3 argument,'
                        f' but {str(3 + texts.__len__())} was given.',
                    lineno=self.current['lineno'],
                    file=self.support.f.name,
                    code=self.current['code']
                ))
                return
            var = Variable(name, self, VARIABLE_NUMERIC)
            var.set(value)
            self.NamespaceInput(var)
        elif vType == 'cstring':
            var = Variable(name, self, VARIABLE_STRING_CONST)
            var.set(' '.join([value, *texts]))
            self.NamespaceInput(var)
        else:
            self.error(SetaException(
                clsname='ArgumentException',
                msg=f'A type should be specified during a variable declaration. Possible types: numeric, cstring.',
                lineno=self.current['lineno'],
                file=self.support.f.name,
                code=self.current['code']
            ))
            return


class SetaStringOperationCode:
    def __init__(self, stream: StringIO, runtime: SetaRuntime):
        self.runtime = runtime
        self.f = stream
        self.text = stream.readlines()
        self.pointer = 0
        precheck = self.precheck
        if precheck:
            msg = {
                1: 'Invalid Seta string operation code file.',
                2: 'Invalid Seta string operation code file.',
                3: 'Version too high, use the newer interpreter.',
                4: 'Invalid Seta string operation code file.',
                5: 'Empty file.',
            }
            # stream.seek(0)
            runtime.error(SetaException(
                clsname='PrecheckException',
                msg=msg.get(precheck, 'Unknown exception happened during precheck.'),
                lineno=1,
                file=stream.name,
                code=stream.readline(),
            ))

    @property
    def precheck(self) -> int:
        """
        Check the first line for pre-checking file.
        :return: result code, 0 for pass, or others for failure.

        Possible values of the result code to return:
        0   Pre-check passed
        1   Wrong flag
        2   Invalid version code
        3   Version too high
        4   Invalid line format
        5   EOF on the line
        """
        try:
            line1 = self.text[self.pointer]
            self.pointer += 1
        except IndexError:
            line1 = EOF
        if line1:
            l = line1[:-1].split(' ')
            if l.__len__() == 2:
                flag: str = l[0]
                version: str = l[1]
                if flag != 'SETA-SOC':
                    return 1
                try:
                    version: float = float(version)
                except ValueError:
                    return 2
                if version > Seta.version:  # Version is too high
                    return 3
                return 0
            else:
                return 4
        else:
            return 5

    @property
    def instruction(self):
        try:
            l = self.text[self.pointer]
            self.pointer += 1
        except IndexError:
            l = EOF
        if not l:
            return EOF
        if l in ('\n', '\n\r'):
            return 'emp', ()
        l = l[:-1].split(' ')
        if not l.__len__() - 1:
            return l[0], ()
        else:
            return l[0], l[1:]


class Seta:
    version = 1.0

    @staticmethod
    def requireInt(i: str):
        try:
            r = eval(i)
        except Exception:
            return None
        if not isinstance(r, int):
            return None
        else:
            return r

    @staticmethod
    def requireFloat(f: str):
        try:
            r = eval(f)
        except Exception:
            return None
        if not isinstance(r, float):
            return None
        else:
            return r

    @staticmethod
    def requireReal(r: str):
        try:
            r = eval(r)
        except Exception:
            return None
        if isinstance(r, int) or isinstance(r, float):
            return r
        else:
            return None

    @staticmethod
    def requireImg(i: str):
        try:
            r = eval(i)
        except Exception:
            return None
        if not isinstance(r, complex):
            return None
        else:
            return r

    @staticmethod
    def requireIdentifier(i: str) -> bool:
        """
        Check if a string can be an identifier.
        :param i: identifier name
        :return: judging result
        """
        if not i:
            return False
        for char in i:
            if 'a' <= char <= 'z' or 'A' <= char <= 'Z' or \
                    char in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '_', '#'):
                continue
            return False
        if i[0] in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '#'):
            return False
        return True

    def run(self):
        self.runtime.run()

    def __init__(self, path: str, mode: int = SETA_SOC):
        self.runtime = SetaRuntime()
        if not os.path.isfile(path):
            self.runtime.error(SetaException(
                clsname='RunningException',
                msg=f'File "{path}" does not exist.',
                lineno=0,
                file=path,
            ))
        else:
            try:
                if mode == SETA_SOC:
                    self.file = open(path, 'r')
                    self.support = SetaStringOperationCode(self.file, self.runtime)
                    self.runtime.setSupport(self.support)
                else:
                    self.runtime.error(SetaException(
                        clsname='RunningException',
                        msg=f'Running mode {str(mode)} is invalid.',
                        lineno=0,
                        file=path,
                    ))
            except Exception:
                self.runtime.error(SetaException(
                    clsname='RunningException',
                    msg=f'Cannot open file "{path}".',
                    lineno=0,
                    file=path,
                ))
