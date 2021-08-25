import os
import argparse
import itertools
from hpobench.util.openml_data_manager import get_openmlcc18_taskids


all_task_ids_by_in_mem_size = [
    10101, 53, 146818, 146821, 9952, 146822, 31, 3917, 168912, 3, 167119, 12, 146212, 168911,
    9981, 168329, 167120, 14965, 146606,  # < 30 MB
    168330, 7592, 9977, 168910, 168335, 146195, 168908, 168331,  # 30-100 MB
    168868, 168909, 189355, 146825, 7593,  # 100-500 MB
    168332, 168337, 168338,  # > 500 MB
    189354, 34539,  # > 2.5k MB
    3945,  # >20k MB
    # 189356  # MemoryError: Unable to allocate 1.50 TiB; array size (256419, 802853) of type float64
]

ntasks_done = dict(
    svm=30,
    lr=30,
    rf=30,
    xgb=30,
    nn=30
)

expset_dc = {
    "NAS201": ["Cifar10ValidNasBench201Benchmark", "Cifar100NasBench201Benchmark",
               "ImageNetNasBench201Benchmark"],
    "NAS101": ["NASCifar10ABenchmark", "NASCifar10BBenchmark", "NASCifar10CBenchmark"],
    "NASTAB": ["SliceLocalizationBenchmark", "ProteinStructureBenchmark",
               "NavalPropulsionBenchmark", "ParkinsonsTelemonitoringBenchmark", ],
    "NAS1SHOT1": ["NASBench1shot1SearchSpace1Benchmark", "NASBench1shot1SearchSpace2Benchmark",
                  "NASBench1shot1SearchSpace3Benchmark", ],
    "pybnn": ["BNNOnBostonHousing", "BNNOnProteinStructure", "BNNOnYearPrediction", ],
    "rl": ["cartpolereduced"],
    "learna": ["metalearna", "learna"],
    "paramnettime": ["ParamNetAdultOnTimeBenchmark", "ParamNetHiggsOnTimeBenchmark",
                     "ParamNetLetterOnTimeBenchmark", "ParamNetMnistOnTimeBenchmark",
                     "ParamNetOptdigitsOnTimeBenchmark", "ParamNetPokerOnTimeBenchmark", ],
    "paramnettimered": [
        "ParamNetReducedAdultOnTimeBenchmark", "ParamNetReducedHiggsOnTimeBenchmark",
        "ParamNetReducedLetterOnTimeBenchmark", "ParamNetReducedMnistOnTimeBenchmark",
        "ParamNetReducedOptdigitsOnTimeBenchmark", "ParamNetReducedPokerOnTimeBenchmark", ],
    "svmsurrogate": ["SurrogateSVMBenchmark", ],
    "svm": ["svm", ],
    "xgboostsub": ["xgboostsub", ],
    "xgboostest": ["xgboostest", ],
    "seeds": ["NASCifar10ABenchmark_fixed_seed_0", "NASCifar10ABenchmark_random_seed",
              "ProteinStructureBenchmark_fixed_seed_0", "ProteinStructureBenchmark_random_seed",
              "Cifar10ValidNasBench201Benchmark_fixed_seed_777", "Cifar10ValidNasBench201Benchmark_random_seed", ],
    "tabular_svm": [
        "{}_{}".format(x[0], x[1]) for x in itertools.product(
            *[["svm"], all_task_ids_by_in_mem_size[:ntasks_done["svm"]]]
        )
    ],
    "tabular_lr": [
        "{}_{}".format(x[0], x[1]) for x in itertools.product(
            *[["lr"], all_task_ids_by_in_mem_size[:ntasks_done["lr"]]]
        )
    ],
    "tabular_nn": [
        "{}_{}".format(x[0], x[1]) for x in itertools.product(
            *[["nn"], all_task_ids_by_in_mem_size[:ntasks_done["nn"]]]
        )
    ],
    "tabular_xgb": [
        "{}_{}".format(x[0], x[1]) for x in itertools.product(
            *[["xgb"], all_task_ids_by_in_mem_size[:ntasks_done["xgb"]]]
        )
    ],
    "tabular_rf": [
        "{}_{}".format(x[0], x[1]) for x in itertools.product(
            *[["rf"], all_task_ids_by_in_mem_size[:ntasks_done["rf"]]]
        )
    ],
}

