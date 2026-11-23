import copy

import pytest

import fido.fido as fido_mod


@pytest.fixture(autouse=True)
def restore_fido_defaults():
    """Undo what main() writes into the module level defaults, which Fido() reads on every construction.

    Restored in place so that modules holding a reference to the dict (tests/test_cli_args.py) stay valid.
    """
    saved = copy.deepcopy(fido_mod.defaults)
    yield
    fido_mod.defaults.clear()
    fido_mod.defaults.update(saved)
