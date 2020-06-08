import argparse
import logging
from collections import OrderedDict
from importlib import import_module
from pathlib import Path
from typing import Union, Dict

from HPOlibExperimentUtils import BOHBReader, SMACReader
from HPOlibExperimentUtils.utils.runner_utils import transform_unknown_params_to_dict, get_setting_per_benchmark

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('BenchmarkRunner')


def validate_benchmark(benchmark: str,
                       output_dir: Union[Path, str],
                       rng: int,
                       **benchmark_params: Dict):

    output_dir = Path(output_dir)

    assert output_dir.is_dir(), f'Result folder doesn\"t exist: {output_dir}'
    optimizer_settings, benchmark_settings = get_setting_per_benchmark(benchmark, rng=rng, output_dir=output_dir)

    # Load benchmark
    module = import_module(f'hpolib.benchmarks.{benchmark_settings["import_from"]}')
    benchmark_obj = getattr(module, benchmark_settings['import_benchmark'])

    benchmark = benchmark_obj(**benchmark_params)  # Todo: Arguments for Benchmark? --> b(**benchmark_params)

    # first try to load already extracted trajectory file
    unvalidated_trajectory = output_dir / f'traj_hpolib.json'
    already_extracted = unvalidated_trajectory.exists()
    bohb_run = len(list(unvalidated_trajectory.parent.glob('**/results.json'))) != 0

    reader = SMACReader() if already_extracted or bohb_run else BOHBReader()
    reader.read(file_path=unvalidated_trajectory if already_extracted else output_dir)
    reader.get_trajectory()

    trajectory_ids = reader.get_configuration_ids_trajectory()

    configurations_to_validate = \
        OrderedDict({traj_id: reader.config_ids_to_configs[traj_id][0] for traj_id in trajectory_ids})
    validated_loss = OrderedDict({traj_id: -1234 for traj_id in trajectory_ids})

    for traj_id in configurations_to_validate:
        config = configurations_to_validate[traj_id]
        max_budget = optimizer_settings['max_budget']
        cast_to = benchmark_settings['fidelity_type']
        fidelity = {benchmark_settings['fidelity_name']: cast_to(max_budget)}
        result_dict = benchmark.objective_function_test(config, **fidelity, **benchmark_settings)
        validated_loss[traj_id] = result_dict['function_value']

    reader.add_validated_trajectory(validated_loss)
    traj_path = optimizer_settings['output_dir'] / f'traj_validated_hpolib.json'

    reader.export_validated_trajectory(traj_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='HPOlib3 Wrapper',
                                     description='HPOlib3 validated a trajectory from a benchmark with a '
                                                 'unified interface',
                                     )

    parser.add_argument('--output_dir', required=True, type=str)
    parser.add_argument('--benchmark', required=True, type=str)
    parser.add_argument('--rng', required=False, default=0, type=int)

    args, unknown = parser.parse_known_args()
    benchmark_params = transform_unknown_params_to_dict(unknown)

    validate_benchmark(**vars(args), **benchmark_params)
