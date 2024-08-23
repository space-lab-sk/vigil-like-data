from extractDataSrc.Hapi import get_hapi_data
from extractDataSrc.MissionsOperationalTime import check_operational_time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.io as pio

class InSitu:
    def __init__(self, start_datetime: str, stop_datetime: str) -> None:
        self.start_date = start_datetime
        self.stop_date = stop_datetime


    def extract_data(self, instrument: str, make_png: bool=False, verbose: bool=False, custom_target_dir: str=None):

        # ------------extract data-----------------
        server = 'https://cdaweb.gsfc.nasa.gov/hapi'
        dataset = ""
        parameter = ""

        if instrument == "V_p":
            dataset = "SOHO_CELIAS-PM_30S"
            parameter = 'V_p'
            mission = "soho"
            check_operational_time("soho_celias", str(self.start_date))
        elif instrument == "N_p":
            dataset = "SOHO_CELIAS-PM_30S"
            parameter = 'N_p'
            mission = "soho"
            check_operational_time("soho_celias", str(self.start_date))
        elif instrument == "B_z":
            dataset = "WI_H0_MFI@0"
            parameter = "BGSM"
            mission = "wind"
            check_operational_time("wind_mfi", str(self.start_date))
        else:
            raise ValueError("product should be \"V_p\" for proton velocity or \"N_p\" for proton density or \"B_z\" for magnetic field")
        
        hapi_data = get_hapi_data(server, dataset, parameter, self.start_date, self.stop_date)
        
        # ------------transform data-----------------
        if verbose:
            print("transforming data...")
        transformed_data_frame = None
        if instrument == "V_p" or instrument == "N_p":
            transformed_data_frame = self._transform_proton_data(hapi_data, instrument)
        else:
            transformed_data_frame = self._transform_magnetic_field_data(hapi_data, instrument)

        # ------------load data to csv-----------------
        if verbose:
            print("saving data...")
        date_obj = datetime.strptime(self.start_date, "%Y-%m-%d %H:%M:%S")
        new_date = date_obj + timedelta(days=10)
        event_time = new_date.strftime("%Y%m%d")

        if custom_target_dir:
            target_dir = custom_target_dir if custom_target_dir.endswith("/") else custom_target_dir + "/"
        else:
            target_dir = "data_processed/in_situ/"
            
        filename = f"{event_time}_{mission}_{instrument}.csv"
        destination_filename = target_dir + filename

        transformed_data_frame.to_csv(destination_filename, index=False)

        # ------------save time-series into png (optional)-----------------

        if make_png:
            if verbose:
                print("creating png...")
            plot_title = f"{instrument} in time"
            fig = px.scatter(transformed_data_frame, x="Time", y=instrument, title=plot_title)
            fig.update_traces(marker=dict(size=3))
            png_destination_filename = self._change_extension_to_png(destination_filename, "png")
            pio.write_image(fig, png_destination_filename, format="png")
        
        if verbose:
            print("Done")


    def _transform_proton_data(self, hapi_data: np.ndarray, instrument: str) -> pd.DataFrame:
        """
        Transforms raw proton data from HAPI into a Pandas DataFrame.

        Filters out invalid records, structures the data appropriately, and creates 
        a DataFrame ready for analysis.

        Args:
            hapi_data (np.ndarray): A NumPy array containing the raw HAPI data.
            instrument (str): The name of the instrument corresponding to the proton data.

        Returns:
            pd.DataFrame: A Pandas DataFrame with columns 'Time' (datetime) and the 
                        instrument name containing the proton data values.
        """
        
        # clean data of records filled with -1.0E31
        filtered_data = [record for record in hapi_data if record[1] != -1.0E31]
        filtered_data = np.array(filtered_data, dtype=[('Time', 'S22'), (instrument, '<f8')])

        df = pd.DataFrame(data=filtered_data)
        df['Time'] = df['Time'].str.decode('utf-8')
        df['Time'] = pd.to_datetime(df['Time'], format="%Y-%m-%dT%H:%M:%S.00")

        return df
    

    def _transform_magnetic_field_data(self, hapi_data: np.ndarray, instrument: str) -> pd.DataFrame:
        """
        Transforms raw magnetic field data retrieved from HAPI into a Pandas DataFrame.

        Processes the data to filter out invalid records, extracts the relevant magnetic 
        field component, and prepares it for use in a DataFrame structure.

        Args:
            hapi_data (np.ndarray): A NumPy array containing the raw HAPI data.
            instrument (str): The name of the instrument corresponding to the magnetic field data.

        Returns:
            pd.DataFrame: A Pandas DataFrame with columns 'Time' (datetime) and the 
                        instrument name containing the magnetic field values.
        """

        filtered_data = [record for record in hapi_data if record[1][2] != -1.0E31]

        bz_data = []
        for record in filtered_data:
            row = []
            row.append(record[0])
            row.append(round(record[1][2], 3))
            bz_data.append(row)

        df = pd.DataFrame(data=bz_data, columns=["Time", instrument])
        df['Time'] = df['Time'].str.decode('utf-8')
        df['Time'] = pd.to_datetime(df['Time'], format="%Y-%m-%dT%H:%M:%S.000Z")

        return df
        

    def _change_extension_to_png(self, filename: str, new_extension: str):
        """
        Changes the extension of a filename in a string to a new extension.

        Args:
            filename: The filename as a string.
            new_extension: The new extension (e.g., "png").

        Returns:
            The filename string with the new extension.
        """
        dot_index = filename.rfind(".")

        if dot_index != -1 and filename[dot_index:].lower() == ".csv":
            new_filename = filename[:dot_index] + f".{new_extension}"
        else:
            raise ValueError("Filename does not have a .csv extension")

        return new_filename