"""
Script to generate the LaTex table with final performances for the chose optimizer families
"""

import sys
import time
import logging
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import rankdata
from typing import Union, List
import matplotlib.pyplot as plt

from HPOBenchExperimentUtils.utils.runner_utils import get_benchmark_names, get_benchmark_settings
from HPOBenchExperimentUtils.analysis.trajectory_plotting import plot_trajectory
from HPOBenchExperimentUtils.analysis.stats_generation import plot_fidels, plot_overhead, \
    plot_ecdf, plot_correlation, get_stats
from HPOBenchExperimentUtils.analysis.table_generation import save_median_table
from HPOBenchExperimentUtils.analysis.rank_plotting import plot_ranks, plot_ecdf_per_family
from HPOBenchExperimentUtils import _log as _root_log
from HPOBenchExperimentUtils.utils.plotting_utils import plot_dc, color_per_opt, unify_layout, \
    benchmark_dc, benchmark_families
from HPOBenchExperimentUtils.utils.validation_utils import load_json_files, \
    load_trajectories_as_df, df_per_optimizer

from utils.util import tasks_available, ntasks_done

_root_log.setLevel(logging.DEBUG)
_log = logging.getLogger(__name__)


def write_latex(result_df, output_file, col_list):
    replace_dc = {
        '\\{': "{",
        "\\}": "}",
        "textbf": "\\textbf",
        "underline": "\\underline",
        'xgboostsub': r"\xgboostfrac",
        'xgboostest': r"\xgboostnest",
        'cartpolereduced': r"\cartpole",
        "cartpolefull": "%cartpolefull",
        'BNNOnBostonHousing': r"\bnnboston",
        'BNNOnProteinStructure': r"\bnnprotein",
        'BNNOnYearPrediction': r"\bnnyear",
        'learna': r"\learna",
        'NASCifar10ABenchmark': r"\NASA",
        'NASCifar10BBenchmark': r"\NASB",
        'NASCifar10CBenchmark': r"\NASC",
        'SliceLocalizationBenchmark': r"\slice",
        'ProteinStructureBenchmark': r"\protein",
        'NavalPropulsionBenchmark': r"\naval",
        'ParkinsonsTelemonitoringBenchmark': r"\parkinson",
        'Cifar10NasBench201Benchmark': r"%\nbcifart",
        'Cifar10ValidNasBench201Benchmark': r"\nbcifartv",
        'Cifar100NasBench201Benchmark': r"\nbcifarh",
        'ImageNetNasBench201Benchmark': r"\nbimage",
        "SurrogateSVMBenchmark": r"\nsvmsurro",
        "ParamNetReducedAdultOnTimeBenchmark": r"\paramadult",
        "ParamNetReducedHiggsOnTimeBenchmark": r"\paramhiggs",
        "ParamNetReducedLetterOnTimeBenchmark": r"\paramletter",
        "ParamNetReducedMnistOnTimeBenchmark": r"\parammnist",
        "ParamNetReducedOptdigitsOnTimeBenchmark": r"\paramoptdigits",
        "ParamNetReducedPokerOnTimeBenchmark": r"\parampoker",
        "NASBench1shot1SearchSpace1Benchmark": r"\NASOSOA",
        "NASBench1shot1SearchSpace2Benchmark": r"\NASOSOB",
        "NASBench1shot1SearchSpace3Benchmark": r"\NASOSOC",
        "tabular_svm": r"\svm",
        "tabular_lr": r"\lr",
        "tabular_rf": r"\rf",
        "tabular_xgb": r"\xgb",
        "tabular_nn": r"\mlp",
    }
    with open(output_file, 'w') as fh:
        latex = result_df.to_latex(index_names=False, index=False, columns=["benchmark"] + col_list)
        for i in replace_dc:
            latex = latex.replace(i, replace_dc[i])
        print(latex)
        fh.write(latex)


