from datetime import datetime
import math
import requests
import os
import gzip
import unlzw3
import shutil
from pathlib import Path

class IGSDataDownloader(requests.Session):
    """
    Class to download IGS data from the NASA CDDIS server.
    Look at https://igs.org/products/ for more information.
    """
    
    AUTH_HOST = 'urs.earthdata.nasa.gov'
    """The host for NASA Earthdata authentication."""
    
    PROVIDER_URL = "https://cddis.nasa.gov/archive/gnss/"
    """The base URL for the NASA CDDIS server."""
    
    _provider_url: str
    """The URL of the data provider."""
    
    _session: str
    """The password for the NASA data provider."""
    
    _date_obj: dict
    """The date object for the data to be downloaded."""
    
    _files_obj: dict
    """The files object for the data to be downloaded."""
    
    def __init__(self, nasaUsr: str = None, nasaPwd: str = None):
        """Initialize the IGSDataDownloader class."""
        super().__init__()
        self.auth = (nasaUsr, nasaPwd)
        self._date_obj = {}
        self._files_obj = {}
        
    def rebuild_auth(self, prepared_request, response):
        """Override the rebuild_auth method to keep headers when redirected to or from the NASA auth host."""
        headers = prepared_request.headers
        url = prepared_request.url
        if 'Authorization' in headers:
            original_parsed = requests.utils.urlparse(response.request.url)
            redirect_parsed = requests.utils.urlparse(url)
            if (original_parsed.hostname != redirect_parsed.hostname) and redirect_parsed.hostname != self.AUTH_HOST and original_parsed.hostname != self.AUTH_HOST:
                del headers['Authorization']
        return
    
    def setDate(self, year: int, month: int, day: int):
        """Create the date object for the data to be downloaded."""
        # check if the date is valid (not in the future)
        current_date = datetime.now()
        if datetime(year, month, day) > current_date:
            raise ValueError("The date cannot be in the future.")
        
        try:
            # assemble the date string (YYYY-MM-DD)
            date = f"{year}-{month:02d}-{day:02d}"
            # convert the string into a datetime object
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            # day of the year (1-366, DDD)
            day_of_year = date_obj.timetuple().tm_yday
            # day of the week (0-6; Monday-Sunday in the ISO format; 7=weekly, D)
            # Per ottenere 0=domenica, 6=sabato (formato americano), usa date_obj.weekday() + 1) % 7
            day_of_week_iso = date_obj.weekday()  # 0-6 (lunedì-domenica)
            day_of_week_us = (date_obj.weekday() + 1) % 7  # 0-6 (domenica-sabato)
            # GPS week number (WWWW)
            gps_epoch = datetime(1980, 1, 6) # the reference date for GPS is 06/01/1980
            days_since_epoch = (date_obj - gps_epoch).days
            gps_week = math.floor(days_since_epoch / 7)
            
            self._date_obj = {
                'date_str': date,
                'date_obj': date_obj,
                'YYYY': year, 
                'YY': str(year)[2:], 
                'DDD': day_of_year, 
                'D': day_of_week_iso, 
                'D_us': day_of_week_us, 
                'WWWW': gps_week
            }
            
            return self._date_obj
        except Exception as e:
            raise Exception(f"Cannot parse this date: {date}. Error: {e}")
        
    def getDate(self) -> datetime:
        """Get the date object for the data to be downloaded."""
        return self._date_obj['date_obj']
        
    def getFiles(self) -> dict:
        """Get the files object for the data to be downloaded."""
        return self._files_obj
    
    def downloadBroadcastEphemeris(self, save_path: str) -> str:
        """
        Download the daily broadcast ephemeris file.

        Tries the following products in priority order (best → fallback):

        1. RINEX 3 IGS combined multi-GNSS: daily/YYYY/DDD/YYp/
           BRDC00IGS_R_YYYYDDD0000_01D_MN.rnx.gz
        2. RINEX 3 DLR merged multi-GNSS: daily/YYYY/DDD/YYp/
           BRDM00DLR_S_YYYYDDD0000_01D_MN.rnx.gz
        3. RINEX 2 GPS-only: daily/YYYY/DDD/YYn/brdcDDD0.YYn.gz
        4. RINEX 2 GPS-only (alternate path): daily/YYYY/brdc/brdcDDD0.YYn.gz

        Note: multi-GNSS combined files (BRDC/BRDM) live in the YYp/ directory,
        alongside individual-station MN files. The YYb/ directory does not exist
        on CDDIS for most dates.

        References:
          https://igs.org/data/#daily_data
          https://cddis.nasa.gov/Data_and_Derived_Products/GNSS/broadcast_ephemeris_data.html
        """
        found = False
        startURL = f"{self.PROVIDER_URL}data/daily/"
        is_new = datetime.strptime(self._date_obj['date_str'], '%Y-%m-%d') >= datetime(2020, 12, 1)
        ext = "gz" if is_new else "Z"

        YYYY = self._date_obj['YYYY']
        YY   = self._date_obj['YY']
        DDD  = f"{self._date_obj['DDD']:03d}"

        url_candidates = []

        # 1. RINEX 3 IGS combined multi-GNSS (best) — YYp/ directory
        if is_new:
            url_candidates.append(
                f"{startURL}{YYYY}/{DDD}/{YY}p/BRDC00IGS_R_{YYYY}{DDD}0000_01D_MN.rnx.gz"
            )

        # 2. RINEX 3 DLR merged multi-GNSS — YYp/ directory
        if is_new:
            url_candidates.append(
                f"{startURL}{YYYY}/{DDD}/{YY}p/BRDM00DLR_S_{YYYY}{DDD}0000_01D_MN.rnx.gz"
            )

        # 3. RINEX 2 GPS-only (primary path)
        url_candidates.append(
            f"{startURL}{YYYY}/{DDD}/{YY}n/brdc{DDD}0.{YY}n.{ext}"
        )

        # 4. RINEX 2 GPS-only (alternate legacy path)
        url_candidates.append(
            f"{startURL}{YYYY}/brdc/brdc{DDD}0.{YY}n.{ext}"
        )

        for url in url_candidates:
            try:
                file_name = self.download(url, save_path)
                self._files_obj['broadcast_eph'] = self.extract(os.path.join(save_path, file_name))
                found = True
                break
            except Exception:
                continue

        if not found:
            raise Exception("Cannot find broadcast ephemeris file (tried BRDC00IGS, BRDM00DLR, brdc).")
        
    def downloadPreciseFinalOrbit(self, save_path: str):
        """
        Download the precise (Final) Orbit and Clock file (https://igs.org/products/#orbits_clocks).
        Precise Orbits: https://cddis.nasa.gov/Data_and_Derived_Products/GNSS/orbit_products.html
        """
        found = False

        url = []
        if self._date_obj['WWWW'] <= 2237:
            # Precise (Final) Orbit and Clock file (https://igs.org/products/#orbits_clocks)
            # Precise Orbits: https://cddis.nasa.gov/Data_and_Derived_Products/GNSS/orbit_products.html
            # - until week 2237:   https://cddis.nasa.gov/archive/gnss/products/WWWW/igsWWWWD.sp3.Z
            url.append(f"{self.PROVIDER_URL}products/{self._date_obj['WWWW']}/igs{self._date_obj['WWWW']}{self._date_obj['D_us']}.sp3.Z")
        else:
            # - from week 2338 on: 
            #      - https://cddis.nasa.gov/archive/gnss/products/wwww[/reproX]
            #      - https://cddis.nasa.gov/archive/gnss/products/latest
            #           - old name: igswwwwd.sp3.Z
            #           - new name: IGS0OPSFIN_yyyyddd0000_01D_15M_ORB.SP3.gz
            url.append(f"{self.PROVIDER_URL}products/{self._date_obj['WWWW']}/IGS0OPSFIN_{self._date_obj['YYYY']}{self._date_obj['DDD']:03d}0000_01D_15M_ORB.SP3.gz")
            url.append(f"{self.PROVIDER_URL}products/latest/IGS0OPSFIN_{self._date_obj['YYYY']}{self._date_obj['DDD']:03d}0000_01D_15M_ORB.SP3.gz")
            # trying also the old name
            url.append(f"{self.PROVIDER_URL}products/{self._date_obj['WWWW']}/igs{self._date_obj['WWWW']}{self._date_obj['D_us']}.sp3.Z")
            url.append(f"{self.PROVIDER_URL}products/latest/igs{self._date_obj['WWWW']}{self._date_obj['D_us']}.sp3.gz")
            
        for u in url:
            try:
                file_name = self.download(u, save_path)
                self._files_obj['orbits'] = self.extract(os.path.join(save_path, file_name))
                found = True
                break
            except Exception as e:
                continue
        if not found:
            raise Exception(f"cannot find the precise (final) orbit .sp3 file.")
    
    def downloadPreciseFinalClock(self, save_path: str):
        """
        Download the precise (Final) Clock file (https://igs.org/products/#orbits_clocks).
        Precise Clocks: https://cddis.nasa.gov/Data_and_Derived_Products/GNSS/clock_products.html
        """
        found = False
        url = []
        
        if self._date_obj['WWWW'] <= 2237:
            # - until week 2237:   https://cddis.nasa.gov/archive/gnss/products/WWWW/igsWWWWD.clk.Z
            url.append(f"{self.PROVIDER_URL}products/{self._date_obj['WWWW']}/igs{self._date_obj['WWWW']}{self._date_obj['D_us']}.clk.Z")
        else:
            # - from week 2338 on:
            #      - https://cddis.nasa.gov/archive/gnss/products/wwww[/reproX]
            #      - https://cddis.nasa.gov/archive/gnss/products/latest
            #           - old name: igswwwwd.clk.Z
            #           - new name: IGS0OPSFIN_yyyyddd0000_01D_05M_CLK.CLK.gz 
            url.append(f"{self.PROVIDER_URL}products/{self._date_obj['WWWW']}/IGS0OPSFIN_{self._date_obj['YYYY']}{self._date_obj['DDD']:03d}0000_01D_05M_CLK.CLK.gz")
            url.append(f"{self.PROVIDER_URL}products/latest/IGS0OPSFIN_{self._date_obj['YYYY']}{self._date_obj['DDD']:03d}0000_01D_05M_CLK.CLK.gz")
            url.append(f"{self.PROVIDER_URL}products/{self._date_obj['WWWW']}/igs{self._date_obj['WWWW']}{self._date_obj['D_us']}.clk.Z")
            url.append(f"{self.PROVIDER_URL}products/latest/igs{self._date_obj['WWWW']}{self._date_obj['D_us']}.clk.gz")
        for u in url:
            try:
                file_name = self.download(u, save_path)
                self._files_obj['clocks'] = self.extract(os.path.join(save_path, file_name))
                found = True
                break
            except Exception as e:
                continue
        if not found:
            raise Exception(f"cannot find the precise (final) clock .clk file.")
        else:
            return file_name
    
    def downloadIonosphere(self, save_path: str):
        """
        Download the Ionosphere File (https://igs.org/products/#ionosphere and https://cddis.nasa.gov/Data_and_Derived_Products/GNSS/atmospheric_products.html)
        """
        found = False
        url = []
        
        if self._date_obj['WWWW'] <= 2237:
            # - until week 2237: https://cddis.nasa.gov/archive/gnss/products/ionex/YYYY/DDD/igsgddd0.yyi.Z
            url.append(f"{self.PROVIDER_URL}products/ionex/{self._date_obj['YYYY']}/{self._date_obj['DDD']:03d}/igsg{self._date_obj['DDD']:03d}0.{self._date_obj['YY']}i.Z")
        else:
            # - from week 2238 on: https://cddis.nasa.gov/archive/gnss/products/ionex/WWWW/ (su igs dice YYYY/DDD...)
            #                      IGS0OPSFIN_yyyyddd0000_01D_02H_GIM.INX.gz (new name)
            url.append(f"{self.PROVIDER_URL}products/ionex/{self._date_obj['WWWW']}/IGS0OPSFIN_{self._date_obj['YYYY']}{self._date_obj['DDD']:03d}0000_01D_02H_GIM.INX.gz")
            url.append(f"{self.PROVIDER_URL}products/ionex/{self._date_obj['YYYY']}/{self._date_obj['DDD']:03d}/IGS0OPSFIN_{self._date_obj['YYYY']}{self._date_obj['DDD']:03d}0000_01D_02H_GIM.INX.gz")
            # trying also the old name
            url.append(f"{self.PROVIDER_URL}products/ionex/{self._date_obj['WWWW']}/igsg{self._date_obj['DDD']:03d}0.{self._date_obj['YY']}i.Z")
            url.append(f"{self.PROVIDER_URL}products/ionex/{self._date_obj['YYYY']}/{self._date_obj['DDD']:03d}/igsg{self._date_obj['DDD']:03d}0.{self._date_obj['YY']}i.Z")
        
        for u in url:
            try:
                file_name = self.download(u, save_path)
                self._files_obj['ionosphere'] = self.extract(os.path.join(save_path, file_name))
                found = True
                break
            except Exception as e:
                continue
        if not found:
            raise Exception(f"cannot find the ionosphere .ionex file.")
    
    def downloadTroposhpere(self, save_path: str):
        """
        Download the Troposphere File (https://igs.org/products/#troposphere and https://cddis.nasa.gov/Data_and_Derived_Products/GNSS/atmospheric_products.html).
        The troposphere products utilize the IGS final satellite, orbit, and EOP products and are therefore available approximately three weeks following the observation day
        """
        
        # from https://network.igs.org/
        sites = [
            {'4-digit-name': 'medi', '9-character-name': 'MEDI00ITA'},
            {'4-digit-name': 'pado', '9-character-name': 'PADO00ITA'},
            {'4-digit-name': 'bzr2', '9-character-name': 'BZR200ITA'},
            {'4-digit-name': 'ieng', '9-character-name': 'IENG00ITA'},
            {'4-digit-name': 'geno', '9-character-name': 'GENO00ITA'},
            {'4-digit-name': 'm0se', '9-character-name': 'M0SE00ITA'},
            {'4-digit-name': 'mat1', '9-character-name': 'MAT100ITA'},
            {'4-digit-name': 'not1', '9-character-name': 'NOT100ITA'},
        ]
        
        found = False
        url = []
        
        for site in sites:
            SSSS = site['4-digit-name']
            SITENAME = site['9-character-name']
            
            if self._date_obj['WWWW'] <= 2237:
                # - until week 2237: https://cddis.nasa.gov/archive/gnss/products/troposphere/zpd/
                # Append the following directory and file names to the starting directory for current files: TYP/SSSSDDD#.YYzpd.gz
                # as described in the table below.
                # | Code | Meaning
                # | TYP  | type of solution (zpd or sub, analysis center input products to combined zpd product)
                # | SSSS | IGS monument name
                # | DDD  | 3-digit day of year
                # | #    | file number for the day, typically 0
                # | YY   | 2-digit year
                # | .gz  | gzip compressed file
                TYP = "zpd"
                url.append(f"{self.PROVIDER_URL}products/troposphere/{TYP}/{self._date_obj['YYYY']}/{self._date_obj['DDD']:03d}/{SSSS}{self._date_obj['DDD']:03d}0.{self._date_obj['YY']}zpd.gz")
            else:
                # - from week 2238 on: https://cddis.nasa.gov/archive/gnss/products/troposphere/zpd/
                # Append the following directory and file names to the starting directory for current files: YYYY/IGS0OPSFIN_YYYYDOYHHMM_01D_05M_SITENAME_TRO.TRO.gz
                # as described in the table below.
                # | Code     | Meaning
                # | YYYY     | 4-digit year
                # | DOY      | 3-digit day of year
                # | HH       | 2-digit hour
                # | MM       | file number for the day, typically 0
                # | SITENAME | 9 character site name
                # | .gz      | gzip compressed file
                TYP = "zpd"
                HH = "00"
                MM = "00"
                url.append(f"{self.PROVIDER_URL}products/troposphere/{TYP}/{self._date_obj['YYYY']}/{self._date_obj['DDD']:03d}/IGS0OPSFIN_{self._date_obj['YYYY']}{self._date_obj['DDD']:03d}{HH}{MM}_01D_05M_{SITENAME}_TRO.TRO.gz")
    
        for u in url:
            try:
                file_name = self.download(u, save_path)
                self._files_obj['troposphere'] = self.extract(os.path.join(save_path, file_name))
                found = True
                break
            except Exception as e:
                continue
        if not found:
            raise Exception(f"cannot find the troposphere .tro file in {SITENAME}.")
    
    def download(self, url: str, save_path: str):
        """Download a file from the given URL and save it to the specified path."""
        print(url)
        try:
            # submit the request using the session
            response = self.get(url, stream=True)
            # raise an exception in case of http errors
            response.raise_for_status()
            # save the file
            file_name = os.path.basename(url)
            with open(os.path.join(save_path, file_name), 'wb') as fd:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    fd.write(chunk)
            return file_name
        except requests.exceptions.HTTPError as e:
            raise Exception(f"HTTP error occurred: {e}")
    
    def extract(self, save_path: str):
        """Extract the downloaded file if it is compressed."""
        try:
            # get the name of the downloaded file
            file_name = os.path.join(save_path)
            # check if the file is compressed
            if file_name.endswith('.gz'):
                # os.system(f"gunzip {file_name}")
                with gzip.open(file_name, "rb") as infile:
                    with open(file_name[:-3], "wb") as outfile:
                        shutil.copyfileobj(infile, outfile)
                os.remove(file_name)
                return file_name[:-3]
            elif file_name.endswith('.Z'):
                # os.system(f"uncompress {file_name}")
                uncompressed_data = unlzw3.unlzw(Path(file_name).read_bytes())
                with open(file_name[:-2], 'wb') as output:
                    output.write(uncompressed_data)
                os.remove(file_name)
                return file_name[:-2]
        except Exception as e:
            raise Exception(f"Cannot extract the file {file_name}. Error: {e}")