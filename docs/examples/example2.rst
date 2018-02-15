.. _example2:

******************
Waveform Databases
******************

The Simplest Case
-----------------

A new waveform database can be created with a few simple commands using when using `write_events()`. If a pedestal database is specified, `write_events()` will automatically perform pedestal subtraction and calculate the charge, amplitude, and position for each event. If no pedestal database is provided, the created database will only contain raw waveform data. 

.. code:: python

    from sct_toolkit import waveform

    #define list of module numbers (must be same order as when data was taken)
    modules = [118,125,126,119,108,121,110,128,123,124,112,100,111,114,107]

    #Create a new waveform database 
    wf = waveform()
    wf.write_events(run_number=322344, 
                    modules=modules, 
                    ped_name='pedestal_database_322342.h5')


Note: you must be on a machine with target_driver and target_io installed to use `write_events()`.

The Simplest Case
-----------------
