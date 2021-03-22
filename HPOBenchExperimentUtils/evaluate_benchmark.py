import argparse
import logging

from HPOBenchExperimentUtils.utils.runner_utils import get_benchmark_names
from HPOBenchExperimentUtils.analysis.trajectory_plotting import plot_trajectory
from HPOBenchExperimentUtils.analysis.stats_generation import plot_fidels, plot_overhead, \
    plot_ecdf, plot_correlation, get_stats
from HPOBenchExperimentUtils.analysis.table_generation import save_median_table
from HPOBenchExperimentUtils.analysis.rank_plotting import plot_ranks
from HPOBenchExperimentUtils import _log as _root_log

_root_log.setLevel(logging.DEBUG)
_log = logging.getLogger(__name__)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='HPOBench Wrapper - Plotting tool',
                                     description='Plot the trajectories')

    parser.add_argument('--output_dir', required=True, type=str)
    parser.add_argument('--input_dir', required=True, type=str)
    parser.add_argument('--benchmark', choices=get_benchmark_names(), required=True, type=str)
    parser.add_argument('--what', choices=["all", "best_found", "over_time", "other",
                                           "ecdf", "correlation", "stats", "ranks"], default="all")
    parser.add_argument('--agg', choices=["mean", "median"], default="median")
    parser.add_argument('--unvalidated', action='store_true', default=False)
    parser.add_argument('--which', choices=["v1", "v2"], default="v1")
    args, unknown = parser.parse_known_args()

    list_of_opt_to_consider = ["autogluon", "dragonfly_default", "randomsearch",
                               "smac_sf", "smac_hb_eta_3",
                               "dehb", "hpbandster_bohb_eta_3", "hpbandster_hb_eta_3",
                               #"mumbo",
                               ]
    if args.what in ("all", "best_found"):
        save_median_table(**vars(args), opt_list=list_of_opt_to_consider)

    if args.what in ("all", "over_time"):
        plot_trajectory(criterion=args.agg, **vars(args), opt_list=list_of_opt_to_consider)

    if args.what in ("all", "ecdf"):
        plot_ecdf(**vars(args), opt_list=list_of_opt_to_consider)

    if args.what in ("all", "correlation"):
        plot_correlation(**vars(args), opt_list=list_of_opt_to_consider)

    if args.what in ("all", "stats"):
        get_stats(**vars(args), opt_list=list_of_opt_to_consider)

    if args.what in ("all", "other"):
        if args.unvalidated is False:
            _log.critical("Statistics will be plotted on unvalidated data")
        plot_fidels(**vars(args), opt_list=list_of_opt_to_consider)
        plot_overhead(**vars(args), opt_list=list_of_opt_to_consider)

    if args.what == "ranks":
        plot_ranks(**vars(args), benchmarks=["NASCifar10ABenchmark", "NASCifar10BBenchmark"],
                   criterion=args.agg, opt_list=["randomsearch", "smac_sf"])


