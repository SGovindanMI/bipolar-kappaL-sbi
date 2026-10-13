"""Load frozen observations and version 5 corrected inference arrays.

The forward model promotes all numeric inputs to float64.
"""
import os

import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, 'data')

PARAM_NAMES = ['log10N_net', 'log10m_maj', 'log10m_min', 'log10mu300', 'p_mu',
               'log10Eg', 'log10A', 'w', 'r', 'kmin']


def load_ppc(path=None):
    """Per-curve posterior samples and posterior-predictive diagnostics (13,256 curves)."""
    return np.load(path or os.path.join(DATA, 'inference_v5.npz'), allow_pickle=True)


def load_theta(path=None):
    """Posterior samples, shape (N, 128, 10), as float64. Always use this."""
    return load_ppc(path)['theta'].astype(np.float64)


def load_analysis_set(path=None):
    """The 13,256-curve corpus: 50-d features, window endpoints, DOI, family."""
    return np.load(path or os.path.join(DATA, 'real_analysis_set.npz'), allow_pickle=True)


def load_results(path=None):
    """kappa_L decomposition and explicit masks for all eligible curves."""
    return np.load(path or os.path.join(DATA, 'results_v5.npz'), allow_pickle=True)


def unpack_features(x, NG=16):
    """Split the 50-vector into physical quantities.

    Returns sigma [S/m], S [uV/K], kappa [W/m/K], and the window endpoints [K].
    """
    x = np.atleast_2d(x)
    sigma = 10.0 ** x[:, :NG]
    seebeck = x[:, NG:2 * NG]
    kappa = np.exp(x[:, 2 * NG:3 * NG])
    Thi = x[:, -2] * 1000.0
    Tlo = x[:, -1] * 1000.0
    return sigma, seebeck, kappa, Tlo, Thi


def temperature_grid(Tlo, Thi, NG=16):
    """The grid each curve was resampled onto."""
    return np.linspace(Tlo, Thi, NG, axis=-1)
