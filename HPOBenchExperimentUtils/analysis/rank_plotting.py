import logging
from pathlib import Path
from typing import Union, List

from HPOBenchExperimentUtils.utils.plotting_utils import plot_dc, color_per_opt, unify_layout, benchmark_dc, \
    export_legend, linestyle_per_opt
from HPOBenchExperimentUtils import _log as _main_log
from HPOBenchExperimentUtils.utils.validation_utils import load_json_files, load_trajectories_as_df
from HPOBenchExperimentUtils.utils.runner_utils import get_optimizer_setting, get_benchmark_settings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

_main_log.setLevel(logging.DEBUG)
_log = logging.getLogger(__name__)


exclude = [['SurrogateSVMBenchmark', 'autogluon'],
           ['SurrogateSVMBenchmark', 'optuna_tpe_hb'],
           ['SurrogateSVMBenchmark', 'optuna_cmaes_hb'],
           ['SurrogateSVMBenchmark', 'ray_hyperopt_asha'],

           ['SliceLocalizationBenchmark', 'optuna_cmaes_hb'],
           ['ProteinStructureBenchmark', 'optuna_cmaes_hb'],
           ['NavalPropulsionBenchmark', 'optuna_cmaes_hb'],
           ['ParkinsonsTelemonitoringBenchmark', 'optuna_cmaes_hb'],
           ]


def read_trajectories(benchmark: str, input_dir: Path, output_dir: Path, train: bool=True,
                      which: str="v1", opt_list: Union[List[str], None] = None, normalize_times_by=1):
    input_dir = Path(input_dir) / benchmark
    assert input_dir.is_dir(), f'Result folder doesn\"t exist: {input_dir}'

    unique_optimizer = load_trajectories_as_df(
        input_dir=input_dir, which=f'train_{which}' if train else f'test_{which}')
    optimizer_names = list(unique_optimizer.keys())
    if opt_list is None:
        opt_list = optimizer_names
    _log.critical("Found: " + ",".join(optimizer_names))
    if len(optimizer_names) == 0:
        raise ValueError("No files found")

    trajectories = []
    for key in opt_list:
        if [benchmark, key] in exclude:
            continue

        if key not in optimizer_names:
            raise ValueError(f"Not the same opts for all benchmarks; {benchmark} missed {key}")
        trs = load_json_files(unique_optimizer[key])
        series_list = []
        for t in trs:
            times = np.array([r["total_time_used"] for r in t[1:]]) / normalize_times_by
            vals = np.array([r["function_value"] for r in t[1:]])
            series_list.append(pd.Series(data=vals, index=times))
        series = pd.concat(series_list, axis=1)
        # Fill missing performance values (NaNs) with last non-NaN value.
        series = series.fillna(method='ffill')

        vali = -1
        nan_columns = []
        for c in series.columns:
            # exclude nan columns.
            first_valid_index = series[c].first_valid_index()
            if first_valid_index is None:
                missing_col = int(unique_optimizer[key][c].parent.name.lstrip('run-'))
                nan_columns.append(missing_col)
            else:
                vali = max(vali, first_valid_index)

        columns = [int(c) for c in np.setdiff1d(series.columns, nan_columns)]
        series = series.loc[vali:, columns]
        import logging
        logger = logging.getLogger()
        if len(nan_columns) != 0:
            ex_str = f'{benchmark} - {key} - {nan_columns}\n'
            logger.warning(ex_str)
            (output_dir / 'missing_columns.txt').write_text(ex_str)


        if normalize_times_by != 1:
            # Here we assume max timestep is 1 and we discretize 
            # because we're handling a large ranking plot
            steps = 10**np.linspace(-6, 0, 200)
            series = series.transpose()
            for step in steps:
                if step > 0:
                    series[step] = np.NaN
            a = series.sort_index(axis=1).ffill(axis=1)
            a = a.loc[:,steps]
            series = a
            series = series.transpose()
        trajectories.append(series)
    return trajectories


