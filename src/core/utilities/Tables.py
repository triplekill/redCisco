from prettytable import PrettyTable


def generate_table(field_names: list, field_values: list) -> str:
    x = PrettyTable()
    x.border = False
    x.padding_width = 2
    x.field_names = field_names
    separator = []
    for _value in field_names:
        separator += ['-' * len(_value)]
    x.add_row(separator)
    for value in field_values:
        x.add_row(value)
        x.align = "l"
    return "{}".format(x.get_string())
