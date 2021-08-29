"""
The module with CLI code that handles the `hopla get` group command.
"""
import copy
import logging
from dataclasses import dataclass
from typing import List

import click
import requests

from hopla.hoplalib.clickhelper import data_on_success_else_exit
from hopla.hoplalib.http import RequestHeaders, UrlBuilder
from hopla.hoplalib.outputformatter import JsonFormatter

log = logging.getLogger()


@click.group()
def get():
    """GROUP for getting information from habitica"""


# TODO: add jq back again https://pypi.org/project/jq/
#       or https://pypi.org/project/pyjq/


valid_item_groups = click.Choice([
    "pets", "mounts", "eggs", "food", "hatchingPotions",
    "gear", "quests", "currentPet", "currentMount",
    "lastDrop", "all"
])


def inventory_alias_to_official_habitica_name(inventory_name: str):
    # pylint: disable=too-many-return-statements
    if inventory_name in ["hatchingpotions", "hatchingPotion"]:
        return "hatchingPotions"
    if inventory_name in ["pet"]:
        return "pets"
    if inventory_name in ["mount"]:
        return "mounts"
    if inventory_name in ["currentpet"]:
        return "currentPet"
    if inventory_name in ["currentmount"]:
        return "currentMount"
    if inventory_name in ["lastdrop"]:
        return "lastDrop"

    return inventory_name


@get.command(context_settings=dict(token_normalize_func=inventory_alias_to_official_habitica_name))
@click.argument("item_group_name", type=valid_item_groups, default="all")
def user_inventory(item_group_name) -> dict:
    """Get items from the user's inventory

    If no specific item group is specified,

    \f
    :param item_group_name: The type of items in the inventory (default: all)
    :return: The specified inventory
    """
    log.debug(f"hopla get user-inventory item_group={item_group_name}")
    response = HabiticaUserRequest().request_user()
    response_data: dict = data_on_success_else_exit(response)
    habitica_user = HabiticaUser(user_dict=response_data)
    data_items = habitica_user.get_inventory()

    if item_group_name == "all":
        data_requested_by_user = data_items
    else:
        data_requested_by_user = data_items[item_group_name]
    click.echo(
        JsonFormatter(data_requested_by_user).format_with_double_quotes())
    return data_requested_by_user


valid_stat_names = click.Choice(["hp", "mp", "exp", "gp", "lvl", "class",
                                 "maxMP", "all"])


def stat_alias_to_official_habitica_name(stat_name: str) -> str:
    # pylint: disable=too-many-return-statements
    if stat_name in ["mana", "mana-points", "manapoints"]:
        return "mp"
    if stat_name in ["maxMp", "maxmp"]:
        return "maxMP"
    if stat_name in ["health", "healthpoints"]:
        return "hp"
    if stat_name in ["xp", "experience"]:
        return "exp"
    if stat_name in ["gold"]:
        return "gp"
    if stat_name in ["level"]:
        return "lvl"

    return stat_name


@get.command(context_settings=dict(token_normalize_func=stat_alias_to_official_habitica_name))
@click.argument("stat_name", type=valid_stat_names, default="all")
def user_stats(stat_name: str):
    """Get the stats of a user"""
    log.debug(f"hopla get user-stats stat={stat_name}")
    response = HabiticaUserRequest().request_user()
    response_data: dict = data_on_success_else_exit(response)
    habitica_user = HabiticaUser(user_dict=response_data)

    data_stats = habitica_user.get_stats()
    if stat_name == "all":
        data_requested_by_user = data_stats
    else:
        data_requested_by_user = data_stats[stat_name]
    click.echo(
        JsonFormatter(data_requested_by_user).format_with_double_quotes())
    return data_requested_by_user


valid_auth_info_names = click.Choice(["username", "email", "profilename", "all"])


def auth_alias_to_official_habitica_name(auth_info_name: str):
    if auth_info_name in ["e-mail", "mail"]:
        return "email"
    return auth_info_name


