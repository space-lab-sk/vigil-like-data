# vigil-like-data
---
This is a repository that contains supplemental code for the paper: Extreme Space Weather Events of the Past 30 Years: Analysis and Implications for Data by Mission Vigil

### Data Extraction

We have developed flexible pipeline to download data from numerous instruments:   
- SOHO / EIT - images in 195 filter
- SOHO / MDI - magnetograms and continuum intensity images  
- SOHO / LASCO C2 and C3 - coronagraphs images 
- SOHO / CELIAS - proton speed and density measurements  
- WIND / MFI - magnetic field measurements 
    
       
The notebook [**extract-data.ipynb**](extract-data.ipynb) demonstrates use cases for downloading data. The scripts responsible for downloading the data are located in the [**extractDataSrc**](extractDataSrc) folder. These scripts are organized into separate Python files and classes, each handling data downloads for a specific instrument. 
    
To obtain data, we take advantage of [hapiclient](https://pypi.org/project/hapiclient/) and [hvpy](https://pypi.org/project/hvpy/). Hapiclient is used to obtain in-situ measurements and timestamps for existing image data. Hvpy library is used to collect SOHO/LASCO and SOHO/MDI images. A different approach is required for SOHO/EIT 195 images. We utilize [Virtual Solar Observatory](https://sdac.virtualsolar.org/cgi/search) to search for relevant links to .fits files. Then, script processes the links to obtain .fits files and creates .png images. We observe that this solution provides higher quality for EIT 195 images compared to hvpy solution.   

### Data Vizualization

The notebook [**dashboard.ipynb**](dashboard.ipynb) demonstrates the creation of a dashboard that visualizes extreme space weather events using the above-mentioned extracted data. The full movies of data dashboards from 20 days around 4 great events are available at our [YouTube playlist](https://www.youtube.com/playlist?list=PLNAJsgS6RlzgnhvJzieUyCZP9tV9-bYPr).

