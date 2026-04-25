from ..config import load_config
from ..exceptions import ConfigurationNotFound
from clikit.api.args.exceptions import NoSuchOptionException
from .CanOverrideConfig import CanOverrideConfig
from .CanOverrideOptionsDefault import CanOverrideOptionsDefault


class Command(CanOverrideOptionsDefault, CanOverrideConfig):
    def _get_config(self):
        if not hasattr(self, "_orm_config"):
            try:
                self._orm_config = load_config(self._get_option_value("config"))
            except ConfigurationNotFound:
                self._orm_config = None

        return self._orm_config

    def _get_option_value(self, option_name):
        try:
            return self.option(option_name)
        except NoSuchOptionException:
            option = self.config.options.get(option_name)
            if option:
                return option.default

            return None

    def option_or_config(self, option_name, default, *config_names):
        value = self._get_option_value(option_name)

        if value != default:
            return value

        config = self._get_config()
        if not config:
            return default

        names = config_names or (option_name.replace("-", "_"),)
        for name in names:
            for config_name in (name, name.upper()):
                if hasattr(config, config_name):
                    return getattr(config, config_name)

        return default
