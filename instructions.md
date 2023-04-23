# Ground Station Software

Download at: https://github.com/vtneil/vnet-ugcs/releases/tag/alpha

## Instructions

1. Install Python 3.11 or upper to your machine
2. Download the source code and move the folder to somewhere, e.g., Desktop
3. Open terminal or your Python IDE and go to that folder
4. Install required packages by `pip install -r requirements.txt` (See pip for more details)
5. Run the program's main file: `app_gui.py`
6. Open the GUI in the web browser by visiting address http://127.0.0.1:8050/

## Configurations

In `data_format.json` file, you can configurate on what fields of data you will be using in the telemetry.

In `settings.json` file,

1. `header` field, can be anything (unused)
2. `delimiter` field, data delimiter
3. `file_name` field, file name to save to
4. `file_extension` field, file extension (can be csv)
5. `lat_key` field, latitude field key in telemetry from data format
6. `lon_key` field, longitude field key in telemetry from data format
7. `alt_key` field, altitude field key in telemetry from data format
8. `plot` field, which keys to plot and which plot types to plot

### Plot types

In each plot element from:
```json
    "plot": {
        "0": [
            {
                ... // PLOT 1
            },
            {
                ... // PLOT 2
            }
            // CAN ADD ADDITIONAL CHARTS
        ]
    }
```

can be the following:
```json
// 1. X-Y (multi-Y) plot
{
    "plot_type": "xyz",
    "style": "line",  // or "scatter"
    "x": "counter",   // X axis key
    "y": [
        "altitude"    // Y axis keys in a list, can be more than 1.
    ]
}
```

or

```json
// 2. X-Y-Z plot
{
    "plot_type": "xyz",
    "style": "line",  // or "scatter"
    "x": "latitude",  // X axis key
    "y": "longitude", // Y axis key
    "z": "altitude"   // Z axis key
}
```

## Example Configuration

### 1. `data_format.json`
```json
{
    "0": [
        "device_id",
        "counter",
        "time_now",
        "free_memory",
        "latitude",
        "longitude",
        "altitude",
        "latitude_sec",
        "longitude_sec",
        "altitude_sec",
        "altitude_pht",
        "temperature_pht",
        "humidity_pht",
        "pressure_pht",
        "altitude_pht_ext",
        "temperature_pht_ext",
        "humidity_pht_ext",
        "pressure_pht_ext",
        "temperature_probe",
        "battery_volt"
    ]
}
```
### 2. `settings.json`
```json
{
    "header": "BALLOON",
    "delimiter": ",",
    "file_name": "team_xx",
    "file_extension": "csv",
    "lat_key": "latitude",
    "lon_key": "longitude",
    "alt_key": "altitude",
    "data_points": 120,
    "plot": {
        "0": [
            {
                "plot_type": "xyz",
                "style": "line",
                "x": "counter",
                "y": [
                    "altitude"
                ]
            },
            {
                "plot_type": "xyz",
                "style": "line",
                "x": "counter",
                "y": [
                    "humidity",
                    "temperature"
                ]
            },
            {
                "plot_type": "xyz",
                "style": "scatter",
                "x": "latitude",
                "y": "longitude",
                "z": "altitude"
            }
        ]
    },
    "state_key": "state",
    "state_name": {
        "1": "PRELAUNCH",
        "2": "ASCENT",
        "3": "HAVEN",
        "4": "BREEZE",
        "5": "BIND"
    }
}
```