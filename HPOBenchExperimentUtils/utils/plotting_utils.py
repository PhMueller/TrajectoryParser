import yaml
from pathlib import Path
import matplotlib.pyplot as plt

plot_dc = {
    "BNNOnBostonHousing": {
        # BOHB paper
        "xlim_lo": 10**2,
        "ylim_lo": 3,
        "ylim_up": 8,
        "cylim": [0.1, 1.1],
        "xscale": "log",
        "yscale": "linear",
        # None yet
        "ystar_valid": 0,
        "ystar_test": 0,
    },
    "BNNOnProteinStructure": {
        "xlim_lo": 10**2,
        "ylim_lo": 3,
        "ylim_up": 5,
        "cylim": [0.1, 1.1],
        "xscale": "log",
        "yscale": "linear",
        # None yet
        "ystar_valid": 0,
        "ystar_test": 0,
    },
    "BNNOnYearPrediction": {
        "xlim_lo": 10**2,
        "ylim_lo": 2,
        "ylim_up": 40,
        "cylim": [0.1, 1.1],
        "xscale": "log",
        "yscale": "linear",
        # None yet
        "ystar_valid": 0,
        "ystar_test": 0,
    },
    "cartpolereduced": {
        "xlim_lo": 10**2,
        "ylim_lo": 10**2,
        "ylim_up": 10**3.5,
        "xscale": "log",
        "yscale": "log",
        "cylim": [0.5, 1.1],
        # None yet
        "ystar_valid": 0,
        "ystar_test": 0,
    },
    "SliceLocalizationBenchmark": {
        "xlim_lo": 10**0,
        "ylim_lo": 10**-6,
        "ylim_up": 10**0,
        "xscale": "log",
        "yscale": "log",
        # from hpobench.benchmarks.nas.tabular_benchmarks import SliceLocalizationBenchmark
        # import numpy as np
        # bench = SliceLocalizationBenchmark(rng=1, data_path=<path>)
        #
        # configs, te, ve = [], [], []
        # for k in bench.benchmark.data.keys():
        #     t = bench.benchmark.data[k]["final_test_error"]
        #     t = [float(i) for i in t]
        #     te.append(np.sum(t) / len(t))
        #     v = bench.benchmark.data[k]["valid_mse"][:, -1]
        #     v = [float(i) for i in v]
        #     ve.append(np.sum(v) / len(v))
        #
        # best_test = np.min(te)
        # best_valid = np.min(ve)
        "ystar_valid": 0.00019159916337230243, #0.00020406871,
        "ystar_test": 0.0001442820794181898,
    },
    "ProteinStructureBenchmark": {
        "xlim_lo": 10**0,
        "ylim_lo": 10**-4,
        "ylim_up": 10**0,
        "xscale": "log",
        "yscale": "log",
        # from hpobench.benchmarks.nas.tabular_benchmarks import ProteinStructureBenchmark
        # import numpy as np
        # bench = ProteinStructureBenchmark(rng=1, data_path=<path>)
        #
        # configs, te, ve = [], [], []
        # for k in bench.benchmark.data.keys():
        #     t = bench.benchmark.data[k]["final_test_error"]
        #     # do this to be consistent w/ HPOBench and tabular_nas code
        #     te.append(float(np.mean(t)))
        #     v = bench.benchmark.data[k]["valid_mse"][:, -1]
        #     v = [float(i) for i in v]
        #     ve.append(np.sum(v) / len(v))
        #
        # best_test = np.min(te)
        # best_valid = np.min(ve)
        "ystar_valid": 0.221378855407238, #0.22137885,
        "ystar_test": 0.21536806225776672,
    },
    "NavalPropulsionBenchmark": {
        "xlim_lo": 10**0,
        "ylim_lo": 10**-6,
        "ylim_up": 10**0,
        "xscale": "log",
        "yscale": "log",
        # from hpobench.benchmarks.nas.tabular_benchmarks import NavalPropulsionBenchmark
        # import numpy as np
        # bench = NavalPropulsionBenchmark(rng=1, data_path=<path>)
        #
        # configs, te, ve = [], [], []
        # for k in bench.benchmark.data.keys():
        #     t = bench.benchmark.data[k]["final_test_error"]
        #     # do this to be consistent w/ HPOBench and tabular_nas code
        #     te.append(float(np.mean(t)))
        #     v = bench.benchmark.data[k]["valid_mse"][:, -1]
        #     v = [float(i) for i in v]
        #     ve.append(np.sum(v) / len(v))
        #
        # best_test = np.min(te)
        # best_valid = np.min(ve)
        "ystar_valid": 3.19113473778998e-05, #3.1911346e-05,
        "ystar_test": 2.91102915070951e-05
    },
    "ParkinsonsTelemonitoringBenchmark": {
        "xlim_lo": 10**0,
        "ylim_lo": 10**-4,
        "ylim_up": 10**-0,
        "xscale": "log",
        "yscale": "log",
        # from hpobench.benchmarks.nas.tabular_benchmarks import ParkinsonsTelemonitoringBenchmark
        # import numpy as np
        # bench = ParkinsonsTelemonitoringBenchmark(rng=1, data_path=<path>)
        #
        # configs, te, ve = [], [], []
        # for k in bench.benchmark.data.keys():
        #     t = bench.benchmark.data[k]["final_test_error"]
        #     # do this to be consistent w/ HPOBench and tabular_nas code
        #     te.append(float(np.mean(t)))
        #     v = bench.benchmark.data[k]["valid_mse"][:, -1]
        #     v = [float(i) for i in v]
        #     ve.append(np.sum(v) / len(v))
        #
        # best_test = np.min(te)
        # best_valid = np.min(ve)
        "ystar_valid": 0.0067059280117973685, #0.007629349,
        "ystar_test": 0.00423929700627923,
    },
    "NASCifar10ABenchmark_fixed_seed_0": {
        "xlim_lo": 10**1,
        "ylim_lo": 10**-3.5,
        "ylim_up": 10**-0,
        "xscale": "log",
        "yscale": "log",
        # https://github.com/automl/nas_benchmarks/blob/master/tabular_benchmarks/nas_cifar10.py#L26
        "ystar_valid": 0.04944576819737756,
        "ystar_test": 0.056824247042338016,
    },
    "NASCifar10ABenchmark_random_seed": {
        "xlim_lo": 10**1,
        "ylim_lo": 10**-3.5,
        "ylim_up": 10**-0,
        "xscale": "log",
        "yscale": "log",
        # https://github.com/automl/nas_benchmarks/blob/master/tabular_benchmarks/nas_cifar10.py#L26
        "ystar_valid": 0.04944576819737756,
        "ystar_test": 0.056824247042338016,
    },
    "NASCifar10ABenchmark": {
        "xlim_lo": 10**2,
        "ylim_lo": 10**-2.6,
        "ylim_up": 10**-0,
        "cylim": [-0.3, 1.1],
        "xscale": "log",
        "yscale": "log",
        # https://github.com/automl/nas_benchmarks/blob/master/tabular_benchmarks/nas_cifar10.py#L26
        "ystar_valid": 0.04944576819737756,
        "ystar_test": 0.056824247042338016,
    },
    "NASCifar10BBenchmark": {
        "xlim_lo": 10**2,
        "ylim_lo": 10**-2.6,
        "ylim_up": 10**-0,
        "cylim": [-0.3, 1.1],
        "xscale": "log",
        "yscale": "log",
        # https://github.com/automl/nas_benchmarks/blob/master/tabular_benchmarks/nas_cifar10.py#L26
        "ystar_valid": 0.04944576819737756,
        "ystar_test": 0.056824247042338016,
    },
    "NASCifar10CBenchmark": {
        "xlim_lo": 10**2,
        "ylim_lo": 10**-2.6,
        "ylim_up": 10**-0,
        "cylim": [-0.3, 1.1],
        "xscale": "log",
        "yscale": "log",
        # https://github.com/automl/nas_benchmarks/blob/master/tabular_benchmarks/nas_cifar10.py#L26
        "ystar_valid": 0.04944576819737756,
        "ystar_test": 0.056824247042338016,
    },
    "Cifar100NasBench201Benchmark": {
        "xlim_lo": 10**2,
        "ylim_lo": 10**-1,
        "ylim_up": 10**2,
        "cylim": [0.2, 1.1],
        "xscale": "log",
        "yscale": "log",
        # from hpobench.benchmarks.nas.nasbench_201 import Cifar100NasBench201Benchmark
        # a = Cifar100NasBench201Benchmark()
        # keys = a.data[(777, 'train_acc1es')].keys()
        #
        # configs, te, ve = [], [], []
        # for k in keys:
        #     t1 = a.data[(777, "valid_acc1es")][k][199]
        #     t2 = a.data[(888, "valid_acc1es")][k][199]
        #     t3 = a.data[(999, "valid_acc1es")][k][199]
        #     te.append(float(100 - np.mean([t1, t2, t3])))
        #     v1 = a.data[(777, "test_acc1es")][k]
        #     v2 = a.data[(888, "test_acc1es")][k]
        #     v3 = a.data[(999, "test_acc1es")][k]
        #     ve.append(float(100 - np.mean([v1, v2, v3])))
        # best_test = np.min(te)
        # best_valid = np.min(ve)
        # print(b, best_test, best_valid)
        "ystar_valid": 26.49666666666667,
        "ystar_test": 26.48666667887369,
    },
    "Cifar10ValidNasBench201Benchmark": {
        "xlim_lo": 10**2,
        "ylim_lo": 10**-2,
        "ylim_up": 10**2,
        "cylim": [0.2, 1.1],
        "xscale": "log",
        "yscale": "log",
        # from hpobench.benchmarks.nas.nasbench_201 import Cifar10ValidNasBench201Benchmark
        # a = Cifar10ValidNasBench201Benchmark()
        # keys = a.data[(777, 'train_acc1es')].keys()
        #
        # configs, te, ve = [], [], []
        # for k in keys:
        #     t1 = a.data[(777, "valid_acc1es")][k][199]
        #     t2 = a.data[(888, "valid_acc1es")][k][199]
        #     t3 = a.data[(999, "valid_acc1es")][k][199]
        #     te.append(float(100 - np.mean([t1, t2, t3])))
        #     v1 = a.data[(777, "test_acc1es")][k]
        #     v2 = a.data[(888, "test_acc1es")][k]
        #     v3 = a.data[(999, "test_acc1es")][k]
        #     ve.append(float(100 - np.mean([v1, v2, v3])))
        # best_test = np.min(te)
        # best_valid = np.min(ve)
        # print(b, best_test, best_valid)
        "ystar_valid": 8.393333349609364,
        "ystar_test": 8.476666666666674,
    },
    "ImageNetNasBench201Benchmark": {
        "xlim_lo": 10**2,
        "ylim_lo": 10**-1,
        "ylim_up": 10**2,
        "cylim": [0.2, 1.1],
        "xscale": "log",
        "yscale": "log",
        # from hpobench.benchmarks.nas.nasbench_201 import ImageNetNasBench201Benchmark
        # a = ImageNetNasBench201Benchmark()
        # keys = a.data[(777, 'train_acc1es')].keys()
        #
        # configs, te, ve = [], [], []
        # for k in keys:
        #     t1 = a.data[(777, "valid_acc1es")][k][199]
        #     t2 = a.data[(888, "valid_acc1es")][k][199]
        #     t3 = a.data[(999, "valid_acc1es")][k][199]
        #     te.append(float(100 - np.mean([t1, t2, t3])))
        #     v1 = a.data[(777, "test_acc1es")][k]
        #     v2 = a.data[(888, "test_acc1es")][k]
        #     v3 = a.data[(999, "test_acc1es")][k]
        #     ve.append(float(100 - np.mean([v1, v2, v3])))
        # best_test = np.min(te)
        # best_valid = np.min(ve)
        # print(b, best_test, best_valid)
        "ystar_valid": 53.1555555352105,
        "ystar_test": 52.68888899400499,
    },
    "NASBench1shot1SearchSpace1Benchmark": {
        "xlim_lo": 10**2,
        "ylim_lo": 10**-4,
        "ylim_up": 10**0,
        "xscale": "log",
        "yscale": "log",
        # scripts/Nas1shot1_Incumbent.py
        "ystar_valid": 1-0.9471821784973145,
        "ystar_test": 1-0.9420072237650553,

    },
    "NASBench1shot1SearchSpace2Benchmark": {
        "xlim_lo": 10**2,
        "ylim_lo": 10**-4,
        "ylim_up": 10**0,
        "xscale": "log",
        "yscale": "log",
        # scripts/Nas1shot1_Incumbent.py
        "ystar_valid": 1-0.9456797440846761,
        "ystar_test": 1-0.9396701256434122,

    },
    "NASBench1shot1SearchSpace3Benchmark": {
        "xlim_lo": 10**2,
        "ylim_lo": 10**-4,
        "ylim_up": 10**0,
        "xscale": "log",
        "yscale": "log",
        # scripts/Nas1shot1_Incumbent.py
        "ystar_valid": 1-0.9473824898401896,
        "ystar_test": 1-0.941773513952891,

    },
    "ParamNetAdultOnTimeBenchmark": {
        "xlim_lo": 10**1,
        "ylim_lo": 10**-3,
        "ylim_up": 10**-1,
        "cylim": [-0.6, 1.1],
        "xscale": "log",
        "yscale": "log",
        # from stats json file March 9th
        "ystar_valid": 0.1437777783975557,
        "ystar_test": 0,
    },
    "ParamNetHiggsOnTimeBenchmark": {
        "xlim_lo": 10**1,
        "ylim_lo": 10**-3,
        "ylim_up": 10**-1,
        "cylim": [-0.6, 1.1],
        "xscale": "log",
        "yscale": "log",
        # from stats json file March 9th
        "ystar_valid": 0.2739252715252642,
        "ystar_test": 0,
    },
    "ParamNetLetterOnTimeBenchmark": {
        "xlim_lo": 10**0,
        "ylim_lo": 10**-3.5,
        "ylim_up": 10**0,
        "xscale": "log",
        "yscale": "log",
        # from stats json file March 9th
        "ystar_valid": 0.030800543060296292,
        "ystar_test": 0,
    },
    "ParamNetMnistOnTimeBenchmark": {
        "xlim_lo": 10**1,
        "ylim_lo": 10**-4,
        "ylim_up": 10**0,
        "cylim": [-0.6, 1.1],
        "xscale": "log",
        "yscale": "log",
        # from stats json file March 9th
        "ystar_valid": 0.014969998741149893,
        "ystar_test": 0,
    },
    "ParamNetOptdigitsOnTimeBenchmark": {
        "xlim_lo": 10**0,
        "ylim_lo": 10**-3.5,
        "ylim_up": 10**0,
        "xscale": "log",
        "yscale": "log",
        # from stats json file March 9th
        "ystar_valid": 0.011504424673266123,
        "ystar_test": 0,
   },
    "ParamNetPokerOnTimeBenchmark": {
        "xlim_lo": 10**2,
        "ylim_lo": 10**-4,
        "ylim_up": 10**0,
        "cylim": [-0.6, 1.1],
        "xscale": "log",
        "yscale": "log",
        # from stats json file March 9th
        "ystar_valid": 0.00016679192417291545,
        "ystar_test": 0,
    },
    "ParamNetReducedAdultOnTimeBenchmark": {
        #"xlim_lo": 10 ** 1,
        #"ylim_lo": 10 ** -3,
        #"ylim_up": 10 ** -1,
        "cylim": [0.4, 1.1],
        "xscale": "log",
        "yscale": "log",
        # from stats json file Mar 25th
        "ystar_valid": 0.14413888573646547,
        "ystar_test": 0,
    },
    "ParamNetReducedHiggsOnTimeBenchmark": {
        #"xlim_lo": 10 ** 1,
        #"ylim_lo": 10 ** -3,
        #"ylim_up": 10 ** -1,
        "cylim": [0.4, 1.1],
        "xscale": "log",
        "yscale": "log",
        # from stats json file Mar 25th
        "ystar_valid": 0.2772739828301669,
        "ystar_test": 0,
    },
    "ParamNetReducedLetterOnTimeBenchmark": {
        "xlim_lo": 10 ** 0,
        "ylim_lo": 10 ** -3.5,
        "ylim_up": 10 ** 0,
        "cylim": [0.4, 1.1],
        "xscale": "log",
        "yscale": "log",
        # from stats json file Mar 25th
        "ystar_valid": 0.03344640258559809,
        "ystar_test": 0,
    },
    "ParamNetReducedMnistOnTimeBenchmark": {
        "xlim_lo": 10 ** 1,
        "ylim_lo": 10 ** -4,
        "ylim_up": 10 ** 0,
        "cylim": [0.4, 1.1],
        "xscale": "log",
        "yscale": "log",
        # from stats json file Mar 25th
        "ystar_valid": 0.015160002479553214,
        "ystar_test": 0,
    },
    "ParamNetReducedOptdigitsOnTimeBenchmark": {
        "xlim_lo": 10 ** 0,
        "ylim_lo": 10 ** -3.5,
        "ylim_up": 10 ** 0,
        "cylim": [0.4, 1.1],
        "xscale": "log",
        "yscale": "log",
        # from stats json file Mar 25th
        "ystar_valid": 0.013435238033940667,
        "ystar_test": 0,
    },
    "ParamNetReducedPokerOnTimeBenchmark": {
        "xlim_lo": 10 ** 2,
        "ylim_lo": 10 ** -4,
        "ylim_up": 10 ** 0,
        "cylim": [0.4, 1.1],
        "xscale": "log",
        "yscale": "log",
        # from stats json file Mar 25th
        "ystar_valid": 0.00026607234795810174,
        "ystar_test": 0,
    },
    "NASCifar10ABenchmark_fixed_seed_0": {
        "xlim_lo": 10**1,
        "ylim_lo": 10**-3.5,
        "ylim_up": 10**-0,
        "xscale": "log",
        "yscale": "log",
        # https://github.com/automl/nas_benchmarks/blob/master/tabular_benchmarks/nas_cifar10.py#L26
        "ystar_valid": 0.04944576819737756,
        "ystar_test": 0.056824247042338016,
    },
    "NASCifar10ABenchmark_random_seed": {
        # See original benchmark
        "xlim_lo": 10**1,
        "ylim_lo": 10**-3.5,
        "ylim_up": 10**-0,
        "xscale": "log",
        "yscale": "log",
        "ystar_valid": 0.04944576819737756,
        "ystar_test": 0.056824247042338016,
    },
    "ProteinStructureBenchmark_fixed_seed_0": {
        # See original benchmark
        "xlim_lo": 10**0,
        "ylim_lo": 10**-4,
        "ylim_up": 10**0,
        "xscale": "log",
        "yscale": "log",
        "ystar_valid": 0.221378855407238,
        "ystar_test": 0.21536806225776672,
    },
    "ProteinStructureBenchmark_random_seed": {
        # See original benchmark
        "xlim_lo": 10**0,
        "ylim_lo": 10**-4,
        "ylim_up": 10**0,
        "xscale": "log",
        "yscale": "log",
        "ystar_valid": 0.221378855407238,
        "ystar_test": 0.21536806225776672,    
    },
    "Cifar10ValidNasBench201Benchmark_fixed_seed_777": {
        # See original benchmark
        "xlim_lo": 10**2,
        "ylim_lo": 10**-2,
        "ylim_up": 10**2,
        "xscale": "log",
        "yscale": "log",
        "ystar_valid": 8.393333349609364,
        "ystar_test": 8.476666666666674,
    },
    "Cifar10ValidNasBench201Benchmark_random_seed": {
        # See original benchmark
        "xlim_lo": 10**2,
        "ylim_lo": 10**-2,
        "ylim_up": 10**2,
        "xscale": "log",
        "yscale": "log",
        "ystar_valid": 8.393333349609364,
        "ystar_test": 8.476666666666674,    
    },
}
with open(Path(__file__).absolute().parent / "tabular_plot_config.yaml", "r") as f:
    temp = yaml.load(f, Loader=yaml.FullLoader)