def df_per_optimizer(key, unvalidated_trajectories, y_best: float=0, y_max=None):
    if y_best != 0:
        _log.info("Found y_best = %g; Going to compute regret" % y_best)
    _log.info("Creating DataFrame for %d inputs" % len(unvalidated_trajectories))
    dataframe = {
        "optimizer": [],
        "id": [],
        "total_time_used": [],
        "total_objective_costs": [],
        "function_values": [],
        "fidel_values": [],
        "costs": [],
        "start_time": [],
        "finish_time": [],
    }

    normalizer = 1 if y_max is None else y_max - y_best

    for id, traj in enumerate(unvalidated_trajectories):
        _log.info("Handling input with %d records for %s" % (len(traj), key))
        function_values = [(record['function_value']-y_best) / normalizer for record in traj[1:]]
        total_time_used = [record['total_time_used'] for record in traj[1:]]
        total_obj_costs = [record['total_objective_costs'] for record in traj[1:]]
        costs = [record['cost'] for record in traj[1:]]
        start = [record['start_time'] for record in traj[1:]]
        finish = [record['finish_time'] for record in traj[1:]]

        # this is a dict with only one entry
        fidel_values = [record['fidelity'][list(record['fidelity'])[0]] for record in traj[1:]]

        dataframe["optimizer"].extend([key for _ in range(len(traj[1:]))])
        dataframe["id"].extend([id for _ in range(len(traj[1:]))])
        dataframe['total_time_used'].extend(total_time_used)
        dataframe['total_objective_costs'].extend(total_obj_costs)
        dataframe['function_values'].extend(function_values)
        dataframe['fidel_values'].extend(fidel_values)
        dataframe['costs'].extend(costs)
        dataframe['start_time'].extend(start)
        dataframe['finish_time'].extend(finish)

    dataframe = pd.DataFrame(dataframe)
    return dataframe


def save_median_table_tabular(
        benchmark: str, output_dir: Union[Path, str], input_dir: Union[Path, str],
        unvalidated: bool = True, which: str = "v1", opt_list: Union[List[str], None] = None,
        thresh=1, **kwargs
):
    assert 0 < thresh <= 1, f"thresh needs to be in [0, 1], but is {thresh}"

    if kwargs["tabular"] is None:
        benchmarks = []
        for model in ntasks_done.keys():
            benchmarks.extend(benchmark_families["tabular_{}".format(model)])
    else:
        benchmarks = benchmark_families["tabular_{}".format(kwargs["tabular"])]

    def check_task_id(benchmark_name):
        model, tid = benchmark_name.split("_")
        if int(tid) in tasks_available(model):
            return True
        return False

    benchmarks = [name for name in benchmarks if check_task_id(name)]
    if args.bench_type != "tab":
        benchmarks = ["{}_{}".format(name, args.bench_type) for name in benchmarks]

    orig_input_dir = input_dir
    per_dataset_df = dict()
    for benchmark in benchmarks:
        _log.info(f'Start creating table of benchmark {benchmark}')
        input_dir = Path(orig_input_dir) / benchmark
        # assert input_dir.is_dir(), f'Result folder doesn\"t exist: {input_dir}'
        if not input_dir.is_dir():
            print(f'Result folder doesn\"t exist: {input_dir}')
            # continue
        unique_optimizer = load_trajectories_as_df(input_dir=input_dir,
                                                   which=f'train_{which}' if unvalidated else
                                                   f'test_{which}')
        benchmark_spec = plot_dc.get(benchmark, {})
        y_best_val = benchmark_spec.get("ystar_valid", 0)
        y_best_test = benchmark_spec.get("ystar_test", 0)
        y_max = benchmark_spec.get("y_max", 0)
        benchmark_settings = get_benchmark_settings(benchmark)
        time_limit_in_s = benchmark_settings["time_limit_in_s"]
        cut_time_step = thresh * time_limit_in_s
        _log.info(f"Cut to {thresh} percent -> {time_limit_in_s} sec")

        keys = list(unique_optimizer.keys())
        if opt_list is None:
            opt_list = keys
        result_df = pd.DataFrame()
        for key in opt_list:
            if key not in keys:
                _log.info(f'Skip {key}')
                continue
            trajectories = load_json_files(unique_optimizer[key])
            optimizer_df = df_per_optimizer(
                key=key,
                unvalidated_trajectories=trajectories,
                y_best=y_best_val if unvalidated else y_best_test,
                y_max=y_max
            )

            unique_ids = np.unique(optimizer_df['id'])
            for unique_id in unique_ids:
                df = optimizer_df[optimizer_df['id'] == unique_id]
                df2 = pd.DataFrame(
                    [[
                        key, unique_id, 0, 0, np.inf, df["fidel_values"].max(), 0, 0, 1
                    ], ], columns=df.columns
                )
                df = df.append(df2, ignore_index=True)
                df = df.sort_values(by='total_time_used')
                df = df.drop(df[df["total_time_used"] > cut_time_step].index)
                last_inc = df.tail(1)
                if len(last_inc) < 1:
                    print(unique_id)
                    print(f"{key} has not enough runs at timestep {cut_time_step}")
                    # _log.critical(f"{key} has not enough runs at timestep {cut_time_step}")

                result_df = result_df.append(last_inc)

        def q1(x):
            return x.quantile(0.25)

        def q3(x):
            return x.quantile(0.75)

        def lst(x):
            x = np.array(x)
            #x[x < 1e-6] = 1e-6
            return list(x)

        def median(x):
            x = np.array(x)
            #x[x < 1e-6] = 1e-6
            return np.median(x)

        # q1 = lambda x: x.quantile(0.25)
        # q3 = lambda x: x.quantile(0.75)
        aggregate_funcs = [median, q1, q3, lst]
        result_df = result_df.groupby('optimizer').agg(
            {'function_values': aggregate_funcs, 'total_time_used': ['median']}
        )
        result_df.columns = ["_".join(x) for x in result_df.columns.ravel()]
        result_df["value_lst_len"] = [len(v) for v in result_df.function_values_lst.values]
        per_dataset_df[benchmark] = result_df

    result_df = []
    for benchmark in per_dataset_df.keys():
        result_df.append(per_dataset_df[benchmark].function_values_median)
    for i in range(1, len(result_df)):
        result_df[0] = result_df[0] + result_df[i]
    result_df = result_df[0] / len(result_df)
    result_df = pd.DataFrame(result_df, columns=["function_values_median"])

    # Computing ranks
    _result_df = result_df.transpose.copy()
    rank_df = pd.DataFrame(
        [rankdata(_result_df.values, method="ordinal")], columns=_result_df.columns
    )

    # Compute some statistics
    opt_keys = list(result_df.index)
    opt_keys.sort()

    # get best optimizer
    best_opt = opt_keys[result_df["function_values_median"].argmin()]

    for opt in opt_keys:
        val = result_df["function_values_median"][opt]

        if args.formatter == "orig":
            if val < 1e-3:
                val = "%.2e" % val
            else:
                val = "%.3g" % np.round(val, 3)
        else:
            # val = np.format_float_scientific(val, precision=2)
            val = "%.5f" % np.round(val, 5)

        if opt == best_opt:
            val = r"textbf{{{}}}".format(val)
        result_df.loc[opt, "value"] = val

    # select final cols
    result_df['optimizer'] = result_df.index
    result_df = result_df[["value"]]
    result_df = result_df.transpose()
    result_df["benchmark"] = "tabular_{}".format(kwargs["tabular"])

    header = ["benchmark"] + opt_keys
    result_df = result_df[header]

    val_str = 'unvalidated' if unvalidated else 'validated'
    rank_df.to_pickle(
        Path(output_dir) / f'result_table_tabular_{kwargs["tabular"]}_{val_str}_{which}_{args.table_type}_{args.formatter}.pkl'
    )
    print(rank_df)
    if thresh < 1:
        ouptut_file = Path(output_dir) / f'result_table_tabular_{kwargs["tabular"]}_{val_str}_{which}_{int(thresh*100)}_{args.formatter}.tex'
    else:
        output_file = Path(output_dir) / f'result_table_tabular_{kwargs["tabular"]}_{val_str}_{which}_{args.table_type}_{args.formatter}.tex'
    write_latex(result_df=result_df, output_file=output_file, col_list=opt_list)


