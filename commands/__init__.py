"""Light commands available to all users. But sudo only admin or sudoers"""

from typing import Dict, Callable, Tuple

from views import *
import views


def init_command(*commands: Tuple[str]) -> Dict[str, Callable]:
    """
    Initialize commands. Get commands function by name.
    :param commands: commands, like 'ban', 'warn', etc.
    :return: command and triggered function.
    """
    _commands = {}
    for command in commands:
        for view in views.__all__:
            if command == view.split('_')[0]:
                try:
                    _commands[f'!{command}'] = getattr(globals()[view], view)
                except AttributeError as err:
                    print(
                        f'{err}. '
                        f'May be you forget add or rename function. Module and function name must be the same name!'
                    )
    return _commands

