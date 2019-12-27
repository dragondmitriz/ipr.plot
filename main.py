from lib.metric_parser import *
import matplotlib.pyplot as plt

# index_graph = [0, -1]
#
#
# def update_index_graph(index_gr):
#     if index_gr[1] >= size[1] - 1:
#         index_gr[1] = 0
#         index_gr[0] += 1
#     else:
#         index_gr[1] += 1
#     if index_gr[0] >= size[0]:
#         plt.show()
#         fig = plt.figure(figsize=(16, 9))
#         index_gr[0] = 0
#         index_gr[1] = 0
#     return (index_gr[0], index_gr[1])


sar = SarMetrics()
sar.add_file("sar_mpgu_izh.csv")
sar.show()