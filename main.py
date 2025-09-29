import sys
import traceback
import json

# for prod, to have nice errors
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
#####################################