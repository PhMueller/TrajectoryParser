import argparse
import json
import numpy as np
import os


# manually selected list
benchs_list = {
"raw": ["cartpolereduced", "BNNOnProteinStructure", "BNNOnYearPrediction"],
"surro": ["ParamNetReducedAdultOnTimeBenchmark", "ParamNetReducedHiggsOnTimeBenchmark",
    "ParamNetReducedLetterOnTimeBenchmark", "ParamNetReducedMnistOnTimeBenchmark",
    "ParamNetReducedOptdigitsOnTimeBenchmark", "ParamNetReducedPokerOnTimeBenchmark",
    "Cifar10ValidNasBench201Benchmark", "Cifar100NasBench201Benchmark",
    "ImageNetNasBench201Benchmark", "NASCifar10ABenchmark", "NASCifar10BBenchmark", "NASCifar10CBenchmark",
    "SliceLocalizationBenchmark", "ProteinStructureBenchmark",
    "NavalPropulsionBenchmark", "ParkinsonsTelemonitoringBenchmark",
    "NASBench1shot1SearchSpace1Benchmark", "NASBench1shot1SearchSpace2Benchmark",
    "NASBench1shot1SearchSpace3Benchmark",
    ]
}

if __name__ == "__main__":
    # Script to compute used wallclocktime
    parser = argparse.ArgumentParser()
    parser.add_argument('--inp', required=True, type=str)
    args, unknown = parser.parse_known_args()

    time_unit = 60*60

    for lsname in benchs_list:
        print("*"*80)
        print(lsname)
        print("*"*80)

        res_dc = {}
        table_header = []
        assert os.path.isdir(args.inp)

        for b in benchs_list[lsname]:
            inp_path = os.path.join(args.inp, f"{b}/stats2_{b}_all.json")
            if not os.path.isfile(inp_path):
                print(f"Skipping {b}, {inp_path} does not exist")
                continue

            table_header.append(r"\multicolumn{2}{1}{%s}" % b)
            with open(inp_path) as fh:
                data = json.load(fh)

            for opt in data:
                if opt == "lowest_val": continue
                if opt in ("autogluon", "ray_randomsearch"): continue
                else:
                    if opt not in res_dc: res_dc[opt] = 0
                    res_dc[opt] += np.sum(data[opt]["act_wc_time"])

        for opt in res_dc:
            print("%s: %d" % (opt, np.rint(res_dc[opt])/time_unit))

        print("Total:", np.sum([res_dc[i] for i in res_dc])/time_unit/24/365, "CPU years")
