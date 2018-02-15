
import sys

try:
    __SCT_TOOLKIT_SETUP__
except NameError:
    __SCT_TOOLKIT_SETUP__ = False

if __SCT_TOOLKIT_SETUP__:
    sys.stderr.write('\n***Partial import of sct_toolkit during the build process***\n')
else:
    from .pedestal import pedestal
    from .waveform import waveform
    from .interactive import interactive_heatmap
    from .analysis import charge_spectrum
    from .quick_plots import plot_charge, plot_amplitude, plot_position
    from .utils import docs

__version__ = '0.0.1'
