from lib.metric_parser import *
import matplotlib.pyplot as plt

index_graph = [0, -1]


def update_index_graph(index_gr):
    if index_gr[1] >= size[1] - 1:
        index_gr[1] = 0
        index_gr[0] += 1
    else:
        index_gr[1] += 1
    if index_gr[0] >= size[0]:
        plt.show()
        fig = plt.figure(figsize=(16, 9))
        index_gr[0] = 0
        index_gr[1] = 0
    return (index_gr[0], index_gr[1])


sar = SarMetrics()
sar.set_file("sar_mpgu_izh.csv")

fig = plt.figure(figsize=(16, 9))

# Подготовка данных для прорисовки графиков диска метрик чтения/записи
arr_metrics_disk_rw = []

for timeline_metrics in sar.disk_rw.values():
    if sum(timeline_metrics.metrics[0]) != 0:
        arr_metrics_disk_rw.append(timeline_metrics)

# Подготовка данных для прорисовки графиков дисковой очереди
arr_metrics_disk_qu = []

for timeline_metrics in sar.disk_qu.values():
    if sum(timeline_metrics.metrics[0]) != 0:
        arr_metrics_disk_qu.append(timeline_metrics)

# Подготовка данных для прорисовки графиков дискового CPU
arr_metrics_disk_CPU = []

for timeline_metrics in sar.disk_CPU.values():
    if sum(timeline_metrics.metrics[0]) != 0:
        arr_metrics_disk_CPU.append(timeline_metrics)

# Подготовка данных для прорисовки графиков сетевых интерфейсов
arr_metrics_net = []

for timeline_metrics in sar.net.values():
    if sum(timeline_metrics.metrics[0]) != 0:
        arr_metrics_net.append(timeline_metrics)

# Предварительные параметры графиков
time_step = 40
size = (2, 2)

# ==================CPU====================================
graph_cpu = plt.subplot2grid(size, update_index_graph(index_graph))

# Обработка данных утилизации CPU по формуле =100-%idle
for index_cpu_metric in range(len(sar.CPU.metrics[0])):
    sar.CPU.metrics[0][index_cpu_metric] = 100 - sar.CPU.metrics[0][index_cpu_metric]

graph_cpu.plot(sar.CPU.time, sar.CPU.metrics[0])
graph_cpu.tick_params(axis='x', rotation=90)

# Config limit value of axes 'x' for CPU
x1, x2, y1, y2 = plt.axis()
plt.axis((x1, x2, 0, max(sar.CPU.metrics[0]) + 1))

graph_runq = graph_cpu.twinx()
graph_runq.plot(sar.CPU.time, sar.CPU.metrics[1], color='tab:red')