def plot_ranks(benchmarks: List[str], familyname: str, output_dir: Union[Path, str], 
               input_dir: Union[Path, str], opts: str, criterion: str = 'mean', unvalidated: bool = True,
               which: str = "v1", opt_list: Union[List[str], None] = None,  **kwargs):
    _log.info(f'Start plotting ranks of benchmarks {benchmarks}')

    if 'SliceLocalizationBenchmark' in benchmarks \
            or 'ProteinStructureBenchmark' in benchmarks \
            or 'NavalPropulsionBenchmark' in benchmarks \
            or 'ParkinsonsTelemonitoringBenchmark' in benchmarks:
        opt_list = [opt for opt in opt_list if opt != 'optuna_cmaes_hb']

    if 'SurrogateSVMBenchmark' in benchmarks:
        not_allowed = ['autogluon', 'optuna_tpe_hb', 'optuna_cmaes_hb', 'ray_hyperopt_asha'],
        opt_list = [opt for opt in opt_list if opt not in not_allowed]

    input_dir = Path(input_dir)
    assert input_dir.is_dir(), f'Result folder doesn\"t exist: {input_dir}'

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    benchmark_spec = plot_dc.get(benchmarks[0], {})
    benchmark_settings = get_benchmark_settings(benchmarks[0])



    all_trajectories = []
    horizon = []
    x_lo = []
    for b in benchmarks:
        benchmark_settings = get_benchmark_settings(b)
        tmp_horizon = benchmark_settings['time_limit_in_s']
        if familyname == "all":
            # we need to normalize time stamps and x-axis = fraction of budget
            normalize_times_by = tmp_horizon
            tmp_horizon = 1
        else:
            normalize_times_by = 1

        tr = read_trajectories(benchmark=b, input_dir=input_dir, train=unvalidated, which=which,
                               opt_list=opt_list, output_dir=output_dir, normalize_times_by=normalize_times_by)
        all_trajectories.append(tr)
        horizon.append(tmp_horizon)
        x_lo.append(benchmark_spec.get("xlim_lo", 1))
        
    assert len(set(horizon)) == 1
    horizon = int(horizon[0])
    _log.info(f"Handling horizon: {horizon}sec")
    x_lo = np.min(x_lo)

    # Step 2. Compute average ranks of the trajectories.
    #####################################################################################
    all_rankings = []
    n_tasks = len(benchmarks)
    paired = False

    n_iter = 5000
    if paired:
        n_iter = all_trajectories[0][0].shape[1]

    for i in range(n_iter):
        if i % 500 == 0: print("%d / %d" % (i, n_iter))
        for j in range(n_tasks):
            if paired:
                pick = np.ones(len(opt_list), dtype=np.int) * i
            else:
                # Allow different amount of runs per optimizers
                pick = [np.random.choice(all_trajectories[j][k].shape[1]) for k in range(len(opt_list))]
            all_trajectories_tmp = pd.DataFrame(
                {opt_list[k]: at.iloc[:, pick[k]] for
                 k, at in enumerate(all_trajectories[j])}
            )
            all_trajectories_tmp = all_trajectories_tmp.fillna(method='ffill', axis=0)
            # bottom: assign highest rank to NaN values if ascending
            r_tmp = all_trajectories_tmp.rank(axis=1, na_option="bottom")
            all_rankings.append(r_tmp)

    final_ranks = []
    for i, model in enumerate(opt_list):
        ranks_for_model = []
        for ranking in all_rankings:
            ranks_for_model.append(ranking.loc[:, model])
        ranks_for_model = pd.DataFrame(ranks_for_model)
        ranks_for_model = ranks_for_model.fillna(method='ffill', axis=1)
        if criterion == "mean":
            final_ranks.append(ranks_for_model.mean(skipna=True))
        elif criterion == "median":
            final_ranks.append(ranks_for_model.median(skipna=True))

    # Step 3. Plot the average ranks over time.
    ######################################################################################
    f, ax = plt.subplots(1, 1)
    for i, key in enumerate(opt_list):
        X_data = []
        y_data = []
        for x, y in final_ranks[i].iteritems():
            X_data.append(x)
            y_data.append(y)
        X_data.append(horizon)
        X_data = np.array(X_data)
        y_data.append(y)
        plt.plot(X_data, y_data, label=get_optimizer_setting(key).get("display_name", key),
                 linestyle=linestyle_per_opt.get(key, 'solid'),
                 c=color_per_opt.get(key, "k"),
                 linewidth=2)
    if benchmark_settings["is_surrogate"]:
        plt.xlabel("Simulated runtime in seconds")
    else:
        plt.xlabel("Runtime in seconds")

    if familyname == "all":
        plt.xlabel("Fraction of budget")
        ax.set_xlim([10**-6, 1])
    else:
        ax.set_xlim([x_lo, horizon])
    ax.set_xscale(benchmark_spec.get("xscale", "log"))
    ax.set_ylabel(f"{criterion.capitalize()} rank")
    ax.set_ylim([0.9, len(opt_list)+0.1])
    

    unify_layout(ax, title=None, add_legend=False)
    val_str = 'optimized' if unvalidated else 'validated'
    plt.tight_layout()
    filename = Path(output_dir) / f'ranks_{familyname}_{val_str}_{which}_{opts}.png'
    plt.savefig(filename)

    legend_file = filename.parent / (filename.name.rstrip('png').rstrip('.') + '_legend.png')
    export_legend(ax, legend_file)

    plt.close('all')
    return 1


