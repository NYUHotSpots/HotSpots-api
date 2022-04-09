SPOT_FACTORS = ["factorAvailability", "factorNoiseLevel",
                "factorTemperature", "factorAmbiance"]

RESET_FACTORS = {"factorAvailability": 0,
                 "factorNoiseLevel": 0,
                 "factorTemperature": 0,
                 "factorAmbiance": 0,
                 "numFactorEntries": 0,
                 "factorDate": ""}

FULL_SPOT_DOCUMENT = {
    "spotName": "",
    "spotImage": "",
    "spotAddress": "",
    "spotCapacity": "",
    "spotCreation": "",
    "spotUpdate": "",
    "factorAvailability": 0,
    "factorNoiseLevel": 0,
    "factorTemperature": 0,
    "factorAmbiance": 0,
    "numFactorEntries": 0,
    "factorDate": ""
}

LIGHT_SPOT_DOCUMENT = {
    "spotName": "",
    "spotImage": "",
    "spotAddress": "",
    "spotCapacity": "",
    "spotCreation": "",
    "spotUpdate": "",
}

REVIEW_DOCUMENT = {
    "spotID": "",
    "reviewCreation": "",
    "reviewUpdate": "",
    "reviewTitle": "",
    "reviewText": "",
    "reviewRating": "",
    "userID": ""
}
