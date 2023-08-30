import copy
import tempfile
from contextlib import contextmanager

from cli.cli import get_parameters
from config import Config, new_config

CONFIG_CACHE = {}


@contextmanager
def _new_config_from_parameter(params):
    _params = tuple(params)
    if _params in CONFIG_CACHE:
        return CONFIG_CACHE[_params]
    config, _ = get_parameters(["--path=.", "--xml"] + list(params))
    CONFIG_CACHE[_params] = config
    _config = new_config(copy.deepcopy(config.asdict()))
    try:
        with tempfile.TemporaryDirectory(prefix="wikiteam3test_") as tmpdir:
            _config.path = tmpdir
            yield _config
    finally:
        pass


def get_config(mediawiki_ver, api=True) -> Config:
    assert api == True
    if mediawiki_ver == "1.16.5":
        return _new_config_from_parameter(
            [
                "--api",
                "http://group0.mediawiki.demo.save-web.org/mediawiki-1.16.5/api.php",
            ]
        )  # type: ignore
    else:
        raise ValueError(
            f"Can't test version {mediawiki_ver} of mediawiki; expected version 1.16.5"
        )
