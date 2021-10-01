import logging
import pandas


class Zeitplan(object):
    _eventToColorMapping = {
        # Saturday:
        "U12W": "orange",
        "U12M": "yellow",
        "U16W": "pink",
        "U16M": "blue",
        "WOM_7K": "green",
        "MAN_10K": "red",
        # Sunday:
        "U14W": "orange",
        "U14M": "yellow",
        "WOM_5K": "pink",
        "MAN_6K": "blue",
        "WOM_7K": "green",
        "MAN_10K": "red",
    }

    def __init__(self, elements, resources):
        self._elements = elements
        self._resources = resources

    def getElements(self, resource_name):
        elements = []
        column_index = self._resources.index(resource_name)
        for element in self._elements:
            if element[1] == resource_name:
                print(column_index, element, self.getColorFromEvent(element[0]))
                elements.append((element, column_index, self.getColorFromEvent(element[0])))
        return elements

    def getColorFromEvent(self, eventName):
        for k, v in self._eventToColorMapping.items():
            if eventName.startswith(k):
                return v
        return self._eventToColorMapping[eventName]


def main(args):
    logging.debug("main({})".format(args))
    contentAsString = args.file.read()
    #print("content: {!r}".format(contentAsString))

    withoutBrackets = contentAsString[1:-1]
    #print("without-brackets: {!r}".format(withoutBrackets))
    elementsAsStrings = withoutBrackets.split("), (")
    elementsAsStrings[0] = elementsAsStrings[0][1:]
    elementsAsStrings[-1] = elementsAsStrings[-1][:-1]
    #print("elements: {!r}".format(elementsAsStrings))
    elements = []
    for elementAsString in elementsAsStrings:
        parts = elementAsString.split(', ')
        elements.append((parts[0], parts[1], int(parts[2]), int(parts[3])))
    #print("elements: {!r}".format(elements))

    resources = ["Läufe", "Weit1", "Weit2", "Hoch1", "Hoch2", "Kugel1", "Kugel2", "Diskus", "Speer1", "Speer2", "Stab"]

    zeitplan = Zeitplan(elements, resources)

    lauf_elements = zeitplan.getElements("Läufe")
    print("lauf-elements: {!r}".format(lauf_elements))

    writer = pandas.ExcelWriter('zeitplan.xlsx', engine='xlsxwriter')
    workbook = writer.book
    worksheet = workbook.add_worksheet('Samstag')

    title_cell_format = workbook.add_format()
    title_cell_format.set_font_size(14)
    title_cell_format.set_bold()
    worksheet.write('A1', 'Zeitplan Uster Mehrkampf Meeting: Samstag 25.9.2021', title_cell_format)

    heading_cell_format = workbook.add_format()
    heading_cell_format.set_bold()
    heading_cell_format.set_border()

    empty_table_cell_format = workbook.add_format()
    empty_table_cell_format.set_border()

    for column_index, resource in enumerate(resources):
        elements = zeitplan.getElements(resource)
        for element in elements:
            worksheet.write(2, column_index + 1, resource, heading_cell_format)
            color = element[2]
            start_time = element[0][2]
            end_time = element[0][3]
            cell_format = workbook.add_format()
            cell_format.set_pattern(1)
            cell_format.set_border()
            cell_format.set_bg_color(color)
            for row_index in range(start_time, end_time - 1):
                content = ''
                if row_index == start_time:
                    content = element[0][0]
                    if resource != "Läufe":
                        content = content.split('_')[-2]
                worksheet.write(row_index + 3, column_index + 1, content, cell_format)

    writer.save()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='generate xlsx zeitplan')
    parser.add_argument('-v', '--verbose', action="store_true", help="be verbose")
    parser.add_argument('file', type=argparse.FileType('r'), help='solution-file')
    args = parser.parse_args()
    main(args)