# Config limit value of axes 'x' for runq-sz
x1, x2, y1, y2 = plt.axis()
plt.axis((x1, x2, 0, max(sar.CPU.metrics[1])*1.2//1+1))

# =================Decorations CPU graph==================
graph_cpu.tick_params(axis='x', rotation=0, labelsize=12)
graph_cpu.set_ylabel('Утилизация CPU, %', color='tab:blue', fontsize=12)
graph_cpu.tick_params(axis='y', rotation=0, labelcolor='tab:blue', labelsize=12)
graph_cpu.grid(alpha=.4)

# ax2 (right Y axis)
graph_runq.set_ylabel("Длина очереди, шт.", color='tab:red', fontsize=12)
graph_runq.tick_params(axis='y', rotation=0, labelcolor='tab:red')
graph_runq.set_xticks(range(0, len(sar.CPU.time), time_step))
graph_runq.set_xticklabels(sar.CPU.time[::time_step], fontdict={'fontsize': 12})

graph_runq.set_title("Утилизация CPU", fontsize=16)
fig.tight_layout()
# =================Finish decoration CPU graph=============

# =================Memory==================================
graph_memory = plt.subplot2grid(size, update_index_graph(index_graph))

graph_memory.plot(sar.memory.time, sar.memory.metrics[0])
graph_memory.tick_params(axis='x', rotation=90)

# C onfig limit value of axes 'x'
x1, x2, y1, y2 = plt.axis()
plt.axis((x1, x2, 0, max(sar.memory.metrics[0])*1.2//1+1))

graph_swp = graph_memory.twinx()
graph_swp.plot(sar.memory.time, sar.memory.metrics[1], color='tab:red')

# Config limit value of axes 'x'
x1, x2, y1, y2 = plt.axis()
plt.axis((x1, x2, 0, max(sar.memory.metrics[1])*1.2//1+1))

# =================Decorations memory graph================
graph_memory.tick_params(axis='x', rotation=0, labelsize=12)
graph_memory.set_ylabel('Утилизация памяти, %', color='tab:blue', fontsize=12)
graph_memory.tick_params(axis='y', rotation=0, labelcolor='tab:blue', labelsize=12)
graph_memory.grid(alpha=.4)

# ax2 (right Y axis)
graph_swp.set_ylabel("Утилизация подкачки, %", color='tab:red', fontsize=12)
graph_swp.tick_params(axis='y', rotation=0, labelcolor='tab:red')
graph_swp.set_xticks(range(0, len(sar.CPU.time), time_step))
graph_swp.set_xticklabels(sar.CPU.time[::time_step], fontdict={'fontsize': 12})

graph_swp.set_title("Утилизация памяти", fontsize=16)
fig.tight_layout()
# =================Finish decoration memory graph==========

# =================Disk Read/Write=========================
for index_timeline in range(len(arr_metrics_disk_rw)):
    graph_disk_rw = plt.subplot2grid(size, update_index_graph(index_graph))

    graph_disk_rw.plot(arr_metrics_disk_rw[index_timeline].time,
                       arr_metrics_disk_rw[index_timeline].metrics[0],
                       label=arr_metrics_disk_rw[index_timeline].names[0])
    graph_disk_rw.tick_params(axis='x', rotation=90)

    graph_disk_rw.plot(sar.load_avg.time, arr_metrics_disk_rw[index_timeline].metrics[1],
                       label=arr_metrics_disk_rw[index_timeline].names[1])
    graph_disk_rw.tick_params(axis='x', rotation=90)

    # Config limit value of axes 'x'
    x1, x2, y1, y2 = plt.axis()
    plt.axis((x1, x2, 0, max(max(arr_metrics_disk_rw[index_timeline].metrics[0], arr_metrics_disk_rw[index_timeline].metrics[1]))*1.2//1+1))

    # =================Decorations Disk Read/Write graph===
    graph_disk_rw.tick_params(axis='x', rotation=0, labelsize=12)
    graph_disk_rw.set_ylabel('Время, мс.', fontsize=12)
    graph_disk_rw.tick_params(axis='y', rotation=0, labelsize=12)
    graph_disk_rw.grid(alpha=.4)
    graph_disk_rw.set_xticks(range(0, len(arr_metrics_disk_rw[index_timeline].time), time_step))
    graph_disk_rw.set_xticklabels(arr_metrics_disk_rw[index_timeline].time[::time_step], fontdict={'fontsize': 12})
    graph_disk_rw.set_title(arr_metrics_disk_rw[index_timeline].graph, fontsize=16)
    graph_disk_rw.legend()
    fig.tight_layout()
# =================Finish Disk Read/Write graph============

# =================Disk Queue=========================
for index_timeline in range(len(arr_metrics_disk_qu)):
    graph_disk_qu = plt.subplot2grid(size, update_index_graph(index_graph))

    graph_disk_qu.plot(arr_metrics_disk_qu[index_timeline].time,
                       arr_metrics_disk_qu[index_timeline].metrics[0],
                       label=arr_metrics_disk_qu[index_timeline].names[0])
    graph_disk_qu.tick_params(axis='x', rotation=90)

    # Config limit value of axes 'x'
    x1, x2, y1, y2 = plt.axis()
    plt.axis((x1, x2, 0, max(arr_metrics_disk_qu[index_timeline].metrics[0])*1.2//1+1))

    # =================Decorations Disk Queue graph===
    graph_disk_qu.tick_params(axis='x', rotation=0, labelsize=12)
    graph_disk_qu.set_ylabel('Очередь дисковой подсистемы, шт.', fontsize=12)
    graph_disk_qu.tick_params(axis='y', rotation=0, labelsize=12)
    graph_disk_qu.grid(alpha=.4)
    graph_disk_qu.set_xticks(range(0, len(arr_metrics_disk_qu[index_timeline].time), time_step))
    graph_disk_qu.set_xticklabels(arr_metrics_disk_qu[index_timeline].time[::time_step], fontdict={'fontsize': 12})
    graph_disk_qu.set_title(arr_metrics_disk_qu[index_timeline].graph, fontsize=16)
    fig.tight_layout()
# =================Finish Disk Queue graph============

# =================Disk CPU=========================
for index_timeline in range(len(arr_metrics_disk_CPU)):
    graph_disk_CPU = plt.subplot2grid(size, update_index_graph(index_graph))

    graph_disk_CPU.plot(arr_metrics_disk_CPU[index_timeline].time,
                       arr_metrics_disk_CPU[index_timeline].metrics[0],
                       label=arr_metrics_disk_CPU[index_timeline].names[0])
    graph_disk_CPU.tick_params(axis='x', rotation=90)

    # Config limit value of axes 'x'
    x1, x2, y1, y2 = plt.axis()
    plt.axis((x1, x2, 0, max(arr_metrics_disk_CPU[index_timeline].metrics[0])*1.2//1+1))

    # =================Decorations Disk CPU graph===
    graph_disk_CPU.tick_params(axis='x', rotation=0, labelsize=12)
    graph_disk_CPU.set_ylabel('Утилизация CPU, %.', fontsize=12)
    graph_disk_CPU.tick_params(axis='y', rotation=0, labelsize=12)
    graph_disk_CPU.grid(alpha=.4)
    graph_disk_CPU.set_xticks(range(0, len(arr_metrics_disk_CPU[index_timeline].time), time_step))
    graph_disk_CPU.set_xticklabels(arr_metrics_disk_CPU[index_timeline].time[::time_step], fontdict={'fontsize': 12})
    graph_disk_CPU.set_title(arr_metrics_disk_CPU[index_timeline].graph, fontsize=16)
    fig.tight_layout()
# =================Finish Disk CPU graph============

# =================Network=========================
for index_timeline in range(len(arr_metrics_net)):
    graph_net = plt.subplot2grid(size, update_index_graph(index_graph))

    graph_net.plot(arr_metrics_net[index_timeline].time,
                       arr_metrics_net[index_timeline].metrics[0],
                       label=arr_metrics_net[index_timeline].names[0])
    graph_net.tick_params(axis='x', rotation=90)

    graph_net.plot(arr_metrics_net[index_timeline].time, arr_metrics_net[index_timeline].metrics[1],
                       label=arr_metrics_net[index_timeline].names[1])
    graph_net.tick_params(axis='x', rotation=90)

    # Config limit value of axes 'x'
    x1, x2, y1, y2 = plt.axis()
    plt.axis((x1, x2, 0, max(max(arr_metrics_net[index_timeline].metrics[0], arr_metrics_net[index_timeline].metrics[1]))*1.2//1+1))

    # =================Decorations Network graph===
    graph_net.tick_params(axis='x', rotation=0, labelsize=12)
    graph_net.set_ylabel('Передача данных, Кб./с.', fontsize=12)
    graph_net.tick_params(axis='y', rotation=0, labelsize=12)
    graph_net.grid(alpha=.4)
    graph_net.set_xticks(range(0, len(arr_metrics_net[index_timeline].time), time_step))
    graph_net.set_xticklabels(arr_metrics_net[index_timeline].time[::time_step], fontdict={'fontsize': 12})
    graph_net.set_title(arr_metrics_net[index_timeline].graph, fontsize=16)
    graph_net.legend()
    fig.tight_layout()
# =================Finish Disk Network graph============

# =================Load Average============================
graph_load_avg = plt.subplot2grid(size, update_index_graph(index_graph))

graph_load_avg.plot(sar.load_avg.time, sar.load_avg.metrics[0], label='1 мин.')
graph_load_avg.tick_params(axis='x', rotation=90)

# C onfig limit value of axes 'x'
x1, x2, y1, y2 = plt.axis()
plt.axis((x1, x2, 0, max(sar.load_avg.metrics[0])*1.2//1+1))

graph_load_avg.plot(sar.load_avg.time, sar.load_avg.metrics[1], label='5 мин.')
graph_load_avg.tick_params(axis='x', rotation=90)

# C onfig limit value of axes 'x'
x1, x2, y1, y2 = plt.axis()
plt.axis((x1, x2, 0, max(sar.load_avg.metrics[1])*1.2//1+1))

graph_load_avg.plot(sar.load_avg.time, sar.load_avg.metrics[2], label='15 мин.')
graph_load_avg.tick_params(axis='x', rotation=90)

# C onfig limit value of axes 'x'
x1, x2, y1, y2 = plt.axis()
plt.axis((x1, x2, 0, max(sar.load_avg.metrics[2])*1.2//1+1))
# =================Decorations Load Average graph==========
graph_load_avg.tick_params(axis='x', rotation=0, labelsize=12)
graph_load_avg.set_ylabel('Динамика Load Average', fontsize=12)
graph_load_avg.tick_params(axis='y', rotation=0, labelsize=12)
graph_load_avg.grid(alpha=.4)
graph_load_avg.set_xticks(range(0, len(sar.load_avg.time), time_step))
graph_load_avg.set_xticklabels(sar.load_avg.time[::time_step], fontdict={'fontsize': 12})
graph_load_avg.set_title("Динамика Load Average", fontsize=16)
graph_load_avg.legend()
fig.tight_layout()
# =================Finish decoration Load Average graph====


plt.show()
