def is_digit(str_item):
    if str_item.isdigit():
        return True
    else:
        try:
            float(str_item)
            return True
        except ValueError:
            return False


class TimelineMetrics:

    def __init__(self, graph, *names, addY=False):
        self.graph = graph
        self.names = names
        self.time = []
        self.metrics = []
        for index_name in range(len(self.names)):
            self.metrics.append([])
        self.addY = addY

    def index_time(self, time):
        try:
            index = self.time.index(time)
            return index
        except ValueError:
            return -1

    def add_value(self, time, metrics):
        index = self.index_time(time)
        if index >= 0:
            for index_name in range(len(self.names)):
                if metrics[index_name] is not None:
                    self.metrics[index_name][index] = metrics[index_name]
        else:
            self.time.append(time)
            for index_name in range(len(self.names)):
                self.metrics[index_name].append(metrics[index_name])


class SarMetrics:

    def __init__(self):

        # Утилизация CPU
        # утилизация CPU: %idle all
        # длина очереди: runq-sz
        self.CPU = TimelineMetrics('Утилизация CPU', 'Утилизация CPU', 'Длина очереди', addY=True)

        # Утилизация памяти
        # Утилизация памяти: %memused
        # Утилизация подкачки: %swpused
        self.memory = TimelineMetrics('Утилизация памяти', 'Утилизация памяти', 'Утилизация подкачки', addY=True)

        # Среднее время чтения/записи (устройство)
        # Среднее время выполнения чтения/записи: await
        # Среднее время обслуживания чтения/записи: svctm
        self.disk_rw = TimelineMetrics('Среднее время чтения/записи',
                                       'Среднее время выполнения чтения/записи',
                                       'Среднее время обслуживания чтения/записи',
                                       addY=True)

        # Очередь дисковой подсистемы (устройство)
        # Очередь дисковой подсистемы: avgqu-sz
        self.disk_qu = TimelineMetrics('Очередь дисковой подсистемы', 'Очередь диковой подсистемы')

        # Утилизация CPU дисковой подсистемой (устройство)
        # Утилизация CPU дисковой подсистемой: %util
        self.disk_CPU = TimelineMetrics('Утилизация CPU дисковой подсистемой', 'Утилизация CPU дисковой подсистемой')

        # Утилизация сетевого интерфейса (интерфейс)
        # Передаваемые данные: txbyt/s | txkB/s
        # Принимаемые данные: rxbyt/s | rxkB/s
        self.net = TimelineMetrics('Утилизация сетевого интерфейса', 'Передаваемые данные', 'Принимаемые данные')

        # Динамика Load Average
        # за 1 минуту: ldavg-1
        # за 5 минут: ldavg-5
        # за 15 минут: ldavg-15
        self.load_avg = TimelineMetrics('Динамика Load Average', 'за 1 минуту', 'за 5 минут', 'за 15 минут')

        self.template_CPU = [{'target': self.CPU,
                              'filter': 'all',
                              'mask': (10, None)}]

        self.template_runq_sz = [{'target': self.CPU,
                                  'filter': None,
                                  'mask': (None, 1)},
                                 {'target': self.load_avg,
                                  'filter': None,
                                  'mask': (3, 4, 5)}]

        self.template_runq_sz = [{'target': self.CPU,
                                  'filter': None,
                                  'mask': (None, 1)},
                                 {'target': self.load_avg,
                                  'filter': None,
                                  'mask': (3, 4, 5)}]

        self.template_kbmemfree = [{'target': self.memory,
                                    'filter': None,
                                    'mask': (3, None)}]

        self.template_kbswpfree = [{'target': self.memory,
                                    'filter': None,
                                    'mask': (None, 3)}]

        self.template_DEV = [{'target': self.disk_rw,
                              'filter': 'dev',
                              'mask': (7, 8)}]

        self.template = None

    def add(self, sar_line):
        if len(sar_line) > 1:
            if sar_line[1] == 'CPU' and sar_line[2] == '%usr':
                self.template = self.template_CPU
            elif sar_line[1] == 'runq-sz':
                self.template = self.template_runq_sz
            elif sar_line[1] == 'kbmemfree':
                self.template = self.template_kbmemfree
            elif sar_line[1] == 'kbswpfree':
                self.template = self.template_kbswpfree
            elif self.template is not None and is_digit(str(sar_line[2])) and sar_line[0] != 'Average:':
                for template in self.template:
                    if (template['filter'] is None) or (template['filter'] == 'all' and sar_line[1] == 'all'):
                        mask_metrics = []
                        for index_mask in template['mask']:
                            if index_mask is None:
                                mask_metrics.append(None)
                            else:
                                mask_metrics.append(float(sar_line[index_mask]))
                        template['target'].add_value(sar_line[0], mask_metrics)
            else:

                self.template = None

    def set_file(self, filePath):
        csvFile = open(filePath, "r")

        line = csvFile.readline()
        while line != '':
            arr_line = []
            item = ''
            for i in range(len(line)):
                if line[i] == ' ' or line[i] == '\n':
                    if item != '':
                        arr_line.append(item)
                        item = ''
                else:
                    item += line[i]

            self.add(arr_line)
            line = csvFile.readline()

        csvFile.close()