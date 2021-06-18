class FormattingUtility:

    @staticmethod
    def __get_start(depth):
        """
        get indentation level needed based on recursion depth
        :return: string w/ indentation level applied
        """
        # we uses tabs (\t) because it keeps everything nicely inline
        return ("\t" * depth) + "[*] "

    def format(self, data):
        """
        :param data: input data
        :return: pretty formatted dictionary w/ recursion
        """
        formatted_string = ""
        # upon first addition we don't want an increased depth (extra indentation level)
        # so we keep depth 0 when passing into these methods.
        if isinstance(data, dict) and len(data) > 0:
            formatted_string += self.__format_dict(data, depth=0)
        if isinstance(data, list) and len(data) > 0:
            formatted_string += self.__format_list(data, depth=0)
        return formatted_string

    def __format_dict(self, data, depth=0):
        """
        this is a private method so it can only be invoked from inside the class
        assumes data is in type dict
        :param data: input dictionary
        :type data: dict
        :param depth: recursion depth; not to be set manually
        :type depth: int
        :return: pretty formatted dictionary w/ recursion
        """
        formatted_string = ""
        if len(data) == 0:
            return formatted_string
        start = self.__get_start(depth)
        last_key = list(data.keys())[-1]

        for key, value in data.items():
            if isinstance(value, dict):
                value = self.__format_dict(value, depth + 1)
                formatted_string += f"{start}{key}:\n{value}"
            elif isinstance(value, list):
                value = self.__format_list(value, depth + 1)
                formatted_string += f"{start}{key}:\n{value}"
            else:
                formatted_string += f"{start}{key}:\t{value}"

            if key != last_key:
                formatted_string += "\n"
        return formatted_string

    def __format_list(self, data, depth):
        """
        this is a private method so it can only be invoked from inside the class
        assumes data is in type list
        :param data: input list
        :type data: list
        :param depth: recursion depth; not to be set manually
        :type depth: int
        :return: pretty formatted list w/ recursion
        """
        formatted_string = ""
        if len(data) == 0:
            return formatted_string
        start = self.__get_start(depth)
        last_item = data[-1]
        if not all([isinstance(item, dict) for item in data]):
            # if everything in the list is not a dict: add an indentation level
            # list of dictionaries look awkward when they move over two indentation levels w/o this
            depth += 1
        for item in data:

            if isinstance(item, dict):
                value = self.__format_dict(item, depth)
                formatted_string += value
            elif isinstance(item, list):
                value = self.__format_list(item, depth)
                formatted_string += value
            else:
                formatted_string += f"{start}{item}"

            if item != last_item:
                formatted_string += "\n"
        return formatted_string