plot_dc.update(temp)

color_dc = {
    "mint": '#1b9e77',
    "orange": '#d95f02',
    "purple": '#7570b3',
    "pink": '#e7298a',
    "green": '#66a61e',
    "yellow": '#e6ab02',
    "brown": '#a6761d',
    "red": '#e41a1c',
    "blue": '#377eb8',
    "grey": '#999999',
    "light_blue": '#a6cee3',
    "light_brown": '#fdbf6f',
    "light_purple": '#cab2d6',
    }

color_per_opt = {
    "randomsearch": color_dc["blue"],

    "hpbandster_bohb_eta_3": "darkgreen",
    "hpbandster_bohb_eta_2": "darkgreen",
    "hpbandster_tpe": "lime",
    "hpbandster_hb_eta_3": "greenyellow",

    "smac_hb_eta_3": "deeppink",
    "smac_hb_eta_2": "deeppink",
    "smac_sf": color_dc["purple"],
    "smac_bo": "magenta",

    "dragonfly_default": "pink",
    "dehb": "cyan",
    "de": "darkcyan",

    "autogluon": "yellow",

    "ray_hyperopt_asha": "saddlebrown",
    "ray_randomsearch": "chocolate",
    "ray_hyperopt": "sandybrown",

    'optuna_cmaes_hb': "lightcoral",
    'optuna_tpe_hb': "red",
    'optuna_tpe_median': "darkred",
}

