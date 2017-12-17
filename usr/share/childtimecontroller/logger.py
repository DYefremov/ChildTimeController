import logging
from subprocess import getoutput

LOG_FILE = "/home/dimon/log.log"
DATE_FORMAT = "%d-%m-%y %H:%M:%S %w"  # 'w' is current day (0-6)

logging.Logger("main_logger")
logging.basicConfig(level=logging.INFO,
                    filename=LOG_FILE,
                    # format="%(asctime)s %(message)s",
                    format="%(message)s",
                    datefmt=DATE_FORMAT)


def get_logger():
    return logging.getLogger("main_logger")


def is_in_file(f, text):
    return any(text in line for line in f)


def is_user_in_list(*args):
    """"
       Checking the need for logging for this user(s).

        Need implementation.!!!
       """
    return True


def open_log():
    with open(LOG_FILE) as file:
        lines = file.readlines()
        for line in lines:
            print(line)


def log_login():
    """
    Used to redirect logs from 'last'.

    It is necessary because wtmp can be in tmpfs (as at me).
    """
    logger = get_logger()
    with open(LOG_FILE) as file:
        lines = set(file.readlines())
    # logger.info(pwd.getpwuid(os.geteuid()).pw_name)
    out = getoutput("last -R").splitlines()
    sep = str("(")
    end = "\n"
    for line in out:
        if line + end not in lines and sep in line:
            logger.info(line)


if __name__ == "__main__":
    log_login()
