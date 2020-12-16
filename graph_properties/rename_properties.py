import sys
import os
import json




new_properties_file_name = "all_properties_for_kgs.json"
new_properties = {}

if __name__ == "__main__":
    dirs = os.scandir(".")

    with open(new_properties_file_name, 'w') as new_file:
        graph_data = {}
        for sim in dirs:
            # import pdb
            # pdb.set_trace()
            if sim.is_dir():
                results = os.scandir(sim)
                for res in results:
                    if res.is_dir():
                        properites = os.scandir(res)
                        for prop in properites:
                            if prop.is_file():
                                # import pdb
                                # pdb.set_trace()
                                with open(prop.path) as f:
                                    file_data = json.load(f)
                                    graph_data[sim.name] = file_data
        json.dump(graph_data, new_file, ensure_ascii=False, indent=4)
