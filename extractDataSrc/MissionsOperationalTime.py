from datetime import datetime

missions_operational_times = {
    "soho_celias": "1996-01-20 17:30:28",
    "wind_mfi": "1994-11-13 00:00:30",
    "soho_eit": "1996-01-01 00:00:00",
    "soho_mag": "1996-04-21 00:30:05",
    "soho_con": "1996-05-19 19:08:35",
    "soho_lasco_c2": "1997-02-21 00:55:39",
    "soho_lasco_c3": "1997-02-20 23:54:37"

}

def check_operational_time(mission_instrument: str, start_datetime: str):
    """
    Checks if the provided start datetime is before the operational start datetime of a given mission instrument.

    Args:
        mission_instrument (str): The name or identifier of the mission instrument (e.g. soho_celias, soho_eit195, soho_mag, etc.).
        start_datetime (str):  The datetime to check, formatted as "YYYY-MM-DD HH:MM:SS".

    Raises:
        Exception: If the input start datetime is before the operational start datetime of the specified mission instrument. The exception message includes the operational datetime for reference.
    """

    start_datetime_obj = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S")

    operational_datetime_obj = datetime.strptime(missions_operational_times[mission_instrument], "%Y-%m-%d %H:%M:%S")

    if start_datetime_obj < operational_datetime_obj:
        print("start_datetime_obj was before operational_datetime_obj")
        raise Exception(f"Inputed start datetime was before operational start of {mission_instrument}, which was on {missions_operational_times[mission_instrument]}")
    


