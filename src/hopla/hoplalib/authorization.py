"""
Library code to handle Hopla's authorization, authentication and
identification.
"""

import uuid
import logging
import os
import sys
from configparser import ConfigParser
from pathlib import Path

log = logging.getLogger()


class AuthorizationConstants:
    """Class with authorization and authentication related constants"""
    CONFIG_SECTION_CREDENTIALS = "credentials"
    CONFIG_KEY_USER_ID = "user_id"
    CONFIG_KEY_API_TOKEN = "api_token"

    GLOBAL_ENV_VAR_XDG_CONFIG_HOME = "XDG_CONFIG_HOME"
    GLOBAL_ENV_VAR_HOPLA_AUTH_FILE = "HOPLA_AUTH_FILE"


class AuthorizationHandler:
    """ TODO: violates SRP """

    def __init__(self):
        self.config_parser = ConfigParser()

    @property
    def auth_file(self) -> Path:
        """ Get the file with authorization"""
        auth_file: Path
        hopla_auth_file_env_var: str = os.environ.get(
            AuthorizationConstants.GLOBAL_ENV_VAR_HOPLA_AUTH_FILE)
        xdg_config_home_env_var: str = os.environ.get(
            AuthorizationConstants.GLOBAL_ENV_VAR_XDG_CONFIG_HOME)

        if hopla_auth_file_env_var:
            auth_file = Path(hopla_auth_file_env_var)
        elif xdg_config_home_env_var:
            auth_file = Path(xdg_config_home_env_var) / "hopla" / "auth.conf"
        else:
            auth_file = Path.home() / ".config" / "hopla" / "auth.conf"

        # TODO: check if resolve could fail if these dirs dont exist
        return auth_file.resolve()

    @property
    def auth_dir(self) -> Path:
        """The directory that the authentication file is in.

        :return:
        """
        parent = self.auth_file.parent
        # TODO: cleanup with unittest
        assert parent.exists() and parent.is_dir(), f"expected dir {parent} to exist"
        return parent

    @property
    def user_id(self):
        """Return the user id to be used in habitica API requests"""
        # violating that @property should be cheap;
        # However, the auth file should be short. So we should be fine to parse
        self._parse()
        return self.config_parser[AuthorizationConstants.CONFIG_SECTION_CREDENTIALS] \
            .get(AuthorizationConstants.CONFIG_KEY_USER_ID)

    @property
    def api_token(self):
        """Return the api token to be used in habitica API requests"""
        # violating that @property should be cheap;
        # However, the auth file should be short. So we should be fine to parse
        self._parse()
        return self.config_parser[AuthorizationConstants.CONFIG_SECTION_CREDENTIALS] \
            .get(AuthorizationConstants.CONFIG_KEY_API_TOKEN)

    def auth_file_exists(self) -> bool:
        """Return True if the authentication file exists"""
        return self.auth_file.exists and self.auth_file.is_file()

    def set_hopla_credentials(self, *,
                              user_id: uuid.UUID,
                              api_token: uuid.UUID,
                              overwrite: bool = False):
        log.debug(f"set_hopla_credentials overwrite={overwrite}")
        if self.auth_file_exists() and overwrite is False:
            log.info(f"Auth file {self.auth_file} not recreated because it already exists")
            return

        self._create_auth_dir()
        with open(self.auth_file, mode="w", encoding="utf-8") as new_auth_file:
            self.config_parser.add_section(
                AuthorizationConstants.CONFIG_SECTION_CREDENTIALS)
            self.config_parser.set(
                section=AuthorizationConstants.CONFIG_SECTION_CREDENTIALS,
                option=AuthorizationConstants.CONFIG_KEY_USER_ID,
                value=str(user_id)
            )
            self.config_parser.set(
                section=AuthorizationConstants.CONFIG_SECTION_CREDENTIALS,
                option=AuthorizationConstants.CONFIG_KEY_API_TOKEN,
                value=str(api_token)
            )
            self.config_parser.write(new_auth_file)

        assert self.auth_file_is_valid(), f"{self.auth_file} is not valid"

    def auth_file_is_valid(self) -> bool:
        if self.auth_file_exists() is False:
            log.debug(f"{self.auth_file} does not exist")
            return False

        self.config_parser.read(self.auth_file)
        if self.config_parser.has_section(
                AuthorizationConstants.CONFIG_SECTION_CREDENTIALS) is False:
            log.debug(f"{self.auth_file} has no credentials section")
            return False

        if self._auth_file_has_user_id() is False:
            log.debug(f"{self.auth_file} has no user id")
            return False

        if self._auth_file_has_api_token() is False:
            log.debug(f"{self.auth_file} has no api token")
            return False

        return True

    def _auth_file_has_api_token(self) -> bool:
        return self.config_parser.has_option(
            section=AuthorizationConstants.CONFIG_SECTION_CREDENTIALS,
            option=AuthorizationConstants.CONFIG_KEY_API_TOKEN)

    def _auth_file_has_user_id(self) -> bool:
        return self.config_parser.has_option(
            section=AuthorizationConstants.CONFIG_SECTION_CREDENTIALS,
            option=AuthorizationConstants.CONFIG_KEY_USER_ID)

    def _create_auth_dir(self):
        Path.mkdir(self.auth_dir, parents=True, exist_ok=True)

    def _parse(self):
        if self.auth_file_exists():
            self.config_parser.read(self.auth_file)
        if self._auth_file_has_api_token() is False or self._auth_file_has_user_id() is False:
            print("no credentials found")
            print("Please run:")
            print("    hopla auth")
            sys.exit(1)  # TODO: handle this better
