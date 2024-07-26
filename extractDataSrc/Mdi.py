from extractDataSrc.Hapi import get_hapi_data
import os
import requests
from IPython.display import clear_output
import cv2
import glob
from hvpy import createScreenshot, DataSource, create_layers
from datetime import datetime
import time
from tqdm import tqdm
from extractDataSrc.MissionsOperationalTime import check_operational_time

class Mdi:
    def __init__(self, start_datetime: str, stop_datetime: str) -> None:
        self.start = start_datetime
        self.stop = stop_datetime


    def extract_data(self, product: str, quality_check: bool=True, verbose: bool=True, custom_target_dir: str=None):
        
        # ------------extract data-----------------
        server = 'https://api.helioviewer.org/hapi/Helioviewer/hapi'
        # dataset is determined bellow
        dataset = ""
        parameters = 'url'
        hvpy_layer: DataSource = None
        

        if product == "mag":
            dataset = "MDI_MAG"
            hvpy_layer = DataSource.MDI_MAG
            check_operational_time("soho_mag", self.start)
        elif product == "con":
            dataset = "MDI_INT"
            hvpy_layer = DataSource.MDI_INT
            check_operational_time("soho_con", self.start)
        else:
            raise ValueError("product should be \"mag\" for magnetogram or \"con\" for continuum")
        
        hapi_data = get_hapi_data(server, dataset, parameters, self.start, self.stop)
        images_count = len(hapi_data)
        if custom_target_dir:
            target_dir = custom_target_dir if custom_target_dir.endswith("/") else custom_target_dir + "/"
        else:
            target_dir = f"data_processed/mdi/{product}/"

        # ------------load data (save)-----------------
        images_count = len(hapi_data)

        if verbose:
            iterable = tqdm(hapi_data, total=images_count, desc="Downloading", unit="file")
        else:
            iterable = hapi_data 

        for count, item in enumerate(iterable):
            filename = self._extract_filename(item[1])
            self._download_file_from_hvpy(filename, target_dir, hvpy_layer, count)
            
            if verbose:
                iterable.update(1)
                 


        # ------------check for faulty images (optional)------------
        if quality_check:
            src_dir = target_dir + "*.png"
            images_paths = glob.glob(src_dir)

            for count, image_path in enumerate(images_paths):
                
                if verbose:
                    print(f"checking quality... {count} / {images_count}")
                if self._is_mdi_image_bad(image_path):
                    os.remove(image_path)
                
                clear_output(wait=True)


    def _download_file_from_hvpy(self, filename: str, target_dir: str, hvpy_layer: DataSource, count: int):
        """creates screenshot via hvpy high-level API for Helioviewer 

        Args:
            filename (str): filename for image to save
            target_dir (str): target directory where to save image
            hvpy_layer (DataSource): color layer depends on DataSource  
            count (int): number of images to download.
        """


        datetime_object = self._string_to_datetime(filename)
        for attempt in range(1, 4):
            try:
                screenshot_location = createScreenshot(
                    date=datetime_object,
                    layers=create_layers([(hvpy_layer, 100)]),
                    imageScale=2.57,
                    x0=0,
                    y0=0,
                    width=1024,
                    height=1024,
                    filename=target_dir + filename,
                    overwrite=True
                )
            except Exception as e:
                print(f"Screenshot creation on index {count} failed: {e}")
                print(f"attempting: {attempt} / 4")
                time.sleep(60)
            else:
                break


    def _string_to_datetime(self, date_string):
        """Converts a string in the format YYYYMMDD_HHMM to a datetime object.

        Args:
            date_string: A string representation of a date and time in the format YYYYMMDD_HHMM.

        Returns:
            A datetime object representing the date and time in the input string.
        """

        date_string = date_string[0:13]

        year = int(date_string[:4])
        month = int(date_string[4:6])
        day = int(date_string[6:8])
        hour = int(date_string[9:11])
        minute = int(date_string[11:])
        
        return datetime(year, month, day, hour, minute)


    def _deprecated_download_file(self, url: str, filename: str, target_dir: str):
        """Downloads a file from the specified URL and saves it to the target directory.

        Args:
            url (str): The URL of the file to download.
            filename (str): The filename to use for the downloaded file.
            target_dir (str): The directory where the downloaded file will be saved.

        Raises:
            requests.exceptions.RequestException: If there is an error downloading the file.
        """
        
        with open(os.path.join(target_dir, filename), "wb") as f:
            response = requests.get(url, stream=True)
            total_length = response.headers.get('content-length')

            if total_length is None:
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)


    def _extract_filename(self, original_file_link: str):
        """changes Helioviewer .fits name convention to VSO naming convention. 
        Changin to VSO naming convention will provide ability to synergy with data from Adam's Bachelor Thesis if needed

        Args:
            original_file_link (str): Helioviewer .fits naming convention e.g. 2001_03_21__00_00_01_942__SOHO_MDI_MDI_magnetogram.jp2

        Returns:
            str: VSO naming convention e.g. 20020201_0000_mdimag_1024.png
        """

        resolution = "1024"
        filename: str = original_file_link.split('/')[-1]

        parts = filename.split("_")
        date = parts[0] + parts[1] + parts[2]
        time = parts[4] + parts[5] 

        instrument = parts[10].lower()
        channel = parts[12][:3]

        return f"{date}_{time}_{instrument}{channel}_{resolution}"
    

    def _is_mdi_image_bad(self, img_path):
        """
        Checks if an image is potentially bad based on asymmetry using central moments.

        Args:
            image: image of the solar disc.

        Returns:
            True if the image is likely bad, False otherwise.
        """
        image = cv2.imread(img_path)

        if len(image.shape) == 3:
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray_image = image

        moments = cv2.moments(gray_image)

        mu20 = moments["mu20"]
        mu02 = moments["mu02"]

        asymmetry_threshold = 0.25

        if abs(mu20 - mu02) > asymmetry_threshold * max(mu20, mu02):
            return True
        else:
            return False

