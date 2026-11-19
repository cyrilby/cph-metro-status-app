[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://cph-metro.streamlit.app/)
[![MindGraph](https://img.shields.io/badge/Product%20of%20-MindGraph.dk-1ea2b5?logo=https://mindgraph.dk/favicon.png")](https://mindgraph.dk)

# Copenhagen metro operations monitoring app

* Author: Kiril (GitHub@cyrilby)
* Website: [mindgraph.dk](https://mindgraph.dk)
* Last meaningful update: 19-11-2026

This project is centered around automatically gathering data from the [Copenhagen Metro's website](https://m.dk) and monitoring its operations over time in order to find out how often (and when) things are most likely to break. To facilitate the communication of the insights gathered, the data is presented visually using a [Streamlit app](https://cph-metro.streamlit.app/).

## Note: WIP as of 18-11-2026

Transitioning the app to use `duckdb` for faster data load and filtering as well as performing general optimization. This will take some time to complete.

The `README` file will be updated later.

### Notes on the updated set-up

**Overall structure**: In this new set-up, the `app.py` script has a single job: load the interface and the customisation and set up the navigation between pages. Lots of functions have been moved to scripts in the `core` folder, while the individual pages are set up as individual scripts in the `pages` folder.

**Database**: it is currently downloaded locally from S3 storage but not sure whether the alternative of connecting directly to it (described [here](https://duckdb.org/docs/current/guides/network_cloud_storage/duckdb_over_https_or_s3)) could be a better/more efficient option? In any case, the current implementation seems good enough.

## Requirements

- Python 3.12.10
- Python packages as specified in the `requirements.txt` file


## WIP notes and troubleshooting

### Finished pages

As of 18-11-2026, the following pages are ready for use:

- Welcome
- Overview
- Daily reliability
- Disruption reasons
- Disruption impact
- Disruption history
- Disruption calculator*

\* *Note*: as per the notes in the `disruption_calculator.py` script, I've just copy-pasted the old page in here but I want to make the page a bit more interactive and add charts for when the station is most likely to be disrupted. This may require that I pre-compute the disruption by station, day and hour for all rows and then do the filtering in the page. But for now, at least all pages of the old app are working as before 😉

### Unfinished pages

The following pages have not yet been added:

- Info on data sources*
- Legal disclaimer*

\* *Note*: these last two pages require no coding.

### Other things to double-check

- Make sure that data is cached on all pages to ensure the app runs faster (I may have forgotten to cache the data on some pages)
  - E.g. `daily_reliability.py` seems to load the data a lot slower than `disruption_reasons.py`, which loads data instantly
- AI suggests that I **wrap the data processing** (but not the chart making) in the individual page scripts into Python functions and add the `@st.cache_data` on top of these functions