opt_set = {
    "rs": ["randomsearch", ],
    "dehb": ["dehb", ],
    "hpband": ["hpbandster_bohb_eta_3", "hpbandster_hb_eta_3"],
    "smac": ["smac_hb_eta_3", "smac_sf"],
    "autogluon": ["autogluon", ],
    "dragonfly": ["dragonfly_default", ],
    "fabolas": ["fabolas_mtbo", "fabolas_mumbo"],
    "mumbo": ["mumbo", ],
    "sf": ["smac_bo", "hpbandster_tpe", "de"],
    "optuna": ["optuna_tpe_hb", "optuna_cmaes_hb", "optuna_tpe_median"],
    "ray": ["ray_hyperopt", "ray_randomsearch", "ray_hyperopt_asha"],
}


def main(args):
    exp = args.exp
    opt = args.opt
    nrep = args.nrep
    nworker = args.nworker

    if not os.path.isdir(args.out_cmd):
        os.mkdir(args.out_cmd)

    val_fl = "%s/val_%s_%s_%d.cmd" % (args.out_cmd, exp, opt, nrep)
    run_fl = "%s/run_%s_%s_%d.cmd" % (args.out_cmd, exp, opt, nrep)
    eval_fl = "%s/eval_%s.cmd" % (args.out_cmd, exp)
    evalu_fl = "%s/evalunv_%s.cmd" % (args.out_cmd, exp)

    run_cmd = []
    val_cmd = []
    eval_cmd = []
    evalu_cmd = []

    base = f"python {args.root}/HPOBenchExperimentUtils"

    for benchmark in expset_dc[exp]:
        for optimizer in opt_set[opt]:
            for seed in range(1, nrep + 1):
                if benchmark in ["svm", "xgboostsub", "xgboostest"]:
                    for tid in get_openmlcc18_taskids():
                        cmd = "%s/run_benchmark.py --output_dir %s --optimizer %s --benchmark %s" \
                              " --rng %s --task_id %d" % \
                              (base, args.out_run, optimizer, benchmark, seed, tid)
                        run_cmd.append(cmd)
                else:
                    cmd = "%s/run_benchmark.py --output_dir %s --optimizer %s --benchmark %s " \
                          "--rng %s" % (base, args.out_run, optimizer, benchmark, seed)
                    run_cmd.append(cmd)

        if opt == "rs":
            # We only need this once since it works for all optimizers
            cmd = f"{base}/evaluate_benchmark.py --output_dir {args.out_eval}/ --input_dir {args.out_run}/ --benchmark {benchmark} " \
                  "--agg median --what all"
            eval_cmd.append(cmd)
            cmd += " --unvalidated"
            evalu_cmd.append(cmd)

            # Do this only once
            if benchmark == expset_dc[exp][-1]:
                cmd = f"{base}/evaluate_benchmark.py --output_dir {args.out_eval}/ --input_dir {args.out_run}/ " \
                      f"--agg median --rank {exp}"
                eval_cmd.append(cmd)
                cmd += " --unvalidated"
                evalu_cmd.append(cmd)

            cmd = "%s/validate_benchmark.py start_scheduler --interface eno1 --recompute_all --benchmark %s " \
                  "--output_dir %s/%s --run_id %s --worker_id 0" % (base, benchmark, args.out_run, benchmark, benchmark)
            val_cmd.append(cmd)
            for i in range(nworker):
                cmd = "sleep 360; %s/validate_benchmark.py start_worker --interface eno1 --benchmark %s " \
                      "--output_dir %s/%s --run_id %s --worker_id %d" % (
                      base, benchmark, args.out_run, benchmark, benchmark, i + 1)
                val_cmd.append(cmd)

    for c, f in [[run_cmd, run_fl], [eval_cmd, eval_fl],
                 [evalu_cmd, evalu_fl], [val_cmd, val_fl]]:
        if len(c) > 0:
            write_cmd(c, f)


def write_cmd(cmd_list, out_fl):
    if len(cmd_list) > 10000:
        ct = 0
        while len(cmd_list) > 10000:
            write_cmd(cmd_list[:10000], out_fl + "_%d" % ct)
            ct += 1
            cmd_list = cmd_list[10000:]
    else:
        with open(out_fl, "w") as fh:
            fh.write("\n".join(cmd_list))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--exp', required=True, choices=expset_dc.keys())
    parser.add_argument('--opt', default="def", choices=opt_set.keys())
    parser.add_argument('--nrep', default=10, type=int)
    parser.add_argument('--out-run', default="./exp_outputs", type=str)
    parser.add_argument('--out-eval', default="./plots", type=str)
    parser.add_argument('--out-cmd', default=".", type=str)
    parser.add_argument('--root', default=".")
    parser.add_argument('--nworker', default=50)

    args, unknown = parser.parse_known_args()
    main(args)
