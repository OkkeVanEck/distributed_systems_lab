import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from argparse import ArgumentParser
from pathlib import Path

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('src', type=str, help='Path to job folder')
    parser.add_argument('jobs', nargs='+', help='jobs to plot', type=str)
    args = parser.parse_args()
    return args

def get_data(path_to_job, job_names):
    data = []
    p = Path(path_to_job)
    for job_name in job_names:
        df = pd.read_json(p / job_name / "results" / "scaled_graph_properties.json", typ='series').reset_index()
        df.columns = ["properties", "value"]
        df["job"] = job_name
        data.append(df)
    return pd.concat(data)

def plot(data):
    fig = plt.figure(constrained_layout=True)
    spec = gridspec.GridSpec(ncols=4, nrows=2, figure=fig)
    axes = []
    for i in range(2):
        for j in range(4):
            axes.append(fig.add_subplot(spec[i, j]))

    for i, graph_property in enumerate(data.properties.drop_duplicates()):
        ax = sns.barplot(x="properties", y="value", hue="job", data=data[data.properties == graph_property], ax=axes[i])
        
    plt.show()

if __name__ == "__main__":
    args = parse_args()
    plot(get_data(args.src, args.jobs))

# python code/scripts/plot_properties.py jobs kgs_sc_halted_3_5_false_false_0 kgs_sc_halted_3_5_true_false_01 kgs_sc_halted_3_5_true_false_001 kgs_sc_halted_3_5_true_true_01