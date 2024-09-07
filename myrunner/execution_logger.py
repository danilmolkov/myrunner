import sys
class ExecutionLogger:

    class Colors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKCYAN = '\033[96m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        TERRACOTTA = '\033[38;2;201;100;59m'
        UNDERLINE = '\033[4m'

    allowed_modes = [
        'disable',
        'full',
        'full-no-command',
    ]

    mode = 'disable'

    def __init__(self, mode: str):
        self.set(mode)

    __output_fd = sys.stdout

    def set(self, mode: str):
        self.mode = mode
        self.start = ''
        self.line = ''
        self.middle = ''
        self.end = ''
        if mode in ['full', 'full-no-command']:
            self.start = f'{self.Colors.TERRACOTTA}┌─ {self.Colors.ENDC}'
            self.line = f'{self.Colors.TERRACOTTA}│ {self.Colors.ENDC}'
            self.middle = f'{self.Colors.TERRACOTTA}├─ {self.Colors.ENDC}'
            self.end = f'{self.Colors.TERRACOTTA}└─ {self.Colors.ENDC}'

    def set_output_fd(self, fd):
        self.__output_fd = fd

    def print_runname(self, string: str):
        print(f'{self.middle if self.mode == "full" else self.start}Executing: {self.Colors.TERRACOTTA}{string}{self.Colors.OKCYAN}')

    def print_command(self, text: str):
        if self.mode != 'full':
            return
        # Split the text into lines
        lines = text.splitlines()
        # Append '|' to each line
        modified_lines = [self.line + line for line in lines]
        # Join the lines back into a single string with newline characters
        print('\n'.join(modified_lines), file=self.__output_fd)

    def print_cwd(self, string: str):
        if self.mode == 'full':
            print(f'{self.start}{string}', file=self.__output_fd)

    def print_output(self, string: str):
        print(f'{self.line}{string}', file=self.__output_fd)

    def print_time(self, string: str):
        print(f'{self.end}{string}')

    def get_fd(self):
        return self.__output_fd
