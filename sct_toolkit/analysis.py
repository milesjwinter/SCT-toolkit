from __future__ import division, print_function, absolute_import
import sys, os
import numpy as np
from .pedestal import pedestal
from .waveform import waveform

def charge_spectrum(filename, module, asic, channel, block=None, phase=None):
    """
    Calculate charge spectrum for a given module, asic, and channel

    Parameters
    ----------
    filename : str, (optional)
        If specified, loads an existing database (default: None)

    """
