import os
import sys
import shutil
import time
import builtins
from rich.progress import Progress
from rich.table import Table
from rich import print as print_func


builtins.print = print_func


settings = {
    'fn': None,
    'step': 4096,
    'compress': False
}


def file_exists(file_path: str) -> bool:
    return os.access(file_path, os.F_OK)


def is_full_path(file_path: str) -> bool:
    return not file_exists(os.path.join(os.getcwd(), file_path))


def print_help() -> None:
    table = Table(show_header=True, header_style='bold')
    table.add_column('Argument')
    table.add_column('Full Argument')
    table.add_column('Short Description')
    table.add_row('-h', '--help', 'Show Help Information')
    table.add_row('-f', '--filename', 'Set Filename To Split')
    table.add_row('-s', '--step', 'Set Chunked File Size')
    table.add_row('-c', '--compress', 'Enable Compressing')
    print(table)


def parse_args() -> None:
    for i, cur_ in enumerate(sys.argv[1:]):
        cur = cur_.lower().strip()
        is_last = i + 2 >= len(sys.argv)
        if cur == '-h' or cur == '--help':
            print_help()
            sys.exit(0)
        if (cur == '-f' or cur == '--filename') and not is_last:
            settings['fn'] = sys.argv[i + 2]
        if (cur == '-s' or cur == '--step') and not is_last:
            try:
                settings['step'] = int(sys.argv[i + 2].strip())
            except Exception as err_:
                print(f'[red]Error - Can\'t Set Step: {err_}!')
                sys.exit(1)
        if cur == '-c' or cur == '--compress':
            settings['compress'] = True


def check_args() -> None:
    if not settings['fn']:
        print(f'[red]Error - No File: Type [cyan]"{sys.executable}" "{__file__}" --help[red] For More Information!')
        sys.exit(1)
    if not file_exists(settings['fn']):
        print(f'[red]Error - File "{settings["fn"]}" Is Not Exists!')
        sys.exit(1)
    if not is_full_path(settings['fn']):
        settings['fn'] = os.path.join(os.getcwd(), settings['fn'])


def make_dir() -> None:
    base_fn = os.path.basename(settings['fn'])
    dir_fn = os.path.dirname(settings['fn'])
    ext_fn = base_fn.lower().strip().split('.')[-1]
    no_ext_fn = '.'.join(base_fn.split('.')[:-1])
    out_dir = os.path.join(dir_fn, no_ext_fn + '_out')
    if os.path.isdir(out_dir):
        while True:
            print(f'[yellow]Folder "{out_dir}" Is Already Exists. Continue? [Y/n]: ', end='')
            input_ = input('').lower().strip()
            if input_ == 'n':
                sys.exit(0)
            if input_ == 'y':
                shutil.rmtree(out_dir)
                break
    os.mkdir(out_dir)
    
    skipped_times = 0
    
    launch_time = time.time()
    file = open(settings['fn'], 'rb')
    length = file.seek(0, 2)
    file.seek(0)
    with Progress() as bar:
        task = bar.add_task("[red]Splitting...", total=length)
        i = 0
        while True:
            current_bytes = file.read(settings['step'])
            can_write = True
            if settings['compress']:
                if not current_bytes.replace(b'\x00', b''):
                    can_write = False
                    skipped_times += 1
            if can_write:
                f_ = open(os.path.join(out_dir, f'{no_ext_fn}-{i}.{ext_fn}'), 'wb')
                f_.write(current_bytes)
                f_.close()
            i += settings['step']
            bar.update(task, completed=i)
            if i > length:
                bar.update(task, completed=length)
                break
    file.close()
    end_time = time.time()
    print(f'[cyan]Splitting Finished In [green]{end_time - launch_time}[cyan]s.')
    
    if settings['compress']:
        print(f'[cyan]Compressor Skipped {skipped_times} Times.')


def split() -> None:
    pass


def main() -> None:
    parse_args()
    check_args()
    make_dir()
    split()


if __name__ == '__main__':
    main()