def save_median_table_tabular_expanded(
        benchmark: str, output_dir: Union[Path, str], input_dir: Union[Path, str],
        unvalidated: bool = True, which: str = "v1", opt_list: Union[List[str], None] = None,
        thresh=1, **kwargs
):

    assert 0 < thresh <= 1, f"thresh needs to be in [0, 1], but is {thresh}"

    if kwargs["tabular"] is None:
        benchmarks = []
        for model in ntasks_done.keys():
            benchmarks.extend(benchmark_families["tabular_{}".format(model)])
    else:
        benchmarks = benchmark_families["tabular_{}".format(kwargs["tabular"])]

    def check_task_id(benchmark_name):
        model, tid = benchmark_name.split("_")
        if int(tid) in tasks_available(model):
            return True
        return False

    benchmarks = [name for name in benchmarks if check_task_id(name)]
    if args.bench_type != "tab":
        benchmarks = ["{}_{}".format(name, args.bench_type) for name in benchmarks]

    # _log.info(f'Start creating table of benchmark {benchmark}')
    orig_input_dir = input_dir
    per_dataset_df = dict()
    for i, benchmark in enumerate(benchmarks, start=1):
        print("\n{:<2}/{:<2}\n".format(i, len(benchmarks)))
        # time.sleep(1)
        # assert input_dir.is_dir(), f'Result folder doesn\"t exist: {input_dir}'
        input_dir = Path(orig_input_dir) / benchmark
        if not input_dir.is_dir():
            print(f'Result folder doesn\"t exist: {input_dir}')
        unique_optimizer = load_trajectories_as_df(input_dir=input_dir,
                                                   which=f'train_{which}' if unvalidated else
                                                   f'test_{which}')
        benchmark_spec = plot_dc.get(benchmark, {})
        y_best_val = benchmark_spec.get("ystar_valid", 0)
        y_best_test = benchmark_spec.get("ystar_test", 0)
        y_max = benchmark_spec.get("y_max", 0)
        benchmark_settings = get_benchmark_settings(benchmark)
        time_limit_in_s = benchmark_settings["time_limit_in_s"]
        cut_time_step = thresh * time_limit_in_s
        _log.info(f"Cut to {thresh} percent -> {time_limit_in_s} sec")

        keys = list(unique_optimizer.keys())
        if opt_list is None:
            opt_list = keys
        result_df = pd.DataFrame()
        for key in opt_list:
            if key not in keys:
                _log.info(f'Skip {key}')
                continue
            trajectories = load_json_files(unique_optimizer[key])
            optimizer_df = df_per_optimizer(
                key=key,
                unvalidated_trajectories=trajectories,
                y_best=y_best_val if unvalidated else y_best_test,
                y_max=y_max
            )

            unique_ids = np.unique(optimizer_df['id'])
            for unique_id in unique_ids:
                df = optimizer_df[optimizer_df['id'] == unique_id]
                df2 = pd.DataFrame([[key, unique_id, 0, 0, np.inf, df["fidel_values"].max(), 0, 0, 1], ], columns=df.columns)
                df = df.append(df2, ignore_index=True)
                df = df.sort_values(by='total_time_used')
                df = df.drop(df[df["total_time_used"] > cut_time_step].index)
                last_inc = df.tail(1)
                if len(last_inc) < 1:
                    _log.critical(f"{key} has not enough runs at timestep {cut_time_step}")

                result_df = result_df.append(last_inc)

        def q1(x):
            return x.quantile(0.25)

        def q3(x):
            return x.quantile(0.75)

        def lst(x):
            x = np.array(x)
            #x[x < 1e-6] = 1e-6
            return list(x)

        def median(x):
            x = np.array(x)
            #x[x < 1e-6] = 1e-6
            return np.median(x)

        # q1 = lambda x: x.quantile(0.25)
        # q3 = lambda x: x.quantile(0.75)
        aggregate_funcs = [median, q1, q3, lst]
        result_df = result_df.groupby('optimizer').agg({'function_values': aggregate_funcs,
                                                        'total_time_used': ['median']})
        result_df.columns = ["_".join(x) for x in result_df.columns.ravel()]
        result_df["value_lst_len"] = [len(v) for v in result_df.function_values_lst.values]
        per_dataset_df[benchmark] = result_df

    # Collating into a DataFrame
    _dfs = {k: per_dataset_df[k]["function_values_median"] for k in per_dataset_df.keys()}
    result_df_complete = pd.DataFrame.from_dict(_dfs).transpose()[opt_list]

    # Compute some statistics
    for i in range(result_df_complete.shape[0]):
        result_df = result_df_complete.iloc[i]
        opt_keys = list(result_df.index)
        opt_keys.sort()

        # get best optimizer
        # best_opt = result_df.index[result_df.values.argmin()]
        best_idxs = np.where(result_df.values == result_df.min())[0]
        best_opts = result_df.index[best_idxs]
        # best_opt_ls = [best_opt, ]
        # best_val = np.array(result_df["function_values_lst"][best_opt])
        # best_val = np.array(per_dataset_df[result_df.name]["function_values_lst"][best_opt])
        # _log.info(f"{best_opt} is the best optimizer; found {len(best_val)} runs")
        # not_worse = []
        # for opt in opt_keys:
        #     if opt == best_opt:
        #         continue
        #     opt_val = np.array(per_dataset_df[result_df.name]["function_values_lst"][opt])
        #     if not len(opt_val) == len(best_val):
        #         _log.warning(
        #             f"There are not {len(best_val)} but {len(opt_val)} repetitions for {opt}")
        #         continue
        #
        #     if np.sum(best_val - opt_val) == 0:
        #         # Results are identical
        #         best_opt_ls.append(opt)
        #     else:
        #         # The two-sided test has the null hypothesis that the median of the differences is zero
        #         # against the alternative that it is different from zero.
        #         s, p = scst.wilcoxon(best_val, opt_val, alternative="two-sided")
        #         if p > 0.05:
        #             not_worse.append(opt)

        for opt in opt_keys:
            val = result_df[opt]

            if val < 1e-3:
                val = "%.2e" % val
            else:
                val = "%.3g" % np.round(val, 3)

            if opt in best_opts:
                # val = r"underline{textbf{%s}}" % val
                val = r"textbf{%s}" % val
            # elif opt in not_worse:
            #     val = r"underline{%s}" % val

            result_df[opt] = val

        result_df_complete.iloc[i] = result_df

    filename = "{}_{}_{}".format(args.tabular, args.table_type, args.thresh)
    latex = result_df_complete.to_latex()
    latex = latex.replace("\\}", "}")
    latex = latex.replace("\\{", "{")
    latex = latex.replace("textbf", "\\textbf")
    latex = latex.replace("underline", "\\underline")
    with open(Path(output_dir) / "{}.tex".format(filename), "w") as f:
        f.writelines(latex)
    result_df_complete.to_pickle(Path(output_dir) / "{}.pkl".format(filename))

    return


