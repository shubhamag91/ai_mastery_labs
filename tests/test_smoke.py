from importlib.metadata import version


def test_package_is_installed():
    # version() reads the shopai-*.dist-info label in the venv, so this passes
    # only if the package is installed, not merely present in src/.
    assert version("shopai")
