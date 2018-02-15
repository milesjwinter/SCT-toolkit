.. _example1:

******************
Pedestal Databases
******************

A pedestal database can be created with a few simple commands. Note: you must be on a machine with target_driver and target_io installed. 

.. code:: python

    from sct_toolkit import pedestal

    #specify the run to use for the pedestal database
    run_number = 322342
    ped_name = 'runFiles/pedestal_database_{}.h5'.format(run_number)

    #define list of module numbers (must be same order as when data was taken)
    modules = [118,125,126,119,108,121,110,128,123,124,112,100,111,114,107]
    ped = pedestal()
    ped.make_pedestal_database(ped_name, run_number, modules)
