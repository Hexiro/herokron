import sys
from argparse import ArgumentParser

import dhooks
import heroku3

from .exceptions import AppError, DatabaseError
from .utils import Formatting
from .utils.database import database


class Herokron:

    def __init__(self, app):
        """
        :param app: The name of the Heroku app in which you want to update
        :type app: str
        """

        # if it doesn't exist refresh database
        if app not in database.apps:
            database.sync_database()
        if app in database.apps:
            self.heroku = heroku3.from_key(database.key_from_app(app))
            self.app = self.heroku.app(app)
        # after a refresh if self.heroku still isn't defined
        else:
            raise AppError("App couldn't be found in the local database.")

        # might add `proc_type` param in future
        formation = self.app.process_formation()
        if not formation:
            raise AppError("App has no process types. (can't be turned on/off)")
        elif "worker" in formation:
            self.dynos = self.app.process_formation()["worker"]
        elif "web" in formation:
            self.dynos = self.app.process_formation()["web"]
        else:
            self.dynos = formation[0]

    @property
    def online(self):
        return self.dynos.quantity == 1

    @property
    def offline(self):
        return not self.online

    def status(self):
        """
        :return: dictionary containing information about the app's status
        """
        return {"online": self.online}

    def on(self):
        """
        Switches the app online, if it isn't already.
        :return: dictionary containing information about the app
        """
        if self.online:
            return {"online": True, "updated": False}

        self.dynos.scale(1)
        return {"online": True, "updated": True}

    def off(self):
        """
        Switches the app offline, if it isn't already.
        :return: dictionary containing information about the app
        """
        if self.offline:
            return {"online": False, "updated": False}

        self.dynos.scale(0)
        return {"online": False, "updated": True}


# shorthand functions

def on(app):
    """
    Switches the app online, if it isn't already.
    :param app: The name of the Heroku app in which you want to change
    :type app: str
    :return: dictionary containing information about the app
    """
    return Herokron(app).on()


def off(app):
    """
    Switches the app offline, if it isn't already.
    :param app: The name of the Heroku app in which you want to change
    :type app: str
    :return: dictionary containing information about the app
    """
    return Herokron(app).off()


def status(app):
    """
    :param app: The name of the Heroku app in which you want to change
    :type app: str
    :return: dictionary containing information about the app's status
    """
    return Herokron(app).status()


def main():
    """
    main function:
    used from command line herokron:main (console script)
    """
    parser = ArgumentParser()
    # we make the default False, so that if you don't give it an arg it will be `None` instead of `False`
    # if you know a better way of doing this lmk!
    parser.add_argument("-on",
                        help="Calls the `on` function to turn an app on.")
    parser.add_argument("-off",
                        help="Calls the `off` function to turn an app off.")
    parser.add_argument("-status",
                        help="Calls the `status` function view the current status of an app.")
    parser.add_argument("--database",
                        help="Prints the formatted database.",
                        nargs="?",
                        default=False)
    parser.add_argument("--add-key",
                        help="Adds the Heroku API key specified.",
                        default=False)
    parser.add_argument("--remove-key",
                        help="Removes the Heroku API key specified.",
                        default=False)
    parser.add_argument("--set-webhook",
                        help="Sets the Discord Webhook URL for logging.",
                        default=False)
    parser.add_argument("--set-color",
                        help="Sets the Discord Embed Color.",
                        default=False)
    parser.add_argument("--no-log",
                        nargs="?",
                        help="Stops this iteration from logging.",
                        default=False)
    parser.add_argument("--no-print",
                        help="Stops this iteration from printing.",
                        nargs="?",
                        default=False)

    if len(sys.argv) == 1:
        parser.print_help()
        return

    options = parser.parse_args()

    # handle database updates

    _add_key = options.add_key
    _remove_key = options.remove_key
    _webhook = options.set_webhook
    _color = options.set_color
    _no_log = options.no_log
    _no_print = options.no_print
    _database = options.database

    # duplication checking is done inside `add_key` and `remove_key`.
    if _add_key:
        database.add_key(_add_key)
    if _remove_key:
        database.remove_key(_remove_key)
    if _webhook:
        database.set_webhook(_webhook)
    if _color:
        database.set_color(_color)
    # if anything that would warrant a database update exists, and printing is allowed
    if (any({_add_key, _remove_key, _webhook, _color}) or _database is not False) and _no_print is False:
        # ehhh i don't like the database.database syntax
        # I'll have to work on that sometime.
        print(Formatting().format(database.database))

    # handle status changes

    app = options.on or options.off or options.status

    turn_on = bool(options.on)
    turn_off = bool(options.off)
    check_status = bool(options.status)

    if turn_on:
        result = on(app)
    elif turn_off:
        result = off(app)
    elif check_status:
        result = status(app)
    else:
        # if a `status change` is not called there is nothing else to do past this point,
        # so we just return w/o consequences.
        return

    if _no_print is False:
        print(Formatting().format(result))

    if check_status:
        return

    if _no_log is False and database.webhook:
        try:
            online = result["online"]
            updated = result["updated"]
            current = "🟢" if result["online"] else "🔴"
            if not updated:
                previous = current
            else:
                previous = "🔴" if online else "🟢"
            log_embed = dhooks.Embed(
                title=app,
                color=database.color,
                # `hair spaces` (small space unicode) in description to split the emojis apart in a nice manner.
                description=f"**STATUS:⠀{previous}      →      {current}**\n"
                            "\n"
                            "View affected app:\n"
                            f"[heroku.com](https://dashboard.heroku.com/apps/{app})"

            )
            log_embed.set_timestamp(now=True)
            database.webhook.send(embed=log_embed)
        except ValueError:
            raise DatabaseError("Discord logging attempted with invalid webhook set in local database. "
                                "If your webhook is valid, please open an issue at: "
                                "https://github.com/Hexiro/Herokron.")
