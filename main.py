from lib.metric_parser import *
import matplotlib.pyplot as plt

sar = SarMetrics()
sar.set_file("sar_mpgu_izh.csv")

fig = plt.figure(figsize=(16, 9))

time_step = 40
#==================CPU=====================================
graph_cpu = plt.subplot2grid((1, 2), (0, 0))

for index_cpu_metric in range(len(sar.CPU.metrics[0])):
    sar.CPU.metrics[0][index_cpu_metric] = 100 - sar.CPU.metrics[0][index_cpu_metric]

graph_cpu.plot(sar.CPU.time, sar.CPU.metrics[0])
graph_cpu.tick_params(axis='x', rotation=90)

#Config limit value of axes 'x' for CPU
x1, x2, y1, y2 = plt.axis()
plt.axis((x1, x2, 0, max(sar.CPU.metrics[0]) + 1))

graph_runq = graph_cpu.twinx()
graph_runq.plot(sar.CPU.time, sar.CPU.metrics[1], color='tab:red')

#Config limit value of axes 'x' for runq-sz
x1, x2, y1, y2 = plt.axis()
plt.axis((x1, x2, 0, max(sar.CPU.metrics[1]) + 1))

#==================Decorations CPU graph===================
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
#==================Finish decoration CPU graph=============

#==================Memory=====================================
graph_memory = plt.subplot2grid((1, 2), (0, 1))

for index_memory_metric in range(len(sar.memory.metrics[0])):
    sar.memory.metrics[0][index_memory_metric] = 100 - sar.memory.metrics[0][index_memory_metric]

graph_memory.plot(sar.memory.time, sar.memory.metrics[0])
graph_memory.tick_params(axis='x', rotation=90)

#C onfig limit value of axes 'x'
x1, x2, y1, y2 = plt.axis()
plt.axis((x1, x2, 0, max(sar.memory.metrics[0]) + 1))

graph_swp = graph_memory.twinx()
graph_swp.plot(sar.memory.time, sar.memory.metrics[1], color='tab:red')

# Config limit value of axes 'x'
x1, x2, y1, y2 = plt.axis()
plt.axis((x1, x2, 0, max(sar.memory.metrics[1]) + 1))

#==================Decorations CPU graph===================
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
#==================Finish decoration CPU graph=============

plt.show()
