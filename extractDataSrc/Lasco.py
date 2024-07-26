from extractDataSrc.Hapi import get_hapi_data
import os
from IPython.display import clear_output
import numpy as np
import pandas as pd
from datetime import datetime
from hvpy import createScreenshot, DataSource, create_layers
import time
from tqdm import tqdm
from extractDataSrc.MissionsOperationalTime import check_operational_time


class Lasco:
    def __init__(self, start_datetime: str, stop_datetime: str) -> None:
        self.start = start_datetime
        self.stop = stop_datetime


    def extract_data(self, detector: str, skip_images: int=0, verbose: bool=True, custom_target_dir: str=None):

        # ------------extract data-----------------
        server = 'https://api.helioviewer.org/hapi/Helioviewer/hapi'
        # dataset is determined bellow
        dataset = ""
        parameters = 'url'

        scale = None
        hvpy_layer = None
        
        if detector == "c3":
            dataset = "LASCO_C3"
            scale = 56
            hvpy_layer = DataSource.LASCO_C3
            check_operational_time("soho_lasco_c3", self.start)
        elif detector == "c2":
            dataset = 'LASCO_C2'
            scale = 11.5
            hvpy_layer = DataSource.LASCO_C2
            check_operational_time("soho_lasco_c2", self.start)
        else:
            raise ValueError("product should be \"c2\" or \"c3\"")
        
        # ------------transform data-----------------
        hapi_data = get_hapi_data(server, dataset, parameters, self.start, self.stop)

        if custom_target_dir:
            target_dir = custom_target_dir if custom_target_dir.endswith("/") else custom_target_dir + "/"
        else:
            target_dir = f"data_processed/lasco/{detector}/"

        df = self._transform_data(hapi_data)

        # ------------load data (save)-----------------
        
        self.create_screenshot(df, target_dir, hvpy_layer, detector, scale, skip_images, verbose=verbose)



    def create_screenshot(self, df: pd.DataFrame, target_dir: str, hvpy_layer: DataSource, detector: str, scale: float=None, skip_images=0, verbose=True):
        images_count = len(df)

        if verbose:
            iterable = tqdm(range(images_count), desc="Creating Screenshots", unit="image")
        else:
            iterable = range(images_count) 

        for index in iterable:

            if index < skip_images:
                if verbose:
                    iterable.write("Skipping image...")
                continue

            time_str = str(df.iloc[index]['Time']) 
            original_datetime = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            filename = self._extract_filename(time_str, detector)
            save_path = target_dir + filename

            for attempt in range(1, 4):
                try:
                    createScreenshot(
                        date=datetime(original_datetime.year, original_datetime.month, original_datetime.day, original_datetime.hour, original_datetime.minute),
                        layers=create_layers([(hvpy_layer, 100)]),
                        imageScale=scale,
                        x0=0,
                        y0=0,
                        width=1024,
                        height=1024,
                        filename=save_path,
                        overwrite=True
                    )
                except Exception as e:
                    if verbose:
                        iterable.write(f"Screenshot creation on index {index} failed: {e}. Attempting: {attempt} / 4")
                    time.sleep(60)
                else:
                    break


    def _transform_data(self, data: np.ndarray) -> pd.DataFrame:
        """This function creates dataframe from filtered numpy data downloaded from HAPI.
        """

        filtered_data = np.array(data, dtype=[('Time', 'S22'), ('url', '<U255')])
        df = pd.DataFrame(data=filtered_data)
        df['Time'] = df['Time'].str.decode('utf-8')
        df['Time'] = pd.to_datetime(df['Time'], format="%Y-%m-%dT%H:%M:%SZ")

        return df
    

    def _extract_filename(self, original_file_link: str, detector: str) -> str:
        """changes Helioviewer .fits name convention to VSO naming convention. 
        Changin to VSO naming convention will provide ability to synergy with data from Adam's Bachelor Thesis if needed

        Args:
            original_file_link (str): Helioviewer .fits naming convention e.g. 2001_03_21__00_00_01_942__SOHO_MDI_MDI_magnetogram.jp2

        Returns:
            str: VSO naming convention e.g. 20020201_0000_mdimag_1024
        """

        resolution = "1024"
        instrument = "lasco"
        channel = detector

        filename = original_file_link.split(' ')

        date = filename[0].replace("-", "")
        time = filename[1].replace(":", "")[:4] 

        return f"{date}_{time}_{instrument}{channel}_{resolution}"
