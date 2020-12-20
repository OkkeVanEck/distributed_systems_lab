import matplotlib.pyplot as plt
import os
import pandas as pd
import re
from argparse import ArgumentParser
from matplotlib import cm
from pathlib import Path

# python code/scripts/plot_timing.py jobs kgs scala halted 04 true true 01
# python code/scripts/plot_timing.py jobs kgs scala wild 2 true true 01

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('src', type=str, help='Path to job folder')
    parser.add_argument('dset', type=str, help='Dataset name')
    parser.add_argument('job', type=str, help='Type of job')
    parser.add_argument('sim', type=str, help='Type of simulation')
    parser.add_argument('scale', type=str, help='Scale factor')
    parser.add_argument('stitch', type=str, help='Do stitching')
    parser.add_argument('ring', type=str, help='Ring stitching')
    parser.add_argument('conn', type=str, help='Connectivity')
    args = parser.parse_args()
    return args


def parse_job_name(job_name):
    m = re.match(
        r"(?P<dset>[\w-]+)_(?P<job>\w+)_(?P<sim>\w+)_"
        r"(?P<scale>[0-9]+)_(?P<n_nodes>[0-9]+)_"
        r"(?P<stitch>\w+)_(?P<ring>\w+)_(?P<conn>[0-9]+)",
        job_name
    )
    return m.groupdict()


class TimingVisiualizer:
    def __init__(self, path_to_jobs, dset, job, sim, scale, stitch, ring, conn):
        """Requires multiple jobs under same setting except for different n_nodes.
        
        Arguments:
        path_to_jobs -- path to jobs (ex: jobs, /var/scratch/$USER, ...)
        dset -- dataset name (ex: kgs, wiki-Talk, cit-Patents, ...)
        job -- types of job (sc, scala)
        sim -- types of simluation (wild, halted)
        scale -- scale factor
        stitch -- if do stitching or not (true, false)
        ring -- if do ring stitching or not (true, false)
        conn -- connectivity (for example, 0, 01, 001, ...)
        """
        self.path_to_jobs = path_to_jobs
        self.dset = dset
        self.job = job
        self.sim = sim
        self.scale = scale
        self.stitch = stitch
        self.ring = ring
        self.conn = conn

        self.worker = None
        self.header = None

    def get_vis_jobs(self):
        return [
            job for job in os.listdir(self.path_to_jobs) 
            if re.match(
                rf"{self.dset}_{self.job}_{self.sim}_{self.scale}_"
                rf"[0-9]+_{self.stitch}_{self.ring}_{self.conn}",
                job
            )
        ]

    def load_log(self, job_name):
        dfs = {"worker": pd.DataFrame(), "header": pd.DataFrame()}
        p = Path(f"{self.path_to_jobs}")
        for log_file in p.glob(f"{job_name}/results/node-*.log"):
            node_type = "header" if log_file.name == "node-0.log" else "worker"
            
            skiprows = [i for i, line in enumerate(open(log_file)) if line.startswith("timer")][0] \
                        if node_type == "header" else 0
            node_id = log_file.name.rstrip(".log")

            df = pd.read_csv(log_file, sep=" ", header=None, index_col=None, skiprows=skiprows)
            df.columns=["type", "component", "val"]

            df = df[df.type == "timer"][["component", "val"]]
            df.columns = ["component", node_id]
            df.set_index("component", inplace=True)

            dfs[node_type] = pd.concat([dfs[node_type], df], axis=1)

        for node_type, df in dfs.items():
            dfs[node_type] = df.stack().reset_index()
            dfs[node_type].columns = ["component", "node", "time"]

        return dfs

    def get_data(self):
        data = {"worker": [], "header": []}
        for job in self.get_vis_jobs():
            dfs = self.load_log(job)
            n_nodes = int(parse_job_name(job)["n_nodes"]) - 1

            df = dfs["worker"][["component", "time"]].groupby("component").mean().drop("do_tasks").reset_index()
            df["n_nodes"] = n_nodes
            data["worker"].append(df)

            df = dfs["header"][["component", "time"]].groupby("component").mean().drop(["run", "run_sim"]).reset_index()
            df["n_nodes"] = n_nodes
            data["header"].append(df)

        self.worker = pd.concat(data["worker"]).pivot(columns='component', index='n_nodes', values="time")
        self.header = pd.concat(data["header"]).pivot(columns='component', index='n_nodes', values="time")


    def plot(self, savefig=True):
        for node_type, data in {"worker": self.worker, "header": self.header}.items():
            ax = data.plot(
                kind='bar', 
                stacked=True,
                colormap=cm.rainbow_r,
                alpha=0.5
            )
            ax.set_title(
                f"{self.dset} {self.sim.title()} Forest Fire\n"
                f"Scale Factor: {self.scale}, Stitch: {self.stitch}, "
                f"Connectivity: {self.conn}, Ring: {self.ring}"
            )
            ax.set_xlabel("Number of Nodes")
            ax.set_ylabel("Time (s)")
            ax.legend(prop={'size': 9})
            # ax.set_yticks([0, 150, 300, 500, 1000, 1500, 2000, 2500])
            if savefig:
                plt.savefig(f"figures/{self.dset}_{self.job}_{self.sim}_"
                            f"{self.scale}_{self.stitch}_{self.ring}_{self.conn}_{node_type}.svg",
                            format='svg', dpi=300)
            else:
                plt.show()

if __name__ == "__main__":
    args = parse_args()
    tv = TimingVisiualizer(args.src, args.dset, args.job, args.sim, args.scale, args.stitch, args.ring, args.conn)
    tv.get_data()
    tv.plot(savefig=True)
