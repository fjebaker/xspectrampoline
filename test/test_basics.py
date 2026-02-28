import pytest
import xspectrampoline
import numpy as np


def test_powerlaw():
    lib = xspectrampoline.get_libraries()
    powerlaw = lib.get_model("C_powerlaw")

    energy = np.linspace(0.01, 10.0, 100, dtype=np.float64)
    parameters = np.array([3.0], dtype=np.float64)
    output = np.zeros(len(energy) - 1, dtype=np.float64)
    error = np.zeros(len(energy) - 1, dtype=np.float64)

    powerlaw(energy, parameters, output, error)

    assert pytest.approx(output.sum(), 1e-1) == 5000.0