# username -> 'data.auth.local.username':
# * Your username is used for invitations, @mentions in chat, and messaging.
#   * It:
#     + must be 1 to 20 characters,
#     + must contain only letters a to z, numbers 0 to 9, hyphens, or underscores, and
#     + cannot include any inappropriate terms.
# * is changeable at '<https://habitica.com/user/settings/site>' 'Change Display Name'

# profilename -> 'data.profile.name'
# *  is changeable at '<https://habitica.com/user/settings/site>' under 'Change Display Name'
# profilename is not really in the .data.auth section of /user.. but fits well here
# TODO: probably better to remove profilename here regardless


@get.command(context_settings=dict(token_normalize_func=auth_alias_to_official_habitica_name))
@click.argument("auth_info_name", type=valid_auth_info_names, default="all")
def user_auth(auth_info_name: str):
    """Get user authentication and identification info

    NOTE: `hopla get user-auth` currently only supports email-based
    logins (not 3rd party logins such as google SSO). As a workaround, you
    can use `hopla get user-info --filter|-f FILTER_STRING`. For example, to
    get google SSO credentials you can use:

    \b
    Examples
    ---
    # get email
    hopla get user-auth email

    \b
    # workaround for SSO information
    hopla get user-info -f "auth.google"

    """
    log.debug(f"hopla get user-auth auth={auth_info_name}")
    response = HabiticaUserRequest().request_user()
    response_data: dict = data_on_success_else_exit(response)
    user = HabiticaUser(user_dict=response_data)

    json_data_auth: dict = user.get_auth()

    if auth_info_name == "all":
        click.echo(JsonFormatter(json_data_auth).format_with_double_quotes())
        return json_data_auth

    if auth_info_name == "profilename":
        profile_name = response_data["profile"]["name"]
        click.echo(JsonFormatter(profile_name).format_with_double_quotes())
        return profile_name

    # TODO no support for non-local data yet (e.g. google SSO)
    #      e.g. use hopla get user-info -f "auth.google" as workaround
    auth_info = json_data_auth["local"][auth_info_name]
    click.echo(JsonFormatter(auth_info).format_with_double_quotes())
    return auth_info


valid_info_names = click.Choice(["gems", "id", "notifications", "tags", "lastCron",
                                 "loginIncentives", "all"])


def info_alias_to_official_habitica_name(user_info_name: str) -> str:
    """Return the canonical habitica name"""
    if user_info_name in ["userid", "user-id"]:
        return "id"
    if user_info_name in ["gems", "gem"]:
        return "balance"
    return user_info_name


@get.command(context_settings=dict(token_normalize_func=info_alias_to_official_habitica_name))
# TODO: consider upgrading to full-blown jq and dont handle this yourself
@click.argument("user_info_name", type=valid_info_names, default="all")
@click.option("--filter", "-f", "filter_string", metavar="FILTER_STRING",
              help="a comma seperated list of keys")
def user_info(user_info_name: str,
              filter_string: str) -> dict:
    """Return user information

    If no FILTER_STRING is given, get all user info.
    Otherwise, return the result of filtering the user's info with the
    specified FILTER_STRING.

    USER_INFO_NAME the particular type of information that you want to return, by
    default "all".


    \b
    [BNF](https://en.wikipedia.org/wiki/Backus-Naur-Form)
    for the FILTER_STRING:

    \b
        filter_keys ::= [filter_keys]?[,filter_keys]*
        filter_keys ::= filter_keys[.filter_keys]*

    \b
    Examples:
    ---
    # get all user info
    hopla get user-info

    \b
    # get number of gems
    hopla get user-info gems

    \b
    # get user id
    hopla get user-info id

    \b
    # get number of times logged in
    hopla get user-info loginIncentives

    \b
    # get all items of a user:
    hopla get user-info ---filter "items"

    \b
    # get all mounts
    hopla get user-info ---filter "items.mounts"

    \b
    # get all mounts+pets
    hopla get user-info ---filter "items.mounts,items.pets"

    \b
    # get streaks+completed quests
    hopla get user-info -f "achievements.streak,achievements.quests"

    \b
    # get contributor status, cron-count, profile description, and user id
    hopla get user-info -f "contributor, flags.cronCount, profile.blurb, id"

    \b
    # get last free rebirth, day start (in hours), timezone offset (in minutes), and
    # account creation time
    hopla get user-info -f 'flags.lastFreeRebirth, preferences.dayStart, preferences.timezoneOffset, auth.timestamps.created'   # pylint: disable=line-too-long

    \f
    [APIdocs](https://habitica.com/apidoc/#api-User-UserGet)

    :param user_info_name:
    :param filter_string: string to filter the user dict on (e.g. "achievements.streak,purchased.plan")
    :return
    """
    log.debug(f"hopla get user-info user_info_name={user_info_name} filter={filter_string}")
    response = HabiticaUserRequest().request_user()
    response_data: dict = data_on_success_else_exit(response)
    habitica_user = HabiticaUser(user_dict=response_data)

    if filter_string:
        user: dict = habitica_user.filter_user(filter_string)
    elif user_info_name == "all":
        user: dict = habitica_user.user_dict
        # TODO: refactor
    elif user_info_name == "gems":
        gems = habitica_user.get_gems()
        user: dict = {"gems": gems}
    else:
        user: dict = habitica_user.filter_user(user_info_name)

    user_str = JsonFormatter(user).format_with_double_quotes()
    click.echo(user_str)
    # return user


