from dotenv import dotenv_values
from argparse import ArgumentParser
from sys import platform
from pathlib import Path


def get_datadir() -> Path:

    """
    Returns a parent directory path
    where persistent application data can be stored.

    # linux: ~/.local/share
    # macOS: ~/Library/Application Support
    # windows: C:/Users/<USER>/AppData/Roaming
    """

    home = Path.home()

    if platform == "win32":
        return home / "AppData/Roaming/Herokron"
    elif platform == "linux":
        return home / ".local/share/Herokron"
    elif platform == "darwin":
        return home / "Library/Application Support/Herokron"


def get_datafile() -> Path:
    return get_datadir() / ".env"


try:
    get_datadir().mkdir(parents=True)
except FileExistsError:
    pass
try:
    open(get_datafile(), "x").close()
except FileExistsError:
    pass


def main():
    parser = ArgumentParser()
    parser.add_argument("--add-key",
                        help="Adds the Heroku API key specified.",
                        default=False)
    parser.add_argument("--remove-key", 
                        help="Removes the Heroku API key specified.",
                        default=False)
    parser.add_argument("--set-webhook",
                        help="Sets the Discord Webhook URL for logging (OPTIONAL)",
                        default=False)
    parser.add_argument("--set-color",
                        help="Sets the Discord Embed Color for logging (OPTIONAL)",
                        default=False)
    parser.add_argument("--values", 
                        help="Prints stored values.",
                        nargs="?",
                        default=False) 
    options = parser.parse_args()
    env_keys = dotenv_values(get_datafile())
    values = [[key, env_keys[key]] for key in env_keys]
    keys = [sublist[0] for sublist in values]
    _add_key = options.add_key
    _remove_key = options.remove_key
    _webhook = options.set_webhook 
    _color = options.set_color
    _values = options.values
    print(_values)
    if bool(_add_key):
        values.append([f"HEROKU_KEY_{_add_key[:5]}".upper(), _add_key])
    if bool(_remove_key):
        if f"HEROKU_KEY_{_remove_key[:5]}".upper() in keys:
            del values[keys.index(f"HEROKU_KEY_{_remove_key[:5]}".upper())]
    if bool(_webhook):
        if "WEBHOOK" in keys:
            values[keys.index("WEBHOOK")][1] = _webhook
        else:
            values.append(["WEBHOOK", _webhook])
    if bool(_color):
        if "COLOR" in keys:
            values[keys.index("COLOR")][1] = _color
        else:
            values.append(["COLOR", _color])
    with open(get_datafile(), "w") as file:
        for key, value in values:
            file.write(f"{key}={value}\n")
    if _values is None:
        for key, value in values:
            print({key: value})

if __name__ == "__main__":
    main()
