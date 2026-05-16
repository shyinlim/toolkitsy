from packaging.version import Version

import toolkitsy


def test_package_exposes_version():
    assert hasattr(toolkitsy, "__version__")


def test_version_is_valid_pep440():
    Version(toolkitsy.__version__)
