This package is not maintained any more! Please use https://github.com/serpentine-h2020/SEPpy instead!
======================================================================================================

soho-loader
===============

Python data loader for SOHO charged particle instruments. At the moment provides released data obtained by SunPy through CDF files from CDAWeb for the following datasets:

-   ``'SOHO_CELIAS-PM_30S'``: SOHO CELIAS-PM 30 second data (`Info <https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#SOHO_CELIAS-PM_30S>`_)
-   ``'SOHO_CELIAS-SEM_15S'``: SOHO CELIAS-SEM 15 second data (`Info <https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#SOHO_CELIAS-SEM_15S>`_)    
-   ``'SOHO_COSTEP-EPHIN_L2-1MIN'``: SOHO COSTEP-EPHIN Level2 intensity 1 minute data (`Info <https://www.ieap.uni-kiel.de/et/ag-heber/costep/data.php>`_) [1]_
-   ``'SOHO_COSTEP-EPHIN_L3I-1MIN'``: SOHO COSTEP-EPHIN Level3 intensity 1 minute data (`Info <https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#SOHO_COSTEP-EPHIN_L3I-1MIN>`_)
-   ``'SOHO_ERNE-LED_L2-1MIN'``: SOHO ERNE-LED Level2 1 minute data (`Info <https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#SOHO_ERNE-LED_L2-1MIN>`_)
-   ``'SOHO_ERNE-HED_L2-1MIN'``: SOHO ERNE-HED Level2 1 minute data (`Info <https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#SOHO_ERNE-HED_L2-1MIN>`_)

.. [1] SOHO COSTEP-EPHIN Level2 intensity 1 minute data is directly obtained through ASCII files from the `server of the instrument team <http://ulysses.physik.uni-kiel.de/costep/level2/>`_, not via SunPy/CDAWeb.

Disclaimer
----------
This software is provided "as is", with no guarantee. It is no official data source, and not officially endorsed by the corresponding instrument teams. Please always refer to the instrument descriptions before using the data!


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
                        pos_timestamp=None,
                        max_conn=5)

Input
~~~~~

-  ``dataset``: ``'SOHO_CELIAS-PM_30S'``, ``'SOHO_CELIAS-SEM_15S'``, ``'SOHO_COSTEP-EPHIN_L2-1MIN'``, ``'SOHO_COSTEP-EPHIN_L3I-1MIN'``, ``'SOHO_ERNE-LED_L2-1MIN'``, or ``'SOHO_ERNE-HED_L2-1MIN'``. See above for explanation.
-  ``startdate``, ``enddate``: datetime object or "standard" datetime string
-  ``path``: String, optional. Local path for storing downloaded data, e.g. ``path='data/soho/'``. By default ``None``. Default setting saves data according to `sunpy's Fido standards <https://docs.sunpy.org/en/stable/guide/acquiring_data/fido.html#downloading-data>`_. The default setting can be changed according to the corresponding `sunpy documentation <https://docs.sunpy.org/en/stable/guide/customization.html>`_, where the setting that needs to be changed is named ``download_dir`` (e.g., one could set it to a shared directory on a multi-user system).
-  ``resample``: Pandas frequency (e.g., ``'1min'`` or ``'1h'``), or ``None``, optional. Frequency to which the original data is resamepled. By default ``None``.
-  ``pos_timestamp``: String, optional. Change the position of the timestamp: ``'center'`` or ``'start'`` of the accumulation interval, by default ``None``.
-  ``max_conn``: Integer, optional. The number of parallel download slots used by ``Fido.fetch``, by default ``5``.

Return
~~~~~~

-  Pandas dataframe and dictionary of metadata (e.g., energy channels). See info links above for the different datasets for a description of the dataframe columns.


Caveats
-------
From the **SOHO COSTEP-EPHIN Level2 intensity 1 minute data** (``'SOHO_COSTEP-EPHIN_L2-1MIN'``), only electron data is returned at the moment. The proton and Helium measurements are not provided, see https://github.com/jgieseler/soho-loader/issues/3 for more details.


Data folder structure
---------------------

- COSTEP-EPHIN Level2: All data files are automatically saved in a ``data`` subfolder in the current working directory if ``path`` is not defined.
- All other instruments: All data files are automatically saved in a ``sunpy`` subfolder of the current user home directory if ``path`` is not defined.


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
