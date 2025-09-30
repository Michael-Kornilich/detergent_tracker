# DB related
import sqlite3
from sqlite3 import Connection, Cursor


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

def load_config(
        fp_config: str = "CONFIG.json",
        fp_default_config: str = "default_config.json"
) -> dict[str, float]:
    """
    Loads user's config file and validates it against the default config.\n
    Assumptions:\n
    - Default params assume both files reside in the same directory as the script (main.py)
    - Default config file is flawless and does not require verification
    - You can check user's config against the default one
    - built-in json library is available

    :param fp_config: filepath (string) to user's config file
    :param fp_default_config: filepath (string) to the default config file
    :return: config as dictionary
    :raises ImportError: If an error occurs while reading user's config.
    :raises ValueError, TypeError: If an error occurs while validating config's keys and values.
    """
    import json

    with open(fp_default_config, mode="r") as file:
        default_config: dict[str, float] = json.load(file)

    try:
        with open(fp_config, mode="r") as file:
            CONFIG: dict[str, float] = json.load(file)
    except Exception as err:
        raise ImportError(f"An error occurred while reading config: {type(err).__name__} – {err}.\n"
                          f"Visit https://github.com/Michael-Kornilich/detergent_tracker to see the manual "
                          f"on how to handle the config and / or restore its default contents.")

    # checking against the default config accounts for possible future changes in the config
    if (got_len := len(CONFIG.keys())) != (exp_len := len(default_config.keys())):
        rel = "more" if got_len > exp_len else "less"
        raise ValueError(f"An error occurred while parsing config file. "
                         f"There are {rel} keys (got {got_len}) than expected ({exp_len})")

    if (got_keys := sorted(CONFIG.keys())) != (exp_keys := sorted(default_config.keys())):
        raise ValueError(f"An error occurred while parsing config file. "
                         f"The expected keys ({", ".join(exp_keys)}) don’t match the actual ones: {", ".join(got_keys)}")

    for key, value in CONFIG.items():
        if type(value) not in (int, float):
            raise TypeError(f"The {key} must be a real number, got '{type(value).__name__}'.")
        if value <= 0:
            raise ValueError(f"The {key} must be bigger than 0, got {value}")

    return CONFIG


def init_database(_db_path: str = "./database/database.db") -> None:
    """
    Validate and / or initialize a database at db_fp + db_name if it doesn't exist.\n
    Assumes that pathlib library is available

    :param _db_path: Filepath to the database
    :return: None
    :raises FileNotFound: if the specified DB directory does not exist
    :raises RuntimeError, ImportError: if the database file could not be loaded
    """
    from pathlib import Path
    db_path = Path(_db_path)

    if not db_path.parent.exists():
        raise FileNotFoundError(f"The database directory does not exist. "
                                f"Make sure you create a '{db_path.parent}' directory or "
                                f"mount a named volume '{db_path.parent}' when launching the container.")

    # Since .connect(db_path) has either connect-behavior or load behavior,
    # we do case distinction for errors depending on whether the DB exists or not
    if db_path.exists():
        err_type = ImportError
        err_msg = "Failed to connect the database: {name} – {msg}"
    else:
        err_type = RuntimeError
        err_msg = "An unexpected error occurred while trying to create the database: {name} – {msg}"
        print("Database not found. Creating a new one.")

    try:
        conn: Connection = sqlite3.connect(db_path)
        cur: Cursor = conn.cursor()

        # prevent PyCharm from complaining
        # noinspection SqlNoDataSourceInspection
        cur.execute("""
        CREATE TABLE IF NOT EXISTS usage_data (
            date INTEGER NOT NULL DEFAULT (CAST(strftime('%s', 'now') as INT)),
            n_cups REAL NOT NULL,
            volume_used REAL NOT NULL,
    
            UNIQUE (date),
            CONSTRAINT valid_cups CHECK (n_cups >= 0),
            CONSTRAINT valid_valid_used CHECK (volume_used >= 0)
        );
        """)
        cur.close()
        conn.close()
    except Exception as err:
        raise err_type(err_msg.format(name=type(err).__name__, msg=err))

    return


########## command line arguments parsing ##########
from argparse import ArgumentParser, RawTextHelpFormatter

parser: ArgumentParser = ArgumentParser(
    prog="Detergent Tracker",
    description="""
This app has been created to track usage of detergent.

Before using the app, I strongly advice to fill the config file and attach it, otherwise the app will work in an unexpected way or not run at all. The following config options are available:
    - Bottle_volume: float > 0 (decimal “.” Separated, not integer separator)
    - Cup_volume: float > 0 (decimal “.” Separated, not integer separator)""",
    epilog="""
You can only use ONE flag per call. The only exception is '--log <n-cups> --status'.
Advise README.md to learn the run procedure.""",
    formatter_class=RawTextHelpFormatter
)

parser.add_argument(
    "-l", "--log",
    action="store",
    type=float,
    dest="n_cups",
    metavar="<n-cups>",
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

kwargs: dict[str, float | bool] = vars(parser.parse_args())

if (n_specified := sum(map(bool, kwargs.values()))) > 2:
    raise ValueError(f"You can add at most 2 flags. {n_specified} were added instead.")
if kwargs["reset"] and (kwargs["status"] or kwargs["n_cups"]):
    raise ValueError("Reset flag must not have any flags along with it.")

######## logging logic ########
if (n_cups := kwargs["n_cups"]) is not None:
    CONFIG: dict[str, float] = load_config()
    last_wash_volume: float = n_cups * CONFIG["cup_volume"]

    if n_cups < 0:
        raise ValueError(f"Number of cups must be non-negative, got {n_cups}")
    if last_wash_volume > CONFIG["bottle_volume"]:
        raise ValueError(
            f"The volume most recently used ({n_cups} cups * {CONFIG["cup_volume"]} liters = {last_wash_volume} liters)"
            f" exceeds the total volume of the detergent {CONFIG["bottle_volume"]} liters."
            f" You may need to adjust cup and / or bottle volumes in your config and relaunch the app.")

    db_path: str = "./database/database.db"
    init_database(db_path)

    # isolation_level = None == auto-commits
    with sqlite3.connect(db_path, isolation_level=None) as conn:
        conn: Connection

        # noinspection SqlNoDataSourceInspection
        volume_used: float = float(conn.execute("SELECT SUM(volume_used) FROM usage_data").fetchall()[0][0] or 0.0)
        if CONFIG["bottle_volume"] - volume_used < last_wash_volume:
            raise ValueError(f"The most recent volume of detergent used ({last_wash_volume}) "
                             f"exceeds the (expected) volume left ({CONFIG["bottle_volume"] - volume_used})")

        try:
            # noinspection SqlNoDataSourceInspection
            conn.execute(
                "INSERT INTO usage_data (n_cups, volume_used) VALUES (?, ?)",
                (n_cups, last_wash_volume))
        except Exception as err:
            raise SystemError(f"Unable to insert data: {type(err).__name__} - {err}. Try again later.")

    print("Recorded successfully!")
###############################

if kwargs["status"]:
    print("Here is your status report!")

if kwargs["reset"] and input("Do you really want to delete all your data [n/Y]: ") == "Y":
    print("Deleting data")
