import pandas as pd
import requests
import io


def get_imf_employment_data()-> pd.DataFrame:
    '''Returns pandas DataFrame of unclean data. All columns from IMF API'''   
   

    url = "https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/LS/9.0.0/BRA+GBR+CHN+MAC+HKG+FRA+ITA+JPN+RUS+USA+ZAF.U.*.Q"

    params = {
        "c[TIME_PERIOD]": "ge:1995-12-31+le:2026-12-31",
        "attributes": "all",
        "detail": "full",
        "includeHistory": "true",
        "limit": 100,
    }

    headers = {
        "Accept": "application/vnd.sdmx.data+csv;version=2.0.0"  # ask for CSV instead of JSON
    }

    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()

    uneployment_data = pd.read_csv(pd.io.common.StringIO(resp.text))
    return uneployment_data



def get_imf_gdp_data()-> pd.DataFrame:

    '''All columns from IMF API on GDP. Data in unclean so requires sorting.
    
    Returns Pandas DataFrame'''  
   

    BASE_URL = (
        "https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/QNEA/7.0.0/"
        "USA+JPN+ZAF+GBR+CHN+HKG+MAC+CAN+FRA+ITA+RUS+BRA.B1GQ.*.*.*.*"
        "?c%5BTIME_PERIOD%5D=ge:1995-12-31+le:2026-12-30"
        "&attributes=all&detail=full&includeHistory=true&limit=100"
    )


    def fetch_as_csv(url: str) -> pd.DataFrame:
        """Try requesting SDMX-CSV, which pandas can read directly."""
        headers = {"Accept": "application/vnd.sdmx.data+csv;version=1.0.0"}
        resp = requests.get(url, headers=headers, timeout=60)
        resp.raise_for_status()
        return pd.read_csv(io.StringIO(resp.text))


    def fetch_as_json(url: str) -> pd.DataFrame:
        """Fallback: request SDMX-JSON and flatten it manually."""
        headers = {"Accept": "application/vnd.sdmx.data+json;version=2.0.0"}
        resp = requests.get(url, headers=headers, timeout=60)
        resp.raise_for_status()
        payload = resp.json()

        data = payload["data"]
        dataset = data["dataSets"][0]
        structure = data["structures"][0]

        # Dimensions attached at the series level and at the observation level
        series_dims = structure["dimensions"].get("series", [])
        obs_dims = structure["dimensions"].get("observation", [])

        rows = []
        for series_key, series_val in dataset.get("series", {}).items():
            series_indices = series_key.split(":")
            series_labels = {
                series_dims[i]["id"]: series_dims[i]["values"][int(idx)]["id"]
                for i, idx in enumerate(series_indices)
            }

            for obs_key, obs_val in series_val.get("observations", {}).items():
                obs_indices = obs_key.split(":")
                obs_labels = {
                    obs_dims[i]["id"]: obs_dims[i]["values"][int(idx)]["id"]
                    for i, idx in enumerate(obs_indices)
                }
                row = {**series_labels, **obs_labels, "value": obs_val[0]}
                rows.append(row)

        return pd.DataFrame(rows)


    try:
        df = fetch_as_csv(BASE_URL)
    except Exception as e:
        print(f"CSV fetch failed ({e}), falling back to SDMX-JSON...")
        df = fetch_as_json(BASE_URL)

    return df

   

