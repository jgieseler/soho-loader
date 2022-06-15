# Licensed under a 3-clause BSD style license - see LICENSE.rst

from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    pass  # package is not installed

import cdflib
import datetime as dt
import numpy as np
import pandas as pd

from sunpy.net import Fido
from sunpy.net import attrs as a
from sunpy.timeseries import TimeSeries


def resample_df(df, resample, pos_timestamp='center'):
    """
    Resample Pandas Dataframe
    """
    try:
        df = df.resample(resample).mean()
        if pos_timestamp == 'start':
            df.index = df.index
        else:
            df.index = df.index + pd.tseries.frequencies.to_offset(pd.Timedelta(resample)/2)
        # if pos_timestamp == 'stop' or pos_timestamp == 'end':
        #     df.index = df.index + pd.tseries.frequencies.to_offset(pd.Timedelta(resample))
    except ValueError:
        raise ValueError(f"Your 'resample' option of [{resample}] doesn't seem to be a proper Pandas frequency!")
    return df


def _get_metadata(dataset, path_to_cdf):
    """
    Get meta data from single cdf file
    So far only manually for 'SOHO_ERNE-HED_L2-1MIN' and 'SOHO_ERNE-LED_L2-1MIN'
    """
    metadata = []
    cdf = cdflib.CDF(path_to_cdf)
    if dataset=='SOHO_ERNE-HED_L2-1MIN' or dataset=='SOHO_ERNE-LED_L2-1MIN':
        if dataset=='SOHO_ERNE-HED_L2-1MIN':
            m = 'H'
        if dataset=='SOHO_ERNE-LED_L2-1MIN':
            m = 'L'
        metadata = {'He_E_label': cdf.varget('He_E_label')[0],
                    'He_energy': cdf.varget('He_energy'),
                    'He_energy_delta': cdf.varget('He_energy_delta'),
                    f'A{m}_LABL': cdf.varattsget(f'A{m}')['LABLAXIS'],
                    f'A{m}_UNITS': cdf.varattsget(f'A{m}')['UNITS'],
                    f'A{m}_FILLVAL': cdf.varattsget(f'A{m}')['FILLVAL'],
                    'P_E_label': cdf.varget('P_E_label')[0],
                    'P_energy': cdf.varget('P_energy'),
                    'P_energy_delta': cdf.varget('P_energy_delta'),
                    f'P{m}_LABL': cdf.varattsget(f'P{m}')['LABLAXIS'],
                    f'P{m}_UNITS': cdf.varattsget(f'P{m}')['UNITS'],
                    f'P{m}_FILLVAL': cdf.varattsget(f'P{m}')['FILLVAL'],
                    }

        channels_dict_df_He = pd.DataFrame(cdf.varget('He_E_label')[0], columns=['ch_strings'])
        channels_dict_df_He['lower_E'] = cdf.varget("He_energy")-cdf.varget("He_energy_delta")
        channels_dict_df_He['upper_E'] = cdf.varget("He_energy")+cdf.varget("He_energy_delta")
        channels_dict_df_He['DE'] = cdf.varget("He_energy_delta")
        # channels_dict_df_He['mean_E'] = np.sqrt(channels_dict_df_He['upper_E'] * channels_dict_df_He['lower_E'])
        channels_dict_df_He['mean_E'] = cdf.varget("He_energy")

        channels_dict_df_p = pd.DataFrame(cdf.varget('P_E_label')[0], columns=['ch_strings'])
        channels_dict_df_p['lower_E'] = cdf.varget("P_energy")-cdf.varget("P_energy_delta")
        channels_dict_df_p['upper_E'] = cdf.varget("P_energy")+cdf.varget("P_energy_delta")
        channels_dict_df_p['DE'] = cdf.varget("P_energy_delta")
        # channels_dict_df_p['mean_E'] = np.sqrt(channels_dict_df_p['upper_E'] * channels_dict_df_p['lower_E'])
        channels_dict_df_p['mean_E'] = cdf.varget("P_energy")

        metadata.update({'channels_dict_df_He': channels_dict_df_He})
        metadata.update({'channels_dict_df_p': channels_dict_df_p})
    return metadata


