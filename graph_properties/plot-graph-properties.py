import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import json
import numpy as np
import matplotlib.pyplot as plt
from collections import OrderedDict


import plotly.graph_objects as go

EPERIMENT_NAME_MAP = OrderedDict({
    "original": "original",
    

    "sc_halted_3_5_true_false_01" : "halted up x2 4 partitions true_false_01",
    "sc_halted_3_5_false_false_0" : "halted up x3 4 partitions",
    "sc_halted_3_5_true_true_01" : "halted scaled up x3 4 partitions true true 01",
    "sc_halted_3_5_true_false_001" : "halted scaled up x3 4 partitions true false 001",

    
    "scala_wild_2_3_true_true_01" : "wild up x2 2 partitions",
    "scala_wild_2_5_true_true_01" : "wild up x2 4 parititons",
    "scala_wild_2_9_true_true_01" : "wild up x2 8 partitions ",
    "scala_wild_2_17_true_true_01" : "wild up x2 16 partitions",


    "scala_halted_2_5_true_true_01" : "halted up x2 4 partitions",
    "scala_halted_2_3_true_true_01" : "halted up x2 2 partitions true_true_01",
    "scala_halted_2_9_true_true_01" : "halted up x2 8 parititions",
    "scala_halted_2_17_true_true_01" : "halted up x2 16 paritions",


    "scala_wild_04_3_true_true_01": "wild down x0.4 2 partitions",
    "scala_wild_04_5_true_true_01": "wild down x0.4 4 partitions",
    "scala_wild_04_9_true_true_01": "wild down x0.4 8 partitions",
    "scala_wild_04_17_true_true_01": "wild down x0.4 16 partitions",


    "scala_halted_04_3_true_true_01": "halted down x0.4 2 partitions",
    "scala_halted_04_5_true_true_01": "halted down x0.4 4 partitions",
    "scala_halted_04_9_true_true_01": "halted down x0.4 8 partitions",
    "scala_halted_04_17_true_true_01" : "halted down x0.4 16 partitons",


    "sc_wild_3_5_false_false_0" : "wild up x3 4 partitions",
    "sc_wild_3_5_true_true_01" : "wild scaled up x3 4 partitions true_true_01",
    "sc_wild_3_5_true_false_01" : "wild scaled up x3 4 partitions true_false_01",
})
'''
input file: scaled_graph_preperties
properties value job
vertex_count 54151 halted_07_5_true_false_01
edge_count 45616 halted_07_5_true_false_01
...
''' 

data = {}
try:
    with open("all_properties_for_kgs.json") as file:
        data = json.load(file)
except Exception as e:
    pass
try:
    with open("all_properties_for_wiki_talk.json") as file2:
        data = json.load(file2)
except Exception as e:
    print(e)
try:
    with open("all_properties_for_cit_patents.json") as file3:
        data = json.load(file3)
except Exception as e:
    print(e)

# fig, axs = plt.subplots(2,1)
# # axs[0].axis('tight')
# # axs[0].axis('off')

headers_properties = ['experiment']
rows_experiments = []
d = False
real_data = []
for sim in data.keys():
    row = []
    for experiment in EPERIMENT_NAME_MAP.keys():
        if sim.find(experiment) > -1:
            # print(f"found at  {experiment.find(sim)}")
            row.append(EPERIMENT_NAME_MAP[experiment])
            break
    for prop in data[sim]:
        val = data[sim][prop]
        if isinstance(val, float):
            if val < 0.004:
                val = np.format_float_scientific(val, 2, False, '.')
            else:
                val = np.round_(val, 2)
        row.append(val)
        if d:
            continue
        else:
            headers_properties.append(prop.replace("_", " "))
    real_data.append(row)
    # print("appending row " + str(row))
    d=True

empty_row = ["","","","","",""]

print(real_data[0])
print(real_data[1])


ordered_data = []
line_num = 0
for experiment in EPERIMENT_NAME_MAP.keys():
    for res in real_data:
        if res[0] == EPERIMENT_NAME_MAP[experiment]:
            ordered_data.append(res)
            line_num+=1
            break
    if line_num == 5 or line_num == 9 or line_num==13 or line_num == 17 or line_num == 21:
        ordered_data.append(empty_row)

actual_data = np.transpose(ordered_data)


    # for experiment in EPERIMENT_NAME_MAP.keys():
    #     if sim.find(experiment) > -1:
    #         print(f"found at  {experiment.find(sim)}")
    #         row.append(EPERIMENT_NAME_MAP[experiment])
    #         break

fig = go.Figure(data=[go.Table(
    header=dict(values=headers_properties,
                fill_color='lightgray',
                align='left',
                line_color='black',
                font_size=10,),
    columnwidth = [80,20],
    cells=dict(values=actual_data,
                line_color='grey',
                fill_color='white',
                align='left',
                font_size=10))
])


fig.show()



# real_data = np.array(real_data)
# the_table = axs[0].table(cellText=real_data, colLabels=colLabels, loc='top')

# axs[1].plot(real_data[:,0], real_data[:,1])
# plt.show()
# print(np.array(real_data))
# print(colLabels)
# print(rowLabels)


# plt.plot(data=data)
# table = plt.table(cellText=data, colLabels=colLabels, rowLabels=rowLabels)
# axs[1].plot(data)
# plt.show()




# fig = plt.figure(constrained_layout=True)
# width = 3.487 *2
# height = width / 1.618
# axes = []
# spec = gridspec.GridSpec(ncols=2, nrows=3, figure=fig)
# whatever = {}
# for sim in data.keys():
#     # axes.append(fig.add_subplot(data[sim]['vertex_count']))
#     whatever[str(sim)] =  [data[sim]['vertex_count']]

# whatever = pd.DataFrame(whatever)
# ax = sns.barplot(data=whatever)
# plt.plot()
# plt.show()

# df = pd.read_json("all_properties_for_kgs.json", sep=" ", index_col=None)

# fig = plt.figure(constrained_layout=True)
# spec = gridspec.GridSpec(ncols=2, nrows=3, figure=fig)
# width = 3.487 *2
# height = width / 1.618
# axes = []
# axes.append(fig.add_subplot(spec[0, 0]))
# axes.append(fig.add_subplot(spec[0, 1]))
# axes.append(fig.add_subplot(spec[1, 0]))
# axes.append(fig.add_subplot(spec[1, 1]))
# axes.append(fig.add_subplot(spec[2, 0]))
# axes.append(fig.add_subplot(spec[2, 1]))

# ax = sns.barplot(x="properties", y="value", hue="job", data=df[df.properties == "vertex_count"], ax=axes[0])
# ax = sns.barplot(x="properties", y="value", hue="job", data=df[df.properties == "edge_count"], ax=axes[1])
# ax = sns.barplot(x="properties", y="value", hue="job", data=df[df.properties == "density"], ax=axes[2])
# ax = sns.barplot(x="properties", y="value", hue="job", data=df[df.properties == "component_count"], ax=axes[3])
# ax = sns.barplot(x="properties", y="value", hue="job", data=df[df.properties == "node_connectivity"], ax=axes[4])
# ax = sns.barplot(x="properties", y="value", hue="job", data=df[df.properties == "avg_node_degree"], ax=axes[5])
# # plt.show()
# plt.savefig(f"figures/graph-properties.svg", format='svg', dpi=300)