def plot_ecdf_per_family(benchmarks: List[str], familyname: str, output_dir: Union[Path, str], 
                         input_dir: Union[Path, str], opt_list: Union[List[str], None] = None, **kwargs):
    _log.info(f'Start plotting ECDFs for benchmark family {familyname}')

    input_dir = Path(input_dir)
    assert input_dir.is_dir(), f'Result folder doesn\"t exist: {input_dir}'

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    benchmark_spec = plot_dc.get(benchmarks[0], {})
    benchmark_settings = get_benchmark_settings(benchmarks[0])

    def ecdf(x):
        xs = np.sort(x)
        ys = np.arange(1, len(xs) + 1) / float(len(xs))
        return xs, ys

    plt.figure(figsize=[5, 5])
    a = plt.subplot(111)
    max_ = -1
    min_ = 1000
    for benchmark, color in zip(benchmarks, ['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#ffff33']):
        tmp_input_dir = Path(input_dir) / benchmark
        assert tmp_input_dir.is_dir(), f'Result folder doesn\"t exist: {tmp_input_dir}'

        unique_optimizer = load_trajectories_as_df(
            input_dir=tmp_input_dir, which=f'runhistory')
        optimizer_names = list(unique_optimizer.keys())
        if "randomsearch" not in optimizer_names:
            raise ValueError("Results for randomsearch not found")

        benchmark_spec = plot_dc.get(benchmark, {})
        y_best = benchmark_spec.get("ystar_valid", 0)
        
        trs = load_json_files(unique_optimizer["randomsearch"])
        values = []
        for t in trs:
            vals = [r["function_value"] for r in t[1:]]
            values.extend(vals)
        values = np.array(values) - y_best
        x, y = ecdf(values)
        max_ = max(max_, max(values))
        min_ = min(min_, min(values))
        plt.plot(x, y, c=color, linewidth=3, label=benchmark_dc[benchmark],
                 linestyle=linestyle_per_opt.get(benchmark, 'solid'))


    if y_best != 0:
        plt.xlabel("Optimization Regret")
    else:
        plt.xlabel("Optimization objective value")
    plt.ylabel("P(x < X)")
    yscale = benchmark_spec.get("yscale", "log")
    plt.xscale(yscale)
    if max_ > 10**3:
        plt.xlim([min_*0.9, 10**3])
    #plt.ylim([-0.5, 1.05])
    #yt = plt.yticks()
    #a.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    #a.set_yticklabels([0, 0.2, 0.4, 0.6, 0.8, 1.0])

    unify_layout(a)
    plt.tight_layout()
    plt.savefig(Path(output_dir) / f'ecdf_random_{familyname}.png')