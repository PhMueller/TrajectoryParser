import logging
from importlib import import_module
from pathlib import Path
from typing import List, Dict, Any

import yaml

_log = logging.getLogger(__name__)


def transform_unknown_params_to_dict(unknown_args: List) -> Dict:
    """
    Given a list of unknown parameters in form ['--name', '--value', ...], it transforms the list into a dictionary.
    TODO (pm): figure out how to find the right parameter type. Currently, it just casts it to an integer.

    This function is used to extract the benchmark parameters (such as the task id for the xgboost benchmark) from the
    command line arguments.

    Parameters
    ----------
    unknown_args : List

    Returns
    -------
    Dict
    """
    benchmark_params = {}
    for i in range(0, len(unknown_args), 2):
        try:
            value = int(unknown_args[i+1])
        except ValueError:
            value = unknown_args[i+1]
        except IndexError:
            raise IndexError('While parsing additional arguments an index error occured. '
                             'This means a parameter has no value.')

        benchmark_params[unknown_args[i][2:]] = value
    return benchmark_params


def load_optimizer_settings() -> Dict:
    """ Load the experiment settings from file """
    optimizer_settings_path = Path(__file__).absolute().parent.parent / 'optimizer_settings.yaml'
    with optimizer_settings_path.open('r') as fh:
        optimizer_settings = yaml.load(fh, yaml.FullLoader)
    return optimizer_settings


def get_optimizer_settings_names():
    settings = load_optimizer_settings()
    return list(settings.keys())


def get_optimizer_setting(optimizer_setting_str: str) -> Dict:
    optimizer_settings = load_optimizer_settings()
    settings_names = get_optimizer_settings_names()

    assert optimizer_setting_str in settings_names,\
        f"Optimizer setting {optimizer_setting_str} not found. Should be one of {', '.join(settings_names)}"

    return optimizer_settings[optimizer_setting_str]


def load_benchmark_settings() -> Dict:
    """ Load the experiment settings from file """
    experiment_settings_path = Path(__file__).absolute().parent.parent.glob("*benchmark_settings.yaml")

    experiment_settings = dict()
    for yaml_file in experiment_settings_path:
        with yaml_file.open('r') as fh:
            experiment_settings.update(yaml.load(fh, yaml.FullLoader))

    return experiment_settings


def get_benchmark_names():
    """ Get the names for the supported benchmarks. """
    experiment_settings = load_benchmark_settings()
    return list(experiment_settings.keys())


def get_benchmark_settings(benchmark: str) -> Dict:
    """
    Get a dictionary for each benchmark containing the experiment parameters.

    Parameters
    ----------
    benchmark : str
    rng : int
        Random seed
    output_dir : Path
        path to the output directory

    Returns
    -------
        Tuple[Dict, Dict] - optimizer settings, benchmark settings
    """
    experiment_settings = load_benchmark_settings()
    benchmark_names = get_benchmark_names()

    assert benchmark in benchmark_names,\
        f"benchmark name {benchmark} not found. Should be one of {', '.join(benchmark_names)}"

    experiment_settings = experiment_settings[benchmark]

    # Check that all mandatory fields are in the settings given:
    mandatory = ['time_limit_in_s', 'cutoff_in_s', 'mem_limit_in_mb', 'import_from', 'import_benchmark']
    found = [option in experiment_settings for option in mandatory]

    assert all(found), "Missing mandatory option(s) %s in benchmark settings %s" % \
                       (str([o for b, o in zip(found, mandatory) if not b]), str(experiment_settings))

    # fill missing parameter with default ones:
    default_params = dict(num_iterations=10000000,
                          is_surrogate=False,
                          tae_limit=None,
                          fuel_limit=None)

    experiment_settings = dict(default_params, **experiment_settings)

    return experiment_settings


def load_benchmark(benchmark_name, import_from, use_local: bool) -> Any:
    """
    Load the benchmark object.
    If not `use_local`:  Then load a container from a given source, defined in the HPOBench.

    Import via command from hpobench.[container.]benchmarks.<import_from> import <benchmark_name>

    Parameters
    ----------
    benchmark_name : str
    import_from : str
    use_local : bool
        By default this value is set to false.
        In this case, a container will be downloaded. This container includes all necessary files for the experiment.
        You don't have to install something.

        If true, use the experiment locally. Therefore the experiment has to be installed.
        See the experiment description in the HPOBench.

    Returns
    -------
    Benchmark
    """
    import_str = 'hpobench.' + ('container.' if not use_local else '') + 'benchmarks.' + import_from
    _log.debug(f'Try to execute command: from {import_str} import {benchmark_name}')

    module = import_module(import_str)
    benchmark_obj = getattr(module, benchmark_name)
    _log.debug(f'Benchmark {benchmark_name} successfully loaded')

    return benchmark_obj
