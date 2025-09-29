# for prod, to have nice errors
# import sys
# import traceback
#
# def custom_exception_handler(
#         exc_type: BaseException | None,
#         exc_value: BaseException | None,
#         exc_traceback
# ) -> None:
#     """
#     Custom exception handler, that always raises a RuntimeException as a wrapper to an (unaccounted-for) error
#     :param exc_type: Type of the error
#     :param exc_value: Exception value (message)
#     :param exc_traceback: Traceback
#     :return: None
#     """
#     print(f"An unaccounted-for error occurred: {exc_type.__name__} – {exc_value}.\n"
#           f"Contact the maintainer for help at 'molego16@gmail.com'.")
#     traceback.print_tb(exc_traceback)
#     return
#
#
# sys.excepthook = custom_exception_handler

########## config handling ##########
import json

with open("default_config.json", mode="r") as file:
    DEFAULT_CONFIG: dict[str, float] = json.load(file)

try:
    with open("CONFIG.json", mode="r") as file:
        CONFIG: dict[str, float] = json.load(file)
except Exception as err:
    raise ImportError(f"An error occurred while reading config: {type(err).__name__} – {err}.\n"
                      f"Visit https://github.com/Michael-Kornilich/detergent_tracker to see the manual "
                      f"on how to handle the config and / or restore its default contents.")

# checking against the default config accounts for possible future changes in the config
if (got_len := len(CONFIG.keys())) != (exp_len := len(DEFAULT_CONFIG.keys())):
    rel = "more" if got_len > exp_len else "less"
    raise ValueError(f"An error occurred while parsing config file. "
                     f"There are {rel} keys (got {got_len}) than expected ({exp_len})")

if (got_keys := sorted(CONFIG.keys())) != (exp_keys := sorted(DEFAULT_CONFIG.keys())):
    raise ValueError(f"An error occurred while parsing config file. "
                     f"The expected keys ({", ".join(exp_keys)}) don’t match the actual ones: {", ".join(got_keys)}")

for key, value in CONFIG.items():
    if type(value) not in (int, float):
        raise TypeError(f"The {key} must be a real number, got '{type(value).__name__}'.")
    if value <= 0:
        raise ValueError(f"The {key} must be bigger than 0, got {value}")

# print(CONFIG.items())
#####################################

########## DB handling ##########
import sqlite3
from sqlite3 import Connection, Cursor
from os import path

if not path.exists("./database"):
    raise FileNotFoundError("The database directory does not exist. "
                            "Make sure you create a 'database/' directory or "
                            "mount a named volume 'database' when launching the container.")

if path.exists("./database/database.db"):
    err_type = ImportError
    err_msg = "Failed to load the database: {name} – {msg}"
else:
    print("Database does not exist. Creating a new one.")
    err_type = RuntimeError
    err_msg = "An unexpected error occurred while trying to create the database: {name} – {msg}"

try:
    conn: Connection = sqlite3.connect("./database/database.db")
    cur: Cursor = conn.cursor()

    # prevent PyCharm from complaining
    # noinspection SqlNoDataSourceInspection
    cur.execute("""
    CREATE TABLE IF NOT EXISTS usage_data (
    	date INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    	n_cups REAL NOT NULL,
    	volume_used REAL NOT NULL,

    	PRIMARY KEY (date ASC) ON CONFLICT FAIL,
    	CONSTRAINT valid_cups CHECK (n_cups >= 0),
    	CONSTRAINT valid_valid_used CHECK (volume_used >= 0)
    );
    """)
except Exception as err:
    raise err_type(err_msg.format(name=type(err).__name__, msg=err))
#################################

########## command line arguments parsing ##########
from argparse import ArgumentParser, RawTextHelpFormatter

parser: ArgumentParser = ArgumentParser(
    prog="Detergent Tracker",
    description="""
This app has been created to track usage of detergent.

Before using the app, I strongly advice to fill the config file and attach it, otherwise the app will work in an unexpected way or not run at all. The following config options are available:
    - Bottle_volume: float > 0 (decimal “.” Separated, not integer separator)
    - Cup_volume: float > 0 (decimal “.” Separated, not integer separator)""",
    epilog="Advise README.md to learn the run procedure.",
    formatter_class=RawTextHelpFormatter
)

parser.add_argument(
    "-l", "--log",
    action="store",
    nargs=1,
    type=float,
    dest="n_cups",
    help="input the number of cups used in the last wash."
)

parser.add_argument(
    "-s", "--status",
    action="store_true",
    help="show a status report of the current detergent."
)

parser.add_argument(
    "--reset",
    action="store_true",
    help="reset all data to defaults."
)

args = vars(parser.parse_args())
print(args)
