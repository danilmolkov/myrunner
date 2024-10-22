from sys import stdout

class Logger(object):
    _instance = None
    __no_colors = True
    __pretty_mode = True

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls.__no_colors = True
            cls.__pretty_mode = True

        return cls._instance

    # def pretty_mode(self, )

    supported_pretty_modes = [
        'disable',
        'full',
        'full-no-command',
    ]

    __output_fd = stdout

    def set_output_fd(self, fd):
        self.__output_fd = fd

    def get_fd(self):
        return self.__output_fd

    __runname_fmt = ''
    __error_fmt = ''
    __output_fmt = '{0}'
    __end_fmt = ''
    __stderr_fmt = ''

    def update_formats(self, no_colors: bool):
        self.__no_colors = no_colors
        if self.__no_colors:
            self.__runname_fmt = '┌─ {0}: executing'
            self.__error_fmt = '{0}'
            self.__output_fmt = '│ {0}'
            self.__end_fmt = '└─ {0}'
            self.__stderr_fmt = '{0}\n'
        else:
            self.__error_fmt = '\033[91m{0}\033[0m'
            self.__runname_fmt = '\033[92m┌─\033[0m \033[92m{0}\033[0m: executing'
            self.__output_fmt = '\033[92m│ \033[0m{0}'
            self.__end_fmt = '\033[92m└─\033[0m {0}'
            self.__stderr_fmt = '\033[91m{0}\033[0m\n'

    class Colors(enumerate):
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

    def insert_color(self, color: Colors):
        if self.__no_colors is False:
            return ''
        return color

    def cover_string(self, left_color: Colors, string: str, right_color: Colors):
        if self.__no_colors is False:
            return string
        return f'{self.insert_color(left_color)}{string}{self.insert_color(right_color)}'

    def print_runname(self, run_name: str):
        print(self.__runname_fmt.format(run_name))

    def print_error(self, error: str):
        print(self.__error_fmt.format(error))

    def print_output(self, output: str):
        print(self.__output_fmt.format(output), file=self.__output_fd)

    def get_stderr(self, stderr: str):
        return self.__stderr_fmt.format(stderr[:-1])

    def print_end(self, end: str):
        print(self.__end_fmt.format(end))


logger = Logger()