def soho_load(dataset, startdate, enddate, path=None, resample=None, pos_timestamp=None, max_conn=5):
    """
    Downloads CDF files via SunPy/Fido from CDAWeb for CELIAS, EPHIN, ERNE onboard SOHO

    Parameters
    ----------
    dataset : {str}
        Name of SOHO dataset:
        - 'SOHO_COSTEP-EPHIN_L3I-1MIN': SOHO COSTEP-EPHIN Level3 intensity 1 minute data
            https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#SOHO_COSTEP-EPHIN_L3I-1MIN
        - 'SOHO_CELIAS-PM_30S': SOHO CELIAS-PM 30 second data
            https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#SOHO_CELIAS-PM_30S
        - 'SOHO_CELIAS-SEM_15S': SOHO CELIAS-SEM 15 second data
            https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#SOHO_CELIAS-SEM_15S
        - 'SOHO_ERNE-LED_L2-1MIN': SOHO ERNE-LED Level2 1 minute data - VERY OFTEN NO DATA!
            https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#SOHO_ERNE-LED_L2-1MIN
        - 'SOHO_ERNE-HED_L2-1MIN': SOHO ERNE-HED Level2 1 minute data
            https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#SOHO_ERNE-HED_L2-1MIN
    startdate, enddate : {datetime or str}
        Datetime object (e.g., dt.date(2021,12,31) or dt.datetime(2021,4,15)) or "standard"
        datetime string (e.g., "2021/04/15") (enddate must always be later than startdate)
    path : {str}, optional
        Local path for storing downloaded data, by default None
    resample : {str}, optional
        Resample frequency in format understandable by Pandas, e.g. '1min', by default None
    pos_timestamp : {str}, optional
        Change the position of the timestamp: 'center' or 'start' of the accumulation interval, by default None
    max_conn : {int}, optional
        The number of parallel download slots used by Fido.fetch, by default 5

    Returns
    -------
    df : {Pandas dataframe}
        See links above for the different datasets for a description of the dataframe columns
    metadata : {dict}
        Dictionary containing different metadata, e.g., energy channels
    """
    if not (pos_timestamp=='center' or pos_timestamp=='start' or pos_timestamp is None):
        raise ValueError(f'"pos_timestamp" must be either None, "center", or "start"!')

    trange = a.Time(startdate, enddate)
    cda_dataset = a.cdaweb.Dataset(dataset)
    try:
        result = Fido.search(trange, cda_dataset)
        downloaded_files = Fido.fetch(result, path=path, max_conn=max_conn)  # use Fido.fetch(result, path='/ThisIs/MyPath/to/Data/{file}') to use a specific local folder for saving data files
        downloaded_files.sort()
        data = TimeSeries(downloaded_files, concatenate=True)
        df = data.to_dataframe()

        metadata = _get_metadata(dataset, downloaded_files[0])

        # remove this (i.e. following lines) when sunpy's read_cdf is updated,
        # and FILLVAL will be replaced directly, see
        # https://github.com/sunpy/sunpy/issues/5908
        df = df.replace(-1e+31, np.nan)  # for all fluxes
        df = df.replace(-2147483648, np.nan)  # for ERNE count rates

        # careful!
        # adjusting the position of the timestamp manually.
        # requires knowledge of the original time resolution and timestamp position!
        if pos_timestamp == 'center':
            if (dataset.upper() == 'SOHO_ERNE-HED_L2-1MIN' or
                    dataset.upper() == 'SOHO_ERNE-LED_L2-1MIN' or
                    dataset.upper() == 'SOHO_COSTEP-EPHIN_L3I-1MIN'):
                df.index = df.index+pd.Timedelta('30s')
            if dataset.upper() == 'SOHO_CELIAS-PM_30S':
                df.index = df.index+pd.Timedelta('15s')
        if pos_timestamp == 'start':
            if dataset.upper() == 'SOHO_CELIAS-SEM_15S':
                df.index = df.index-pd.Timedelta('7.5s')

        if isinstance(resample, str):
            df = resample_df(df, resample, pos_timestamp=pos_timestamp)
    except RuntimeError:
        print(f'Unable to obtain "{dataset}" data!')
        downloaded_files = []
        df = []
        metadata = []
    return df, metadata


def calc_av_en_flux_ERNE(df, channels_dict_df, avg_channels, species='p', sensor='HET'):
    """
    avg_channels : list of int, optional
        averaging channels m to n if [m, n] is provided (both integers), by default None
    """
    # calculation of total delta-E for averaging multiple channels:
    if len(avg_channels) > 1:
        DE_total = channels_dict_df.loc[avg_channels[0]:avg_channels[-1]]['DE'].sum()
    else:
        DE_total = channels_dict_df.loc[avg_channels[0]]['DE']

    # averaging of intensities:
    t_flux = 0
    for bins in range(avg_channels[0], avg_channels[-1]+1):
        if species.lower() in ['he', 'a', 'alpha']:
            t_flux = t_flux + df[f'A{sensor.upper()[0]}_{bins}'] * channels_dict_df.loc[bins]['DE']
        elif species.lower() in ['p', 'i', 'h']:
            t_flux = t_flux + df[f'P{sensor.upper()[0]}_{bins}'] * channels_dict_df.loc[bins]['DE']
    avg_flux = t_flux/DE_total

    # string lower energy
    energy_low = channels_dict_df.lower_E[avg_channels[0]]

    # string upper energy without .0 decimal but with ' keV' ending
    energy_up = channels_dict_df.upper_E[avg_channels[-1]]

    new_ch_string = f'{energy_low} - {energy_up} MeV'

    return avg_flux, new_ch_string
