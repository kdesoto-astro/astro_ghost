import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.coordinates import Angle
import os
import sys
from datetime import datetime
import pickle
from collections import Counter

def build_ML_df(dic, hostDF, transientDF):
    """Consolidates the final host associations into a single dataframe.

    :param dic: key,value pairs of transient name, list of associated host PS1 objIDs
        (should be one-to-one except where the association failed).
    :type dic: dictionary
    :param hostDF: PS1 properties for all host galaxies.
    :type hostDF: Pandas DataFrame
    :param transientDF: Pandas DataFrame
    :type transientDF: TNS properties for all transients.
    :return: The final consolidated DF of transient & host galaxy properties.
    :rtype: Pandas DataFrame
    """

    hostDF = hostDF.reset_index(drop=True)
    hostDF = hostDF.drop_duplicates(subset=['objID'],ignore_index=True)
    hostDF["TransientClass"] = ""
    hostDF["TransientName"] = ""
    colNames = set(transientDF.columns.values)
    colNames.remove('HostName')
    colNames.remove('RA')
    colNames.remove('DEC')
    colNames.remove('Obj. Type')
    for name, host in dic.items():
        # only do matching if there's a found host
        chosenHost = ""
        if (host == host):
            if isinstance(host, np.ndarray):
                if host:
                    chosenHost = host[0]
            else:
                chosenHost = host
        if chosenHost:
            #find host in df
            idx = hostDF['objID'] == chosenHost
            idx_transient = transientDF['Name'] == str(name)
            if hostDF.loc[idx, "TransientClass"].values[0] != "":
                print("Found a double!")
                hostDF = hostDF.append([hostDF[idx]], ignore_index=True)
                idx = hostDF.index[-1]
            hostDF.loc[idx, "TransientClass"] = transientDF.loc[idx_transient, 'Obj. Type'].to_string(index=False).strip()
            hostDF.loc[idx, "TransientName"] = transientDF.loc[idx_transient, 'Name'].to_string(index=False).strip()
            transCoord = SkyCoord(transientDF.loc[idx_transient, 'RA'], transientDF.loc[idx_transient, 'DEC'], unit=(u.deg, u.deg))
            if len(transCoord) > 1:
                transCoord = transCoord[0]
            hostDF.loc[idx, "TransientRA"] = transCoord.ra.deg
            hostDF.loc[idx, "TransientDEC"] = transCoord.dec.deg
            #adding all the extra columns that we haven't added yet
            for val in colNames:
                hostDF.loc[idx, "Transient"+val.replace(" ", "")] = transientDF.loc[idx_transient, val].to_string(index=False).strip()
    hostDF = hostDF[hostDF["TransientClass"] != ""]
    hostDF = hostDF.reset_index(drop=True)
    return hostDF
