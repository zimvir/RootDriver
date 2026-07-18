from importlib.metadata import version, PackageNotFoundError

from ..exceptions import OptionalDependenceNotFoundError


def deal_optional_dependence_installed_status(dependence_name: str):
    try:
        version(dependence_name)
        return True
    except PackageNotFoundError:
        raise OptionalDependenceNotFoundError(dependence_name)

