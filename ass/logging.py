def log_message(msg: str):
    print(msg)


def log_warning(msg: str):
    print(f"\033[33m{msg}\033[0m")


def log_error(msg: str):
    print(f"\033[31m{msg}\033[0m")