def input_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_dir', type=str,
                        default="/work/dlclarge1/mallik-hpobench/opt-results/aug2022/")
    parser.add_argument('--input_dir', type=str,
                        default="/work/dlclarge1/mallik-hpobench/opt-results/runs/")
    parser.add_argument('--benchmark', choices=get_benchmark_names(), type=str, default=None)
    parser.add_argument('--what', choices=["all", "best_found", "over_time", "other",
                                           "ecdf", "correlation", "stats"], default="best_found")
    parser.add_argument('--rank', choices=benchmark_families.keys(), default=None)
    parser.add_argument('--agg', choices=["mean", "median"], default="median")
    parser.add_argument('--unvalidated', action='store_true', default=False)
    parser.add_argument('--which', choices=["v1", "v2"], default="v1")
    parser.add_argument('--tabular', choices=["svm", "lr", "rf", "xgb", "nn"], default=None)
    parser.add_argument('--table_type', choices=opt_list.keys(),
                        default="table3")
    parser.add_argument('--bench_type', choices=["tab", "raw", "surr"], type=str,
                        default="tab", help="type of benchmark")
    parser.add_argument('--formatter', choices=["orig", "numpy"],
                        default="orig")
    parser.add_argument('--expand', action="store_true", default=False)
    parser.add_argument('--thresh', default=1.0, type=float, help="fraction of budget")
    args, unknown = parser.parse_known_args()
    return args


