import click
from tabulate import tabulate

from compiler.interpreter import Interpreter
from compiler.parser.MParser import MParser
from compiler.printer import ASTPrinter
from compiler.scanner import MScanner, MLexer
from compiler.types import TypeChecker
from compiler.utils import CompilerError


def _echo_error(err):
    click.echo(click.style(str(err), fg='red'), err=True)


@click.group()
def cli():
    pass


@cli.command('scanner', short_help='Display table of tokens')
@click.argument('file', type=click.File('r'))
def scanner(file):
    """ Displays result of processing given fine by scanner in form of table of tokens """

    try:
        tokens = MScanner().tokenize(file.read())
    except CompilerError as err:
        return _echo_error(err)

    # display table
    click.echo(tabulate(
        [(t.lineno, t.columnno, t.type, t.value) for t in tokens],
        headers=("row", "col", "type", "value"),
        tablefmt="fancy_grid"
    ))


@cli.command('parser', short_help='Run parser on given file')
@click.argument('file', type=click.File('r'))
def parser(file):
    """ Runs parser on given file and displays potential error """

    try:
        MParser().parse(file.read(), lexer=MLexer())
    except CompilerError as err:
        return _echo_error(err)


@cli.command('ast', short_help='Display AST tree')
@click.argument('file', type=click.File('r'))
def ast(file):
    """ Displays AST tree that represents parser file """

    try:
        root = MParser().parse(file.read(), lexer=MLexer(), tracking=True)
    except CompilerError as err:
        return _echo_error(err)

    # print tree
    click.echo(ASTPrinter().generate(root))


@cli.command('check-types', short_help='Performs type check')
@click.argument('file', type=click.File('r'))
def check_types(file):
    """ Performs type check and displays possible errors """

    try:
        root = MParser().parse(file.read(), lexer=MLexer(), tracking=True)

        checker = TypeChecker(collect_errors=True)
        checker.check(root)
    except CompilerError as err:
        return _echo_error(err)

    # print errors
    for err in checker.errors:
        _echo_error(err)


@cli.command('execute', short_help='Executes program')
@click.argument('file', type=click.File('r'))
def execute(file):
    """ Performs parsing, scanning, type check and execution """

    try:
        # parse file
        root = MParser().parse(file.read(), lexer=MLexer(), tracking=True)

        # check types
        TypeChecker().check(root)

        # execute
        Interpreter().execute(root)

    except CompilerError as err:
        return _echo_error(err)


if __name__ == '__main__':
    cli()
