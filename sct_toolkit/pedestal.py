from __future__ import division, print_function, absolute_import
import sys, os, pwd
import datetime
import warnings
import h5py
import numpy as np

try:
    import target_io
    import target_driver
except ImportError:
    pass

class pedestal(object):
    """ Class for handling pedestal databases """
    def __init__(self, ped_database=None):
	"""
        Initialize pedestal class

	Parameters
	----------
	ped_database : str, (optional)
	    If not 'None', loads an existing pedestal database to be used for
	    pedestal subtraction, etc. (default: None)

	"""
        self._generate_maps()
        self.ped_database = ped_database
        if ped_database:
            self._load_database(ped_database)

    def _add_branch(self, ped_waveform, module, asic, channel):
        """ create new branch to hold pedestal waveforms """
	branch_name = "Module{}/Asic{}/Channel{}".format(module ,asic, channel)
	branch = self.ped_database.create_group(branch_name)
	branch.create_dataset("pedestal", data=ped_waveform)

    def _average_events(self, mod_i, module, asic, channel):
        """ calculate average over all events in a given module, asic, and channel """
        ped_array = np.zeros(512*32)
        count_array = np.zeros(512*32)
	for ievt in xrange(self.n_events):
            if(ievt%1000==0):
                sys.stdout.write('\r')
                sys.stdout.write("[%-100s] %d%%" % ('='*int((ievt)*100.0/(self.n_events)),
                                (ievt)*100.0/(self.n_events)))
                sys.stdout.flush() 

	    rawdata = self.reader.GetEventPacket(ievt,(4*mod_i+asic)\
                      *16//self.channels_per_packet+channel//self.channels_per_packet)
	    self.packet.Assign(rawdata, self.reader.GetPacketSize())
	    block = int(self.packet.GetColumn()*8+self.packet.GetRow())
	    phase = int(self.packet.GetBlockPhase())
            wf = self.packet.GetWaveform(channel%self.channels_per_packet)
	    samples = map(wf.GetADC, self.waveform)
            cells = self._get_cell_ids(block, phase)
	    if np.amin(samples)>100:   #reject events with data spikes
		ped_array[cells]+=samples
		count_array[cells]+=1
            else:  #check cell-by-cell to reject data spike
                for index, cell in enumerate(cells):
                    if samples[index] > 100:
                        ped_array[cell]+=samples[index]
                        count_array[cell]+=1

        pedestal = np.nan_to_num(ped_array/count_array)
        ped_waveform = np.round(pedestal,decimals=2)
        self._add_branch(ped_waveform, module, asic, channel)
        sys.stdout.write('\n')

    def _calculate_pedestals(self):
        """ iterate through modules, asics, and channels to calculate all pedestals """
	for mod_i, module in enumerate(self.modules):
	    for asic in self.asics:
		for channel in self.channels:
                    print("Processing {} Events from Module {}, Asic {}, Channel {}".format(
                           self.n_events, module, asic, channel))
                    self._average_events(mod_i, module, asic, channel)

    def _check_type(self,data):
        """ check input type and map to integer(s) list """
        if isinstance(data,list):
            return map(int,data)
        elif isinstance(data,int):
            return [int(data)]
        else:
            raise TypeError('Input must be an integer or a list, got {}'.format(type(data)))

    def _generate_maps(self):
        """ generates block and cell id mappings """
        block_id_map = [0]
        for i in xrange(511):
            if block_id_map[-1]%2==0:
                next_block = (block_id_map[-1]+3)%512
                block_id_map.append(next_block)
            else:
                next_block = (block_id_map[-1]-1)%512
                block_id_map.append(next_block)

        cell_id_map = np.array([])
        block_cells = np.arange(32)
        for i in xrange(512):
            cell_id_map = np.append(cell_id_map,block_id_map[i]*32+block_cells)

        self.block_id_map = block_id_map
        self.cell_id_map = cell_id_map.astype(int)

    def _get_cell_ids(self, block, phase):
        """ 
        convert block to cell id, shift to account for phase, return cell ids   
        """
        first_cell = self.block_id_map.index(int(block))*32
        cells = np.arange(first_cell,first_cell+self.n_samples,1)+phase
        shifted_cells = np.mod(cells,512*32)
        return self.cell_id_map[shifted_cells]

    def _get_pedestal(self, module, asic, channel):
        """ return pedestal array """
        ped_group = self.ped_database['Module{}/Asic{}/Channel{}'.format(module,asic,channel)]
        return np.array(ped_group['pedestal'])

    def _load_database(self,name):
        """ load an existing hdf5 pedestal database """
        try:
            self.ped_database = h5py.File(name,"r",libver='latest')
            self.n_samples = self.ped_database.attrs['waveform_length']
            self.modules = self.ped_database.attrs['modules']
            self.asics = self.ped_database.attrs['asics']
            self.channels = self.ped_database.attrs['channels']
        except IOError:
            raise IOError("file '{}' not found. Check name and/or path ".format(name))

    def _new_database(self, name, check_overwrite):
        """ generates a new hdf5 database """
        if check_overwrite:
	    if os.path.isfile(name):
		print("The file '{}' already exists.".format(name))
		answers = {"yes","no"}
		choice = None
		while True:
		    choice = raw_input("Would you like to overwrite it? (yes/no) ").lower()
		    if choice in answers:
			break
		    else:
			print("Not an acceptable input, try again!")
		if choice == 'no':
		    raise SystemExit('exiting...')

        self.ped_database = h5py.File(name,"w",libver='latest')

    def _set_attributes(self):
        """ assign metadata attributes to database """
        self.ped_database.attrs['name'] = str(self.ped_database.filename)
        self.ped_database.attrs['date'] = str(datetime.datetime.today())
        self.ped_database.attrs['created_by'] = pwd.getpwuid(os.getuid()).pw_name
        self.ped_database.attrs['comments'] = self.comments
        self.ped_database.attrs['run_path'] = self.filename
        self.ped_database.attrs['run'] = self.run_number
        self.ped_database.attrs['modules'] = self.modules
        self.ped_database.attrs['asics'] = self.asics
        self.ped_database.attrs['channels'] = self.channels
        self.ped_database.attrs['channels_per_packet'] = self.channels_per_packet
        self.ped_database.attrs['packet_size'] = self.packet_size
        self.ped_database.attrs['waveform_length'] = self.n_samples
        self.ped_database.attrs['num_events'] = self.n_events
        self.ped_database.attrs['keys'] = "pedestal"
        self.ped_database.attrs['structure'] = "Module#/Asic#/Channel#/'keys'"

    def _set_channels_per_packet(self):
        """ assign channels per packet  """
	self.channels_per_packet = int((0.5*self.packet_size-10.)/(self.n_samples+1.))

    def _set_data_packet_parameters(self):
        """ assigns data packet characteristics """
	self.reader = target_io.EventFileReader(self.filename)
	self.n_events = self.reader.GetNEvents()
	rawdata = self.reader.GetEventPacket(0,0)
	self.packet = target_driver.DataPacket()
	self.packet_size = self.reader.GetPacketSize()
	self.packet.Assign(rawdata, self.packet_size)
	wf = self.packet.GetWaveform(0)
	self.n_samples = wf.GetSamples()
        self.waveform = np.arange(self.n_samples,dtype=int)
	self._set_channels_per_packet()

    def _set_run_file_path(self):
        """ assigns file path for run number """
	self.filename = "{}/target5and7data/run{}.fits".format(os.environ['HOME'],
			 self.run_number)
	if not os.path.isfile(self.filename):
	    new_path = "{0}/target5and7data/runs_{1}0000_"\
		       "through_{1}9999/".format(os.environ['HOME'],
			str(self.run_number)[:-4])
	    self.filename = new_path+"run{}.fits".format(self.run_number)
	    if not os.path.isfile(self.filename):
		raise IOError("File run{}.fits cannot be located".format(self.run_number))

    def _set_run_parameters(self, run_number, modules, asics, channels, filepath, comments):
        """ assign parameters to be used for constructing pedestal database """
        self.run_number = int(run_number)
        print('Creating pedestal database from run {}'.format(self.run_number))
        self.modules = self._check_type(modules)
        if asics:
            self.asics = self._check_type(asics)
        if channels:
            self.channels = self._check_type(channels)
        if filepath:
            self.filename = str(filepath)
            if not os.path.isfile(self.filename):
                raise IOError("Invalid file path: {} cannot be located".format(self.filename))
        if not filepath:
            self._set_run_file_path()
        self.comments = str(comments)

    def close_database(self):
        """ close currently loaded/created pedestal database """
        if isinstance(self.ped_database, h5py.File):
            self.ped_database.close()
        else:
            warnings.warn("No database currently open!",stacklevel=2)

    def get_attributes(self,verbose=True):
        """Get database attributes 

        Parameters
        ----------
        verbose : bool
            If True, prints a list of database attributes (default: True).

        Returns
        ----------
        list of tuples

        """
        attributes = [tuple([str(key), val]) for key, val in sorted(self.ped_database.attrs.items())]
        if verbose:
            print('\n'.join('{}: {}'.format(key, val) for key, val in attributes))
        return attributes

    def get_block_id_map(self):
        """ 
        Gets the block id map 

        Returns
        ----------
        numpy.ndarray

        """
        return np.array(self.block_id_map,dtype=int)

    def get_branch(self,branch_name):
        """ 
        Get object for a specified branch

        Parameters
        ----------
        branch_name : str 
            name of branch

        Returns
        ----------
        database branch object

        """
        if isinstance(self.ped_database, h5py.File):
            return self.ped_database.get(str(branch_name))
        else:
            warnings.warn("No database currently open!",stacklevel=2)

    def get_branches(self, verbose=False, filter_by=None):
        """ 
        Get a list of branch names for each group/subgroup in database

        Parameters
        ----------
        verbose : bool
            If True, print list of branch names (default: False)
        filter_by : list(str), (optional)
            Filter branches matching the specified pattern(s), ex. single ["Module118/Asic10/"] 
            or mutltiple ["Module118","Channel10"] (default: None). Note: case sensitive

        Returns
        ----------
        list of strings

        """
        if isinstance(self.ped_database, h5py.File):
            branches = set()
            self.ped_database.visit(branches.add)
            if filter_by:
                branches = [b for b in branches if all([f in b for f in set(filter_by)])]
            if verbose:
                print('\n'.join(b for b in branches))
            return map(str,branches)
        else:
            warnings.warn("No database currently open!",stacklevel=2)

    def get_cell_id_map(self):
        """ 
        Get the cell id map 

        Returns
        ----------
        numpy.ndarray

        """
        return self.cell_id_map

    def get_database(self):
        """ 
        Get currently loaded pedestal database 

        Returns
        ----------
        h5py database

        """
        if isinstance(self.ped_database, h5py.File):
            return self.ped_database
        else:
            warnings.warn("No database currently open!",stacklevel=2)

    def get_database_name(self):
        """ 
        Get name of current pedestal database 

        Returns
        ----------
        str

        """
        if isinstance(self.ped_database, h5py.File):
            return str(self.ped_database.filename)
        else:
            warnings.warn("No database currently open!",stacklevel=2)

    def get_pedestal_waveform(self, module, asic, channel, block=None, phase=None):
        """
        Get the pedestal waveform for a given module, asic, and channel.

        Parameters
        ----------
        module : int
            module number
        asic : int
            asic number
        channel : int
            channel number
        block : int (optional)
            block number (default: None)
        phase : int (optional)
            phase number (default: None)

        Returns
        ----------
        numpy.ndarray
        
        """
        pedestal = self._get_pedestal(module, asic, channel)
        if block and phase:
            cells = self._get_cell_ids(block, phase)
            ped_values = pedestal[cells]
            return np.array(ped_values)
        else:
            return np.array(pedestal)

    def make_pedestal_database(self, ped_name, run_number, modules, 
                               asics=range(4),channels=range(16), filepath=None, 
                               check_overwrite=True, comments=None):
        """ 
        Create a new pedestal database 

        Parameters
        ----------
        ped_name : str 
            Full name and path for new database
        run_number : int  
            Run number to be used for constructing pedestal database
        modules : int 
            Ordered list of module numbers used during data taking; ex [123,124,...]
            Note: list must make the order that was used during data taking
        asics : int 
            List of asics used in run_number (default: range(4))
        channels : list of ints
            List of channels used in run_number (default: range(16))
        filepath : str (optional) 
            if data is not in target5and7data, specify alternate path and name (default: None)
        check_overwrite : bool 
            if True, checks if ped_name exists before overwriting it (default: True)
        comments : str (optional)
            Comments to be added as metadata to database

        """
	#Check if remote data directory is mounted
	if os.path.ismount(os.environ['HOME']+'/target5and7data')==True:
	    print("Output-directory is mounted")
	else:
	    print("Cannot connect to the remote output directory!")
	    print("Make sure '{}/target5and7data' is mounted!".format(os.environ['HOME']))
	    raise SystemExit

        self._set_run_parameters(run_number, modules, asics=asics, channels=channels, 
                                 filepath=filepath, comments=comments)
        self._new_database(ped_name, check_overwrite)
        self._set_data_packet_parameters()
        self._calculate_pedestals()
        self._set_attributes()
        self.close_database()
        print("Database successfully created, saving to {}".format(ped_name))