if __name__ == "__main__":
    opt_list = dict()
    opt_list['main_sf'] = ['randomsearch', 'de', 'smac_bo', 'smac_sf', #'ray_hyperopt',
                           'hpbandster_tpe']
    opt_list['main_mf'] = ['hpbandster_hb_eta_3', 'hpbandster_bohb_eta_3', 'dehb',
                           'smac_hb_eta_3', 'dragonfly_default',
                           #'ray_hyperopt_asha'
                           ]  # no 'optuna_tpe_median' and 'optuna_tpe_hb'

    # lists for the main paper
    opt_list['table3'] = opt_list['main_sf'] + opt_list['main_mf']  # table
    opt_list['fig4_sf'] = opt_list['main_sf']  # ranking across all benchs
    opt_list['fig4_mf'] = opt_list['main_mf']  # ranking across all benchs
    opt_list['fig5bohb'] = ['randomsearch', 'hpbandster_tpe', 'hpbandster_hb_eta_3',
                            'hpbandster_bohb_eta_3']  # ranking across all benchs
    opt_list['fig5dehb'] = ['randomsearch', 'de', 'hpbandster_hb_eta_3',
                            'dehb']  # ranking across all benchs
    opt_list['fig5all'] = opt_list['main_sf'] + opt_list['main_mf']

    # lists for the appendix
    opt_list['all_sf'] = ['randomsearch', 'de', 'smac_bo', 'smac_sf', #'ray_hyperopt',
                          'hpbandster_tpe', 'hebo']  # table + trajectory per bench + ranking per bench
    opt_list['all_mf'] = ['hpbandster_hb_eta_3', 'hpbandster_bohb_eta_3', 'dehb', 'smac_hb_eta_3',
                          'dragonfly_default',
                          #'ray_hyperopt_asha',
                          'optuna_tpe_median',
                          'optuna_tpe_hb']  # table + trajectory per bench + ranking per bench
    opt_list['all_all'] = opt_list['all_sf'] + opt_list['all_mf']
    args = input_args()

    list_of_opts = opt_list[args.table_type]
    if args.tabular == "svm" and "optuna_tpe_hb" in list_of_opts:
        list_of_opts.remove("optuna_tpe_hb")

    if args.expand:
        save_median_table_tabular_expanded(**vars(args), opt_list=list_of_opts)
    else:
        save_median_table_tabular(**vars(args), opt_list=list_of_opts)
