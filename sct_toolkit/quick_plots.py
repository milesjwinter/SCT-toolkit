from __future__ import division, print_function, absolute_import
import sys, os
import numpy as np
import matplotlib.pyplot as plt
from .pedestal import pedestal
from .waveform import waveform

def plot_charge(filename, module, asic, channel=None, bins=None):
    """
    Generate quick plot of charge spectrum

    Parameters
    ----------
    filename : str
	Name and path of h5py database
    module : int
        Module number
    asic : int
        ASIC number
    channel : int (optional)
        Plot data for a specified channel number only (default: None)
    bins : numpy.ndarray (optional)
        Bins to use for histogram

    """
    wf = waveform(filename)
    if channel:
        charge = np.array(wf.get_branch('Module{}/Asic{}/Channel{}/charge'.format(
                                        module,asic,channel)))
        if bins:
            plt.hist(charge,bins=bins)
        else:
            min_bin = int(np.amin(charge))
            max_bin = int(np.amax(charge))
            plt.hist(charge,bins=np.arange(min_bin-5,max_bin+5,5))
        plt.xlabel('Charge (ADC$\cdot$ns)')
        plt.ylabel('Counts')
        plt.title('Charge: Mod{}, ASIC{}, Ch{}'.format(
                  module,asic,channel))
        plt.minorticks_on()
    else:
        branch = wf.get_branch('Module{}/Asic{}'.format(module,asic))
        f, axarr = plt.subplots(4, 4, figsize=(10,10))
        for i in xrange(4):
            for j in xrange(4):
                index = int(i*4+j)
                charge = np.array(branch['Channel{}/charge'.format(index)])
		if bins:
		    axarr[i, j].hist(charge,bins=bins)
		else:
                    min_bin = int(np.amin(charge))
                    max_bin = int(np.amax(charge))		   
		    axarr[i, j].hist(charge,bins=np.arange(min_bin-5,max_bin+5,5))
                axarr[i, j].set_xlabel('Charge (ADC$\cdot$ns)')
                axarr[i, j].set_ylabel('Counts')
                axarr[i, j].set_title('Charge: Ch{}'.format(channel),fontsize=12)
    wf.close_database()

def plot_amplitude(filename, module, asic, channel=None, bins=None):
    """
    Generate quick plot of the amplitude distribution

    Parameters
    ----------
    filename : str
	Name and path of h5py database
    module : int
        Module number
    asic : int
        ASIC number
    channel : int (optional)
        Plot data for a specified channel number only (default: None)
    bins : numpy.ndarray (optional)
        Bins to use for histogram

    """
    wf = waveform(filename)
    if channel:
        amp = np.array(wf.get_branch('Module{}/Asic{}/Channel{}/amplitude'.format(
                                        module,asic,channel)))
        if bins:
            plt.hist(amp,bins=bins)
        else:
            min_bin = int(np.amin(amp))
            max_bin = int(np.amax(amp))
            plt.hist(amp,bins=np.arange(min_bin-5,max_bin+5,5))
        plt.xlabel('Amplitde (ADC Counts)')
        plt.ylabel('Counts')
        plt.title('Amplitude: Mod{}, ASIC{}, Ch{}'.format(
                  module,asic,channel))
        plt.minorticks_on()
    else:
        branch = wf.get_branch('Module{}/Asic{}'.format(module,asic))
        f, axarr = plt.subplots(4, 4, figsize=(10,10))
        for i in xrange(4):
            for j in xrange(4):
                index = int(i*4+j)
                amp = np.array(branch['Channel{}/amplitude'.format(index)])
		if bins:
		    axarr[i, j].hist(amp,bins=bins)
		else:
                    min_bin = int(np.amin(amp))
                    max_bin = int(np.amax(amp))		   
		    axarr[i, j].hist(amp,bins=np.arange(min_bin-5,max_bin+5,5))
                axarr[i, j].set_xlabel('Amplitude (ADC Counts)')
                axarr[i, j].set_ylabel('Counts')
                axarr[i, j].set_title('Amplitude: Ch{}'.format(channel),fontsize=12)
    wf.close_database()

def plot_position(filename, module, asic, channel=None, bins=None):
    """
    Generate quick plot of position distribution

    Parameters
    ----------
    filename : str
	Name and path of h5py database
    module : int
        Module number
    asic : int
        ASIC number
    channel : int (optional)
        Plot data for a specified channel number only (default: None)
    bins : numpy.ndarray (optional)
        Bins to use for histogram

    """
    wf = waveform(filename)
    if channel:
        pos = np.array(wf.get_branch('Module{}/Asic{}/Channel{}/position'.format(
                                        module,asic,channel)))
        if bins:
            plt.hist(pos,bins=bins)
        else:
            max_bin = wf.get_n_samples()
            plt.hist(pos,bins=np.arange(max_bin))
        plt.xlabel('Position (ns)')
        plt.ylabel('Counts')
        plt.title('Position: Mod{}, ASIC{}, Ch{}'.format(
                  module,asic,channel))
        plt.minorticks_on()
    else:
        branch = wf.get_branch('Module{}/Asic{}'.format(module,asic))
        f, axarr = plt.subplots(4, 4, figsize=(10,10))
        for i in xrange(4):
            for j in xrange(4):
                index = int(i*4+j)
                pos = np.array(branch['Channel{}/position'.format(index)])
		if bins:
		    axarr[i, j].hist(pos,bins=bins)
		else:
                    max_bin = wf.get_n_samples()		   
		    axarr[i, j].hist(pos,bins=np.arange(max_bin))
                axarr[i, j].set_xlabel('Position (ns)')
                axarr[i, j].set_ylabel('Counts')
                axarr[i, j].set_title('Position: Ch{}'.format(channel),fontsize=12)
    wf.close_database()
