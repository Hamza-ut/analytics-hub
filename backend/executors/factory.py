from django.conf import settings
from .base import BaseExecutor
from .local.executor import LocalServerExecutor


def get_executor() -> BaseExecutor:
    backend = getattr(settings, "EXECUTOR_BACKEND", "localserver").lower()

    if backend == "localserver":
        return LocalServerExecutor()
    elif backend == "hpc":
        from .hpc.executor import HPCExecutor

        return HPCExecutor()
    else:
        raise ValueError(f"Unsupported EXECUTOR_BACKEND setting: '{backend}'")