def turn_balance_into_gems(habitica_user):
    user: dict = habitica_user.filter_user("balance")
    return user


class HabiticaUserRequest:
    def __init__(self):
        self.url = UrlBuilder(path_extension="/user").url
        self.headers = RequestHeaders().get_default_request_headers()

    def request_user(self) -> requests.Response:
        return requests.get(url=self.url, headers=self.headers)


@dataclass(frozen=True)
class HabiticaUser:
    """
    Class representing a user model.

    The user_dict is assumed to be returned from a 200 ok Response as (using
    Response.json()) when calling the /user endpoint and getting .data
    """
    user_dict: dict

    def get_stats(self) -> dict:
        return self.user_dict["stats"]

    def get_inventory(self) -> dict:
        return self.user_dict["items"]

    def get_auth(self) -> dict:
        return self.user_dict["auth"]

    def get_gems(self):
        """Get the number of gems of a user.

        gems are stored in the 'balance' field. 1 'balance' equals 4 gems
        [see](https://habitica.fandom.com/wiki/Gems#Information_for_Developers)
        """
        balance = self.user_dict["balance"]
        return balance * 4

    def filter_user(self, filter_string: str) -> dict:
        # TODO: this code is generic, it can be used to filter any dict
        #       move it out of this class and reuse
        result = {}
        filters: List[str] = filter_string.strip().split(",")

        for filter_keys in filters:
            filter_keys: str = filter_keys.strip()
            if len(filter_keys) != 0:
                result.update(self._filter_user(user_dict=self.user_dict,
                                                filter_keys=filter_keys))

        return result

    def _filter_user(self, *, user_dict: dict, filter_keys: str) -> dict:
        """ Gets a starting dict D and uses filter_keys of form "hi.ya.there" to get
            {filter_keys: D["hi"]["ya"]["there"]} or {filter_string: {}} if D["hi"]["ya"]["there"]
            does not exist.

        TODO: include doctests in the build process
        [see(](https://docs.python.org/3/library/doctest.html)
        >>> HabiticaUser({})._filter_user(
        ...     user_dict={"items": {"currentPet":"Wolf-Base", "currentMount":"Aether-Invisible"}},
        ...     filter_keys = "items.currentMount")
        {'items.currentMount': 'Aether-Invisible'}

        :param user_dict:
        :param filter_keys:
        :return: we return {filter_string: D["hi"]["ya"]["there"]} or
                 {filter_string: {}} if there is no such item
        """
        start_dict = copy.deepcopy(user_dict)
        dict_keys: List[str] = filter_keys.split(".")
        for dict_key in dict_keys:
            if start_dict is not None:
                start_dict = start_dict.get(dict_key)
            else:
                log.debug(f"Didn't match anything with the given filter={filter_keys}")
                return {filter_keys: {}}
        return {filter_keys: start_dict}


if __name__ == "__main__":
    import doctest

    doctest.testmod()