"""Base model"""
import os
import re
import subprocess
from dataclasses import dataclass, field
from typing import Tuple

from colorama import Fore, Style


@dataclass
class LangfuseTrace:
    session_id: str
    user_id: str
    tags: list
    _id: str = field(init=False)


class BaseModel:

    # Base logs
    _title: str = 'Initializing ...'
    _context: str = 'Context ...'
    _finished_failed = 'Finish with errors ...'
    _finished_success = 'Finish success'

    # Base methods for print
    @property
    def title(self) -> str:
        return self._title

    @property
    def context(self) -> str:
        return self._context

    @property
    def finished_failed(self) -> str:
        return self._finished_failed

    @property
    def finished_success(self) -> str:
        return self._finished_success

    def title_print(self) -> None:
        self.print_ligth(f'\n\n{self.title.format(**self.__dict__)}')

    def context_print(self) -> None:
        self.print_bold(self.context.format(**self.__dict__))

    def resolve_success_print(self) -> None:
        self.print_green_bold(self.finished_success.format(**self.__dict__))

    def resolve_error_print(self) -> None:
        self.print_red_bold(self.finished_success.format(**self.__dict__))

    def print_green_bold(self, text: str) -> None:
        print(Fore.GREEN + Style.BRIGHT + text + Style.RESET_ALL)

    def print_green_light(self, text: str) -> None:
        print(Fore.LIGHTGREEN_EX + text + Style.RESET_ALL)

    def print_bold(self, text: str) -> None:
        print(Style.BRIGHT + text + Style.RESET_ALL)

    def print_grey(self, text: str) -> None:
        print(Style.DIM + text + Style.RESET_ALL)

    def print_ligth(self, text: str) -> None:
        print(Fore.LIGHTWHITE_EX + text + Style.RESET_ALL)

    def print_red_bold(self, text: str) -> None:
        print(Fore.RED + Style.BRIGHT + text + Style.RESET_ALL)

    # Base methods for execute
    def run(self, *args, **kwargs) -> None:
        self.title_print()
        self.context_print()
        self.resolve(*args, **kwargs)
        self.resolve_success_print() if self.success() else self.resolve_error_print()

    def resolve(self, *args, **kwargs):
        raise NotImplementedError

    def success(self) -> bool:
        raise NotImplementedError

    def sanitize_code(self, code: str) -> str:
        pattern_string = re.search(r'```(.*?)```', code, re.DOTALL)
        sanitize_code = pattern_string.group(1)
        return sanitize_code

    def execute(self, code: str, file_name: str = 'temp', timeout: int = 60) -> Tuple[str, str]:
        file_name = f'/app/scripts/{file_name}.sh'
        script_output = ''
        execution_error = ''
        self.print_ligth(f'Executing \n{code}')
        # Writing the script to a temporary file with all permissions
        with open(file_name, 'w') as f:
            f.write(code)
            f.flush()
            os.fchmod(f.fileno(), 0o777)

        try:
            result = subprocess.run(
                ['bash', file_name], stdout=subprocess.PIPE, text=True, check=True, timeout=timeout)
            script_output = result.stdout
            self.print_green_light(
                f'{script_output if script_output else "Success"}')

        except subprocess.CalledProcessError as e:
            self.print_red_bold(f"{e}")
            execution_error = e
        except Exception as e:
            self.print_red_bold(f"{e}")
            execution_error = e

        return script_output, execution_error
