import argparse
import json
import numpy as np
import os

if __name__ == "__main__":
    # Script to compute used wallclocktime
    parser = argparse.ArgumentParser()
    parser.add_argument('--inp', required=True, type=str)
    args, unknown = parser.parse_known_args()

    # manually selected list
    benchs = ["ParamNetReducedAdultOnTimeBenchmark",
              "SliceLocalizationBenchmark",
              "NASCifar10ABenchmark",
              "Cifar100NasBench201Benchmark",
              "NASBench1shot1SearchSpace1Benchmark",
              ]

    time_unit = 60*60
    calls_unit = 1

    res_dc = {}
    table_header = []
    assert os.path.isdir(args.inp)

    for b in benchs:
        inp_path = os.path.join(args.inp, f"{b}/stats2_{b}_all.json")
        if not os.path.isfile(inp_path):
            print(f"Skipping {b}, {inp_path} does not exist")
            continue

        table_header.append(r"\multicolumn{2}{c}{%s}" % b)
        with open(inp_path) as fh:
            data = json.load(fh)

        for opt in data:
            if opt == "lowest_val": continue
            else:
                if opt not in res_dc: res_dc[opt] = []
                res_dc[opt].extend([
                    "%d & %d" % (int(np.rint(np.median(data[opt]["act_wc_time"])/time_unit)), int(np.rint(np.median(data[opt]["n_calls"])/calls_unit)))
                        ])

    print(r"\begin{tabular}{" + "l" + "r"*len(table_header)*2 + r"}")
    print(" & " + " & ".join(table_header) + r" \\")
    for opt in res_dc:
        print(f"{opt} & " + " & ".join(res_dc[opt]) + r" \\")
    print(r"\end{tabular}")
