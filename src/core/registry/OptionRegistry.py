GlobalOptionRegistry = {}


class OptionRegistry:

    @staticmethod
    def register_options(options: dict) -> None:
        """Function to register options within the GlobalOptionRegistry"""
        """
        :param options:     Options to register
        :type options:      dict
        :return:            None
        """
        for ns in options:
            options[ns] = dict((k.lower(), v) for k, v in options[ns].items() for ns in options)
            GlobalOptionRegistry.update(options)

    @staticmethod
    def get_registry_value(key: str) -> str:
        """Function to get registry value from GlobalOptionRegistry"""
        """
        :param key:         key of the value to retrieve from the GlobalOptionsRegistry
        :type key:          str
        :return             str
        """
        for ns in GlobalOptionRegistry:
            if key in GlobalOptionRegistry[ns]:
                return GlobalOptionRegistry[ns][key][0]

    @staticmethod
    def set_registry_value(key: str, value: str) -> None:
        """Function to set registry values within GlobalOptionRegistry"""
        """
        :param key:         key of the dict you want to set/update
        :type key:          str
        :param value:       value of the key you want to set/update
        :type value:        str
        :return:            None
        """
        try:
            for ns in GlobalOptionRegistry:
                if key.lower() not in str(GlobalOptionRegistry[ns]).lower():
                    continue
                opts = GlobalOptionRegistry[ns][key.lower()][2]
                if not opts:
                    GlobalOptionRegistry[ns][key][0] = value
                else:
                    choices = opts.replace(' ', '').split(',')
                    choices.append("")
                    if value in choices:
                        GlobalOptionRegistry[ns][key.lower()][0] = value
        except KeyError:
            pass

    @staticmethod
    def get_registry_dict():
        """Function to return the GlobalOptionRegistry dict"""
        return GlobalOptionRegistry
