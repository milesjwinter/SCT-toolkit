from __future__ import division, print_function, absolute_import
import sys, os
import StringIO
import urllib, base64
import numpy as np
import matplotlib.pyplot as plt
from .pedestal import pedestal
from .waveform import waveform
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.models import HoverTool, BasicTicker, LinearColorMapper, ColorBar

class interactive_heatmap(object):
    def __init__(self, filename=None):
        """
        Class for creating interactive heatmaps

        Parameters
        ----------
        filename : str, (optional)
            If specified, launches interactive heatmap in browser (default: None)

        """
        try:
            if sys.platform == 'darwin':
                os.system('open {}'.format(filename))
            else:
                os.system('open-xdg {}'.format(filename))
        except IOError:
            raise IOError("file '{}' not found. Check name and/or path ".format(filename))
        
