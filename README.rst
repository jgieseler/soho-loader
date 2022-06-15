soho-loader
===============

Python data loader for SOHO charged particle instruments. At the moment provides released data obtained by SunPy through CDF files from CDAWeb for the following datasets:

-   ``'SOHO_CELIAS-PM_30S'``: SOHO CELIAS-PM 30 second data (`Info <https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#SOHO_CELIAS-PM_30S>`_)
-   ``'SOHO_CELIAS-SEM_15S'``: SOHO CELIAS-SEM 15 second data (`Info <https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#SOHO_CELIAS-SEM_15S>`_)    
-   ``'SOHO_COSTEP-EPHIN_L3I-1MIN'``: SOHO COSTEP-EPHIN Level3 intensity 1 minute data (`Info <https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#SOHO_COSTEP-EPHIN_L3I-1MIN>`_)
-   ``'SOHO_ERNE-LED_L2-1MIN'``: SOHO ERNE-LED Level2 1 minute data (`Info <https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#SOHO_ERNE-LED_L2-1MIN>`_)
-   ``'SOHO_ERNE-HED_L2-1MIN'``: SOHO ERNE-HED Level2 1 minute data (`Info <https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#SOHO_ERNE-HED_L2-1MIN>`_)


Disclaimer
----------
This software is provided "as is", with no guarantee. It is no official data source, and not officially endorsed by the corresponding instrument teams. Please always refer to the instrument descriptions before using the data!


Installation
------------

soho_loader requires python >= 3.6 and SunPy >= 3.1.3

It can be installed from this repository using pip:

.. code:: bash

    pip install git+https://github.com/jgieseler/soho-loader

**Note:** Windows users might `need to install git <https://github.com/git-guides/install-git>`_ for this to work!

Usage
-----

The standard usecase is to utilize the ``soho_load`` function, which
returns Pandas dataframe(s) of the measurements.

.. code:: python

   from soho_loader import soho_load
   import datetime as dt

   df, meta = soho_load(dataset="SOHO_ERNE-HED_L2-1MIN",
                        startdate=dt.datetime(2021, 4, 16),
                        enddate="2021/04/20",
                        path=None,
                        resample="1min",
                        pos_timestamp=None)

Input
~~~~~

-  ``dataset``: ``'SOHO_CELIAS-PM_30S'``, ``'SOHO_COSTEP-EPHIN_L3I-1MIN'``, ``'SOHO_COSTEP-EPHIN_L3I-1MIN'``, ``'SOHO_ERNE-LED_L2-1MIN'``, or ``'SOHO_ERNE-HED_L2-1MIN'``. See above for explanation.
-  ``startdate``, ``enddate``: datetime object or "standard" datetime string
-  ``path``: String, optional. Local path for storing downloaded data, e.g. ``path='data/wind/3dp/'``. By default ``None``. Default setting saves data according to `sunpy's Fido standards <https://docs.sunpy.org/en/stable/guide/acquiring_data/fido.html#downloading-data>`_.
-  ``resample``: Pandas frequency (e.g., ``'1min'`` or ``'1h'``), or ``None``, optional. Frequency to which the original data is resamepled. By default ``None``.
-  ``pos_timestamp``: String, optional. Change the position of the timestamp: ``'center'`` or ``'start'`` of the accumulation interval, by default ``None``.
-  ``max_conn``: Integer, optional. The number of parallel download slots used by ``Fido.fetch``, by default ``5``.

Return
~~~~~~

-  Pandas dataframe and dictionary of metadata (e.g., energy channels). See info links above for the different datasets for a description of the dataframe columns.


Data folder structure
---------------------

If no `path` argument is provided, all data files are automatically saved in a SunPy subfolder of the current user home directory.


Combine intensitiy for multiple energy channels (ERNE only)
-----------------------------------------------------------

For ERNE measurements, it's possible to combine the intensities of multiple adjacent energy channels with the function ``calc_av_en_flux_ERNE``. It returns a Pandas Dataframe with the arithmetic mean of all intensities and a string providing the corresponding energy range. The following example demonstrates how to build an average channel of ERNE proton energy channels 2 to 8. 


.. code:: python

    from soho_loader import soho_load, calc_av_en_flux_ERNE
    
    # first, load original data:
    df, meta = soho_load(dataset="SOHO_ERNE-HED_L2-1MIN",
                         startdate="2021/04/16",
                         enddate="2021/04/20",
                         path=None,
                         resample="1min",
                         pos_timestamp=None)

    # define energy channel range that should be combined:
    combine_channels = [2, 8]
    erne_avg_int, erne_avg_chstring = calc_av_en_flux_ERNE(df, 
                                                           meta['channels_dict_df_p'],
                                                           combine_channels,
                                                           species='p',
                                                           sensor='HET')
    print(erne_avg_chstring)


License
-------

This project is Copyright (c) Jan Gieseler and licensed under
the terms of the BSD 3-clause license. This package is based upon
the `Openastronomy packaging guide <https://github.com/OpenAstronomy/packaging-guide>`_
which is licensed under the BSD 3-clause license. See the licenses folder for
more information.

Acknowledgements
----------------

The development of this software has received funding from the European Union's Horizon 2020 research and innovation programme under grant agreement No 101004159 (SERPENTINE).
