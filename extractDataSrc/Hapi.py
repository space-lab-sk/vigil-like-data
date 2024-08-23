from hapiclient import hapi
import numpy as np

def get_hapi_data(server: str, dataset: str, parameters: str, start: str, stop: str) ->np.ndarray:
    """
    Retrieves data from a HAPI server and converts it into a NumPy array.

    Args:
        server (str): The URL of the HAPI server.
        dataset (str): The name of the dataset to access.
        parameters (str): A comma-separated list of parameters for the data request.
        start (str): The start datetime (initial format might vary, will be converted).
        stop (str): The end datetime (initial format might vary,  will be converted).

    Returns:
        np.ndarray: A NumPy array containing the retrieved HAPI data.

    Raises:
        Exception: If there's a general error during the HAPI request.
        Exception: If there's a 503 error, indicating a problem with HAPI's resource server. Includes a specific message in this case.
    """

    opts = {'logging': False} # set True for some more info about transfer
    start, stop = convert_datetime_format(start, stop)

    
    try:
        data, meta = hapi(server, dataset, parameters, start, stop, **opts)
    except Exception as e:
        
        if "503" in str(e):
            print("There is problem in HAPI's resource server (not responding), not in HAPI itself.")

        raise(e)

    return data


def convert_datetime_format(start: str, stop: str) -> tuple[str, str]:
    """
    Converts a datetime string in the format "YYYY-MM-DD HH:MM:SS" to the format "YYYY-MM-DDTHH:MM:SS", 
    suitable for HAPI

    Args:
        start (str): Starting datetime string to convert.
        stop (str): Stop datetime string to convert.

    Returns:
        The converted datetime string.
    """
    return start.replace(" ", "T"), stop.replace(" ", "T")