marker_per_opt = {
    "hpbandster_bohb_eta_3": "o",
    "hpbandster_bohb_eta_2": "o",
    "hpbandster_hb_eta_3": "o",
    "hpbandster_tpe": "o",
    "smac_hb_eta_3": "s",
    "smac_hb_eta_2": "s",
    "smac_sf": "s",
    "smac_bo": "s",
    "randomsearch": "v",
    "dragonfly_default": "^",
    "dehb": "*",
    "autogluon": "o",
    "ray_bayesopt_hb": "x",
    "ray_hyperopt_hb": "x",
    "ray_optuna_hb": "x",
    "ray_hyperopt_no_fidelity": "x",
    "ray_randomsearch": "x",
    "ray_bohb": "x",
    'optuna_tpe_hb': "X",
    'optuna_cmaes_hb': "X",
    'optuna_randomsearch': "X",
    'optuna_tpe_median': "X",
}


def unify_layout(ax, fontsize=20, legend_args=None, title=None, add_legend=True):
    if legend_args is None:
        legend_args = {}
    if add_legend:
        ax.legend(fontsize=fontsize, **legend_args)
    ax.tick_params(axis="x", labelsize=fontsize)
    ax.tick_params(axis="y", labelsize=fontsize)
    ax.xaxis.get_label().set_fontsize(fontsize)
    ax.yaxis.get_label().set_fontsize(fontsize)
    if title is not None:
        ax.set_title(title, fontsize=fontsize)
    ax.grid(b=True, which="both", axis="both", alpha=0.5)


