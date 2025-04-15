# FAQ

## Why Do Not All Jobs Have All Steps for Speedup Defined?

This is a side effect of small processing times. Because we only look at processing times as an int, it is possible that some speedups overlap with each other. The following shows amplification values used for calculating energy and shortened processing time (`beta=2`, `alpha=10`):

```json
{
    "Amplifiers": {
        "1.0": 10.0, 
        "1.1": 12.1, 
        "1.2": 14.4, 
        "1.3": 16.9, 
        "1.4": 19.6, 
        "1.5": 22.5, 
        "1.6": 25.6, 
        "1.7": 28.9, 
        "1.8": 32.4, 
        "1.9": 36.1, 
        "2.0": 40.0
    }
}
```
What follows is an example task using the above mentioned amplification:

```json
{
    "Id": 47,
    "Stage": 7,
    "ProcessingTime": 64,
    "SpeedUp": {
        "64": 640.0,
        "58": 774.4,
        "53": 921.6,
        "49": 1081.6,
        "46": 1254.4,
        "43": 1440.0,
        "40": 1638.4,
        "38": 1849.6,
        "36": 2073.6,
        "34": 2310.4,
        "32": 2560.0
    }
}
```

Here are additional examples with processing times with clashing values. In this case we highest energy cost is kept. This is a side effect of keeping the speedup as an integer. 

```json
{
    "Id": 48,
    "Stage": 8,
    "ProcessingTime": 4,
    "SpeedUp": {
        "4": 48.4,
        "3": 90.0,
        "2": 160.0
    }
},
{
    "Id": 49,
    "Stage": 9,
    "ProcessingTime": 5,
    "SpeedUp": {
        "5": 60.5,
        "4": 98.0,
        "3": 180.5,
        "2": 200.0
    }
}
```

## How do I use the PV data combined with the scheduling instances?

Each instanc contains a `PvScalingFactor` which tells you how many kwP the instance expects. You can then generate data using for example the [PVGIS service](https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis_en) or use the CSVs provided for example industrial locations. NOTE: The examples are all calculated with 1kWp you need to manually scale it up by multipling the values with the `PvScalingFactor`.
