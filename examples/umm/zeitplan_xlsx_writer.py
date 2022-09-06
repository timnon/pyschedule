from datetime import datetime, timedelta
import logging
import pandas


class Zeitplan(object):
    _eventToColorMapping = {
        # Saturday:
        "U12W": "orange",
        "U12M": "yellow",
        "U16W": "pink",
        "U16M": "cyan",
        "WOM_7K": "green",
        "MAN_10K": "red",
        # Sunday:
        "U14W": "orange",
        "U14M": "yellow",
        "WOM_5K": "pink",
        "MAN_6K": "cyan",
        "WOM_7K": "green",
        "MAN_10K": "red",
    }

    def __init__(self, tasks, resources):
        self._tasks = tasks
        self._resources = resources

    def getTasks(self, resource_name):
        tasks = []
        column_index = self._resources.index(resource_name)
        for task in self._tasks:
            if task[1] == resource_name:
                print(column_index, task, self.getColorFromEvent(task[0]))
                tasks.append((task, column_index, self.getColorFromEvent(task[0])))
        return tasks

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
    tasksAsStrings = withoutBrackets.split("), (")
    tasksAsStrings[0] = tasksAsStrings[0][1:]
    tasksAsStrings[-1] = tasksAsStrings[-1][:-1]
    #print("tasks: {!r}".format(tasksAsStrings))
    tasks = []
    for taskAsString in tasksAsStrings:
        parts = taskAsString.split(', ')
        tasks.append((parts[0], parts[1], int(parts[2]), int(parts[3])))
    #print("tasks: {!r}".format(tasks))

    resources = ["Läufe", "Weit1", "Weit2", "Hoch1", "Hoch2", "Kugel1", "Kugel2", "Diskus", "Speer", "Stab"]

    zeitplan = Zeitplan(tasks, resources)

    writer = pandas.ExcelWriter('zeitplan.xlsx', engine='xlsxwriter')
    workbook = writer.book
    worksheet = workbook.add_worksheet()

    title_cell_format = workbook.add_format()
    title_cell_format.set_font_size(14)
    title_cell_format.set_bold()
    worksheet.write('A1', 'Zeitplan Uster Mehrkampf Meeting', title_cell_format)

    heading_cell_format = workbook.add_format()
    heading_cell_format.set_bold()
    heading_cell_format.set_border()

    empty_table_cell_format = workbook.add_format()
    empty_table_cell_format.set_border()

    def get_time(row_index):
        if args.start_time is None:
            return str(row_index)
        ts_start = datetime.strptime(args.start_time, "%H:%M")
        ts_end = ts_start + timedelta(minutes=10*row_index)
        return ts_end.time().strftime("%-H:%M")

    for column_index, resource in enumerate(resources):
        tasks = zeitplan.getTasks(resource)
        if resource == "Läufe":
            first_task = tasks[0][0][2]
            last_task = tasks[-1][0][3] - 2
            worksheet.write(2, 0, 'Zeit', heading_cell_format)
            for row_index in range(first_task, last_task + 1):
                worksheet.write(row_index + 3, 0, get_time(row_index), empty_table_cell_format)
        filled_slots = []
        for task in tasks:
            worksheet.write(2, column_index + 1, resource, heading_cell_format)
            color = task[2]
            start_time = task[0][2]
            end_time = task[0][3]
            cell_format = workbook.add_format()
            cell_format.set_pattern(1)
            cell_format.set_border()
            cell_format.set_bg_color(color)
            for row_index in range(start_time, end_time - 1):
                content = ''
                if row_index == start_time:
                    content = task[0][0]
                    if resource != "Läufe":
                        content = content.split('_')[-2]
                worksheet.write(row_index + 3, column_index + 1, content, cell_format)
                filled_slots.append(row_index)
        for row_index in range(first_task, last_task + 1):
            if row_index not in filled_slots:
                worksheet.write(row_index + 3, column_index + 1, '', empty_table_cell_format)
    writer.save()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='generate xlsx zeitplan')
    parser.add_argument('-v', '--verbose', action="store_true", help="be verbose")
    parser.add_argument('-s', '--start-time', help="start time")
    parser.add_argument('file', type=argparse.FileType('r'), help='solution-file')
    args = parser.parse_args()
    main(args)