benchmark_families = {
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
    "tabular_svm": [
        'svm_10101', 'svm_53', 'svm_146818', 'svm_146821', 'svm_9952', 'svm_146822', 'svm_31',
        'svm_3917', 'svm_168912', 'svm_3', 'svm_167119', 'svm_12', 'svm_146212', 'svm_168911',
        'svm_9981', 'svm_168329', 'svm_167120', 'svm_14965', 'svm_146606', 'svm_168330',
        'svm_7592', 'svm_9977', 'svm_168910', 'svm_168335', 'svm_146195', 'svm_168908',
        'svm_168331', 'svm_168868', 'svm_168909', 'svm_189355', 'svm_146825', 'svm_7593',
        'svm_168332', 'svm_168337', 'svm_168338', 'svm_189354', 'svm_34539', 'svm_3945'
    ],
    "tabular_lr": [
        'lr_10101', 'lr_53', 'lr_146818', 'lr_146821', 'lr_9952', 'lr_146822', 'lr_31',
        'lr_3917', 'lr_168912', 'lr_3', 'lr_167119', 'lr_12', 'lr_146212', 'lr_168911',
        'lr_9981', 'lr_168329', 'lr_167120', 'lr_14965', 'lr_146606', 'lr_168330', 'lr_7592',
        'lr_9977', 'lr_168910', 'lr_168335', 'lr_146195', 'lr_168908', 'lr_168331', 'lr_168868',
        'lr_168909', 'lr_189355', 'lr_146825', 'lr_7593', 'lr_168332', 'lr_168337', 'lr_168338',
        'lr_189354', 'lr_34539', 'lr_3945'
    ],
    "tabular_rf": [
        'rf_10101', 'rf_53', 'rf_146818', 'rf_146821', 'rf_9952', 'rf_146822', 'rf_31',
        'rf_3917', 'rf_168912', 'rf_3', 'rf_167119', 'rf_12', 'rf_146212', 'rf_168911',
        'rf_9981', 'rf_168329', 'rf_167120', 'rf_14965', 'rf_146606', 'rf_168330', 'rf_7592',
        'rf_9977', 'rf_168910', 'rf_168335', 'rf_146195', 'rf_168908', 'rf_168331', 'rf_168868',
        'rf_168909', 'rf_189355', 'rf_146825', 'rf_7593', 'rf_168332', 'rf_168337', 'rf_168338',
        'rf_189354', 'rf_34539', 'rf_3945'
    ],
    "tabular_xgb": [
        'xgb_10101', 'xgb_53', 'xgb_146818', 'xgb_146821', 'xgb_9952', 'xgb_146822', 'xgb_31',
        'xgb_3917', 'xgb_168912', 'xgb_3', 'xgb_167119', 'xgb_12', 'xgb_146212', 'xgb_168911',
        'xgb_9981', 'xgb_168329', 'xgb_167120', 'xgb_14965', 'xgb_146606', 'xgb_168330',
        'xgb_7592', 'xgb_9977', 'xgb_168910', 'xgb_168335', 'xgb_146195', 'xgb_168908',
        'xgb_168331', 'xgb_168868', 'xgb_168909', 'xgb_189355', 'xgb_146825', 'xgb_7593',
        'xgb_168332', 'xgb_168337', 'xgb_168338', 'xgb_189354', 'xgb_34539', 'xgb_3945'
    ],
    "tabular_nn": [
        'nn_10101', 'nn_53', 'nn_146818', 'nn_146821', 'nn_9952', 'nn_146822', 'nn_31', 
        'nn_3917', 'nn_168912', 'nn_3', 'nn_167119', 'nn_12', 'nn_146212', 'nn_168911', 
        'nn_9981', 'nn_168329', 'nn_167120', 'nn_14965', 'nn_146606', 'nn_168330', 'nn_7592', 
        'nn_9977', 'nn_168910', 'nn_168335', 'nn_146195', 'nn_168908', 'nn_168331', 'nn_168868', 
        'nn_168909', 'nn_189355', 'nn_146825', 'nn_7593', 'nn_168332', 'nn_168337', 'nn_168338', 
        'nn_189354', 'nn_34539', 'nn_3945'
    ],
}

