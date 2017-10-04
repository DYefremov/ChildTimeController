import logging
import datetime
import pwd
import os

LOG_FILE = "log.log"
DATE_FORMAT = "%d-%m-%y %H:%M:%S %w"  # 'w' is current day (0-6)

logging.Logger("main_logger")
logging.basicConfig(level=logging.INFO,
                    filename=LOG_FILE,
                    format="%(asctime)s %(message)s",
                    datefmt=DATE_FORMAT)


def get_logger():
    return logging.getLogger("main_logger")


def is_in_file(f, text):
    return any(text in line for line in f)


def open_log():
    with open(LOG_FILE) as file:
        time = datetime.datetime.now()
        day = time.isoweekday()
        date = time.date().strftime(DATE_FORMAT)
        if is_in_file(file, str(date)):
            print(date)


if __name__ == "__main__":
    logger = get_logger()
    logger.info(pwd.getpwuid(os.geteuid()).pw_name)
    open_log()
