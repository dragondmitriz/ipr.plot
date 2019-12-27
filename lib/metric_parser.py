import matplotlib.pyplot as plt


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
        self.disk_rw = {}

        # Очередь дисковой подсистемы (устройство)
        # Очередь дисковой подсистемы: avgqu-sz
        self.disk_qu = {}

        # Утилизация CPU дисковой подсистемой (устройство)
        # Утилизация CPU дисковой подсистемой: %util
        self.disk_CPU = {}

        # Утилизация сетевого интерфейса (интерфейс)
        # Передаваемые данные: txbyt/s | txkB/s
        # Принимаемые данные: rxbyt/s | rxkB/s
        self.net = {}

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
                              'mask': (7, 8)},
                             {'target': self.disk_qu,
                              'filter': 'dev',
                              'mask': (6,)},
                             {'target': self.disk_CPU,
                              'filter': 'dev',
                              'mask': (9,)}]

        self.template_IFACE = [{'target': self.net,
                                'filter': 'dev',
                                'mask': (4, 5)}]

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
            elif sar_line[1] == 'DEV':
                self.template = self.template_DEV
            elif sar_line[1] == 'IFACE' and sar_line[2] == 'rxpck/s':
                self.template = self.template_IFACE
            elif self.template is not None and is_digit(str(sar_line[2])) and sar_line[0] != 'Average:':
                is_add_dev_line = True
                if self.template == self.template_DEV or self.template == self.template_IFACE:
                    is_add_dev_line = False
                for template in self.template:
                    if (template['filter'] is None) or (template['filter'] == sar_line[1]):
                        mask_metrics = []
                        for index_mask in template['mask']:
                            if index_mask is None:
                                mask_metrics.append(None)
                            else:
                                mask_metrics.append(float(sar_line[index_mask]))
                        template['target'].add_value(sar_line[0], mask_metrics)
                        is_add_dev_line = True
                if not is_add_dev_line:
                    if self.template == self.template_DEV:
                        self.disk_rw[sar_line[1]] = TimelineMetrics('Среднее время чтения/записи ' + sar_line[1],
                                                                    'Среднее время выполнения чтения/записи',
                                                                    'Среднее время обслуживания чтения/записи',
                                                                    addY=True)
                        self.disk_qu[sar_line[1]] = TimelineMetrics('Очередь дисковой подсистемы ' + sar_line[1],
                                                                    'Очередь диковой подсистемы')
                        self.disk_CPU[sar_line[1]] = TimelineMetrics(
                            'Утилизация CPU дисковой подсистемой ' + sar_line[1],
                            'Утилизация CPU дисковой подсистемой')
                        self.template.append({'target': self.disk_rw[sar_line[1]],
                                              'filter': sar_line[1],
                                              'mask': (7, 8)})
                        self.template.append({'target': self.disk_qu[sar_line[1]],
                                              'filter': sar_line[1],
                                              'mask': (6,)})
                        self.template.append({'target': self.disk_CPU[sar_line[1]],
                                              'filter': sar_line[1],
                                              'mask': (9,)})
                    elif self.template == self.template_IFACE:
                        self.net[sar_line[1]] = TimelineMetrics('Утилизация сетевого интерфейса ' + sar_line[1],
                                                                'Принимаемые данные',
                                                                'Передаваемые данные')
                        self.template.append({'target': self.net[sar_line[1]],
                                              'filter': sar_line[1],
                                              'mask': (4, 5)})
                    self.add(sar_line)
            else:
                self.template = None

    def add_file(self, filePath):
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

    def update_index_graph(self, index_gr):
        if index_gr[1] >= self.size[1] - 1:
            index_gr[1] = 0
            index_gr[0] += 1
        else:
            index_gr[1] += 1
        if index_gr[0] >= self.size[0]:
            plt.show()
            self.fig = plt.figure(figsize=(16, 9))
            index_gr[0] = 0
            index_gr[1] = 0
        return (index_gr[0], index_gr[1])

    def show(self):
        # Предварительные параметры графиков
        time_step = 40
        self.size = (2, 2)
        index_graph = [0, -1]
        self.fig = plt.figure(figsize=(16, 9))

        # Подготовка данных для прорисовки графиков диска метрик чтения/записи
        arr_metrics_disk_rw = []

        for timeline_metrics in self.disk_rw.values():
            if sum(timeline_metrics.metrics[0]) != 0:
                arr_metrics_disk_rw.append(timeline_metrics)

        # Подготовка данных для прорисовки графиков дисковой очереди
        arr_metrics_disk_qu = []

        for timeline_metrics in self.disk_qu.values():
            if sum(timeline_metrics.metrics[0]) != 0:
                arr_metrics_disk_qu.append(timeline_metrics)

        # Подготовка данных для прорисовки графиков дискового CPU
        arr_metrics_disk_CPU = []

        for timeline_metrics in self.disk_CPU.values():
            if sum(timeline_metrics.metrics[0]) != 0:
                arr_metrics_disk_CPU.append(timeline_metrics)

        # Подготовка данных для прорисовки графиков сетевых интерфейсов
        arr_metrics_net = []

        for timeline_metrics in self.net.values():
            if sum(timeline_metrics.metrics[0]) != 0:
                arr_metrics_net.append(timeline_metrics)

        # ==================CPU====================================
        graph_cpu = plt.subplot2grid(self.size, self.update_index_graph(index_graph))

        # Обработка данных утилизации CPU по формуле =100-%idle
        for index_cpu_metric in range(len(self.CPU.metrics[0])):
            self.CPU.metrics[0][index_cpu_metric] = 100 - self.CPU.metrics[0][index_cpu_metric]

        graph_cpu.plot(self.CPU.time, self.CPU.metrics[0])
        graph_cpu.tick_params(axis='x', rotation=90)

        # Config limit value of axes 'x' for CPU
        x1, x2, y1, y2 = plt.axis()
        plt.axis((x1, x2, 0, max(self.CPU.metrics[0]) + 1))

        graph_runq = graph_cpu.twinx()
        graph_runq.plot(self.CPU.time, self.CPU.metrics[1], color='tab:red')

        # Config limit value of axes 'x' for runq-sz
        x1, x2, y1, y2 = plt.axis()
        plt.axis((x1, x2, 0, max(self.CPU.metrics[1]) * 1.2 // 1 + 1))

        # =================Decorations CPU graph==================
        graph_cpu.tick_params(axis='x', rotation=0, labelsize=12)
        graph_cpu.set_ylabel('Утилизация CPU, %', color='tab:blue', fontsize=12)
        graph_cpu.tick_params(axis='y', rotation=0, labelcolor='tab:blue', labelsize=12)
        graph_cpu.grid(alpha=.4)

        # ax2 (right Y axis)
        graph_runq.set_ylabel("Длина очереди, шт.", color='tab:red', fontsize=12)
        graph_runq.tick_params(axis='y', rotation=0, labelcolor='tab:red')
        graph_runq.set_xticks(range(0, len(self.CPU.time), time_step))
        graph_runq.set_xticklabels(self.CPU.time[::time_step], fontdict={'fontsize': 12})

        graph_runq.set_title("Утилизация CPU", fontsize=16)
        self.fig.tight_layout()
        # =================Finish decoration CPU graph=============

        # =================Memory==================================
        graph_memory = plt.subplot2grid(self.size, self.update_index_graph(index_graph))

        graph_memory.plot(self.memory.time, self.memory.metrics[0])
        graph_memory.tick_params(axis='x', rotation=90)

        # C onfig limit value of axes 'x'
        x1, x2, y1, y2 = plt.axis()
        plt.axis((x1, x2, 0, max(self.memory.metrics[0]) * 1.2 // 1 + 1))

        graph_swp = graph_memory.twinx()
        graph_swp.plot(self.memory.time, self.memory.metrics[1], color='tab:red')

        # Config limit value of axes 'x'
        x1, x2, y1, y2 = plt.axis()
        plt.axis((x1, x2, 0, max(self.memory.metrics[1]) * 1.2 // 1 + 1))

        # =================Decorations memory graph================
        graph_memory.tick_params(axis='x', rotation=0, labelsize=12)
        graph_memory.set_ylabel('Утилизация памяти, %', color='tab:blue', fontsize=12)
        graph_memory.tick_params(axis='y', rotation=0, labelcolor='tab:blue', labelsize=12)
        graph_memory.grid(alpha=.4)

        # ax2 (right Y axis)
        graph_swp.set_ylabel("Утилизация подкачки, %", color='tab:red', fontsize=12)
        graph_swp.tick_params(axis='y', rotation=0, labelcolor='tab:red')
        graph_swp.set_xticks(range(0, len(self.CPU.time), time_step))
        graph_swp.set_xticklabels(self.CPU.time[::time_step], fontdict={'fontsize': 12})

        graph_swp.set_title("Утилизация памяти", fontsize=16)
        self.fig.tight_layout()
        # =================Finish decoration memory graph==========

        # =================Disk Read/Write=========================
        for index_timeline in range(len(arr_metrics_disk_rw)):
            graph_disk_rw = plt.subplot2grid(self.size, self.update_index_graph(index_graph))

            graph_disk_rw.plot(arr_metrics_disk_rw[index_timeline].time,
                               arr_metrics_disk_rw[index_timeline].metrics[0],
                               label=arr_metrics_disk_rw[index_timeline].names[0])
            graph_disk_rw.tick_params(axis='x', rotation=90)

            graph_disk_rw.plot(self.load_avg.time, arr_metrics_disk_rw[index_timeline].metrics[1],
                               label=arr_metrics_disk_rw[index_timeline].names[1])
            graph_disk_rw.tick_params(axis='x', rotation=90)

            # Config limit value of axes 'x'
            x1, x2, y1, y2 = plt.axis()
            plt.axis((x1, x2, 0, max(max(arr_metrics_disk_rw[index_timeline].metrics[0],
                                         arr_metrics_disk_rw[index_timeline].metrics[1])) * 1.2 // 1 + 1))

            # =================Decorations Disk Read/Write graph===
            graph_disk_rw.tick_params(axis='x', rotation=0, labelsize=12)
            graph_disk_rw.set_ylabel('Время, мс.', fontsize=12)
            graph_disk_rw.tick_params(axis='y', rotation=0, labelsize=12)
            graph_disk_rw.grid(alpha=.4)
            graph_disk_rw.set_xticks(range(0, len(arr_metrics_disk_rw[index_timeline].time), time_step))
            graph_disk_rw.set_xticklabels(arr_metrics_disk_rw[index_timeline].time[::time_step],
                                          fontdict={'fontsize': 12})
            graph_disk_rw.set_title(arr_metrics_disk_rw[index_timeline].graph, fontsize=16)
            graph_disk_rw.legend()
            self.fig.tight_layout()
        # =================Finish Disk Read/Write graph============

        # =================Disk Queue=========================
        for index_timeline in range(len(arr_metrics_disk_qu)):
            graph_disk_qu = plt.subplot2grid(self.size, self.update_index_graph(index_graph))

            graph_disk_qu.plot(arr_metrics_disk_qu[index_timeline].time,
                               arr_metrics_disk_qu[index_timeline].metrics[0],
                               label=arr_metrics_disk_qu[index_timeline].names[0])
            graph_disk_qu.tick_params(axis='x', rotation=90)

            # Config limit value of axes 'x'
            x1, x2, y1, y2 = plt.axis()
            plt.axis((x1, x2, 0, max(arr_metrics_disk_qu[index_timeline].metrics[0]) * 1.2 // 1 + 1))

            # =================Decorations Disk Queue graph===
            graph_disk_qu.tick_params(axis='x', rotation=0, labelsize=12)
            graph_disk_qu.set_ylabel('Очередь дисковой подсистемы, шт.', fontsize=12)
            graph_disk_qu.tick_params(axis='y', rotation=0, labelsize=12)
            graph_disk_qu.grid(alpha=.4)
            graph_disk_qu.set_xticks(range(0, len(arr_metrics_disk_qu[index_timeline].time), time_step))
            graph_disk_qu.set_xticklabels(arr_metrics_disk_qu[index_timeline].time[::time_step],
                                          fontdict={'fontsize': 12})
            graph_disk_qu.set_title(arr_metrics_disk_qu[index_timeline].graph, fontsize=16)
            self.fig.tight_layout()
        # =================Finish Disk Queue graph============

        # =================Disk CPU=========================
        for index_timeline in range(len(arr_metrics_disk_CPU)):
            graph_disk_CPU = plt.subplot2grid(self.size, self.update_index_graph(index_graph))

            graph_disk_CPU.plot(arr_metrics_disk_CPU[index_timeline].time,
                                arr_metrics_disk_CPU[index_timeline].metrics[0],
                                label=arr_metrics_disk_CPU[index_timeline].names[0])
            graph_disk_CPU.tick_params(axis='x', rotation=90)

            # Config limit value of axes 'x'
            x1, x2, y1, y2 = plt.axis()
            plt.axis((x1, x2, 0, max(arr_metrics_disk_CPU[index_timeline].metrics[0]) * 1.2 // 1 + 1))

            # =================Decorations Disk CPU graph===
            graph_disk_CPU.tick_params(axis='x', rotation=0, labelsize=12)
            graph_disk_CPU.set_ylabel('Утилизация CPU, %.', fontsize=12)
            graph_disk_CPU.tick_params(axis='y', rotation=0, labelsize=12)
            graph_disk_CPU.grid(alpha=.4)
            graph_disk_CPU.set_xticks(range(0, len(arr_metrics_disk_CPU[index_timeline].time), time_step))
            graph_disk_CPU.set_xticklabels(arr_metrics_disk_CPU[index_timeline].time[::time_step],
                                           fontdict={'fontsize': 12})
            graph_disk_CPU.set_title(arr_metrics_disk_CPU[index_timeline].graph, fontsize=16)
            self.fig.tight_layout()
        # =================Finish Disk CPU graph============

        # =================Network=========================
        for index_timeline in range(len(arr_metrics_net)):
            graph_net = plt.subplot2grid(self.size, self.update_index_graph(index_graph))

            graph_net.plot(arr_metrics_net[index_timeline].time,
                           arr_metrics_net[index_timeline].metrics[0],
                           label=arr_metrics_net[index_timeline].names[0])
            graph_net.tick_params(axis='x', rotation=90)

            graph_net.plot(arr_metrics_net[index_timeline].time, arr_metrics_net[index_timeline].metrics[1],
                           label=arr_metrics_net[index_timeline].names[1])
            graph_net.tick_params(axis='x', rotation=90)

            # Config limit value of axes 'x'
            x1, x2, y1, y2 = plt.axis()
            plt.axis((x1, x2, 0, max(max(arr_metrics_net[index_timeline].metrics[0],
                                         arr_metrics_net[index_timeline].metrics[1])) * 1.2 // 1 + 1))

            # =================Decorations Network graph===
            graph_net.tick_params(axis='x', rotation=0, labelsize=12)
            graph_net.set_ylabel('Передача данных, Кб./с.', fontsize=12)
            graph_net.tick_params(axis='y', rotation=0, labelsize=12)
            graph_net.grid(alpha=.4)
            graph_net.set_xticks(range(0, len(arr_metrics_net[index_timeline].time), time_step))
            graph_net.set_xticklabels(arr_metrics_net[index_timeline].time[::time_step], fontdict={'fontsize': 12})
            graph_net.set_title(arr_metrics_net[index_timeline].graph, fontsize=16)
            graph_net.legend()
            self.fig.tight_layout()
        # =================Finish Disk Network graph============

        # =================Load Average============================
        graph_load_avg = plt.subplot2grid(self.size, self.update_index_graph(index_graph))

        graph_load_avg.plot(self.load_avg.time, self.load_avg.metrics[0], label='1 мин.')
        graph_load_avg.tick_params(axis='x', rotation=90)

        # C onfig limit value of axes 'x'
        x1, x2, y1, y2 = plt.axis()
        plt.axis((x1, x2, 0, max(self.load_avg.metrics[0]) * 1.2 // 1 + 1))

        graph_load_avg.plot(self.load_avg.time, self.load_avg.metrics[1], label='5 мин.')
        graph_load_avg.tick_params(axis='x', rotation=90)

        # C onfig limit value of axes 'x'
        x1, x2, y1, y2 = plt.axis()
        plt.axis((x1, x2, 0, max(self.load_avg.metrics[1]) * 1.2 // 1 + 1))

        graph_load_avg.plot(self.load_avg.time, self.load_avg.metrics[2], label='15 мин.')
        graph_load_avg.tick_params(axis='x', rotation=90)

        # C onfig limit value of axes 'x'
        x1, x2, y1, y2 = plt.axis()
        plt.axis((x1, x2, 0, max(self.load_avg.metrics[2]) * 1.2 // 1 + 1))
        # =================Decorations Load Average graph==========
        graph_load_avg.tick_params(axis='x', rotation=0, labelsize=12)
        graph_load_avg.set_ylabel('Динамика Load Average', fontsize=12)
        graph_load_avg.tick_params(axis='y', rotation=0, labelsize=12)
        graph_load_avg.grid(alpha=.4)
        graph_load_avg.set_xticks(range(0, len(self.load_avg.time), time_step))
        graph_load_avg.set_xticklabels(self.load_avg.time[::time_step], fontdict={'fontsize': 12})
        graph_load_avg.set_title("Динамика Load Average", fontsize=16)
        graph_load_avg.legend()
        self.fig.tight_layout()
        # =================Finish decoration Load Average graph====

        plt.show()