benchmark_dc = {
    "Cifar10ValidNasBench201Benchmark": "NB201 - Cifar10",
    "Cifar100NasBench201Benchmark":  "NB201 - Cifar100",
    "ImageNetNasBench201Benchmark":  "NB201 - ImageNet",
    "NASCifar10ABenchmark":  "NB101 - A",
    "NASCifar10BBenchmark":  "NB101 - B",
    "NASCifar10CBenchmark":  "NB101 - C",
    "SliceLocalizationBenchmark": "NBHPO - Slice", 
    "ProteinStructureBenchmark":  "NBHPO - Protein",
    "NavalPropulsionBenchmark":  "NBHPO - Naval",
    "ParkinsonsTelemonitoringBenchmark":  "NBHPO - Parkinsons",
    "NASBench1shot1SearchSpace1Benchmark":  "NB1Shot1 - 1",
    "NASBench1shot1SearchSpace2Benchmark":  "NB1Shot1 - 2",
    "NASBench1shot1SearchSpace3Benchmark":  "NB1Shot1 - 3",
    "BNNOnBostonHousing":  "BNN - Boston",
    "BNNOnProteinStructure":  "BNN - Protein",
    "BNNOnYearPrediction":  "BNN - Year",
    "cartpolereduced":  "cartpole reduced",
    "metalearna":  "metalearna",
    "learna":  "learna",
    "ParamNetAdultOnTimeBenchmark":   "Net - full - Adult",
    "ParamNetHiggsOnTimeBenchmark":   "Net - full - Higgs",
    "ParamNetLetterOnTimeBenchmark":  "Net - full - Letter",
    "ParamNetMnistOnTimeBenchmark":   "Net - full - Mnist",
    "ParamNetOptdigitsOnTimeBenchmark":  "Net - full - OptDigits",
    "ParamNetPokerOnTimeBenchmark":   "Net - full - Poker",
    "ParamNetReducedAdultOnTimeBenchmark":   "Net - Adult",
    "ParamNetReducedHiggsOnTimeBenchmark":   "Net - Higgs",
    "ParamNetReducedLetterOnTimeBenchmark":  "Net - Letter",
    "ParamNetReducedMnistOnTimeBenchmark":   "Net - Mnist",
    "ParamNetReducedOptdigitsOnTimeBenchmark":  "Net - OptDigits",
    "ParamNetReducedPokerOnTimeBenchmark":   "Net - Poker",
}
