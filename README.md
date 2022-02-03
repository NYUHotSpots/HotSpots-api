# HotSpots API

[![GitHub Actions Build Status](https://github.com/NYUHotSpots/HotSpots-api/actions/workflows/main.yml/badge.svg)](https://github.com/NYUHotSpots/HotSpots-api/actions)

[Heroku App](https://hotspotsapi.herokuapp.com/)

[MongoDB](https://cloud.mongodb.com/v2/61f12b273f1f376f02f6ac37#clusters)

## About

Help students find available study spots around the university based on factors such as availability and noise level by crowsourcing real-time data from student

## Design

Cluster: Cluster0
Database: hotspots_dev

Collections: Spots
{
  spotID,
  spotName,
  spotAddress,
  spotCapacity,
  spotImage,
  factorAvailabiliity: {
    factorDate,
    factorValue,
    factorNumOfInputs
  },
  factorNoiseLevel: {
    factorDate,
    factorValue,
    factorCount
  },
  factorTemperature: {
    factorDate,
    factorValue,
    factorCount
  },
  factorAmbiance: {
    factorDate,
    factorValue,
    factorCount
  },
  reviews: [
    ObjectID("reviewID")
  ]
}


Collections: Reviews
{
  reviewID,
  spotID,
  reviewDate,
  reviewTitle,
  reviewText, 
  reviewRating
}

### Requirements

- CREATE
  - spot
  - review
- READ
  - all spot + availability
  - one spot + all factors
- UPDATE
  - spot availability
  - spot noise level
  - spot temperature
  - spot ambiance
- DELETE
  - spot
  - review

### Endpoints

- CREATE
  - [X] POST /spot
  - [X] POST /review
- READ
  - [X] GET /spot (return all spot documents including: spotID, spotName, spotAddress, spotImage, factorAvailability)
  - [X] GET /spot/{spotID} (returns one spot document including: spotID, spotName, spotAddress, spotCapacity, spotImage, factorAvailabiliity, factorNoiseLevel, factorTemperature, factorAmbiance)
- UPDATE
  - [X] PUT /spot/{spotID}
  - [ ] PUT /spot/availability/{spotID}
  - [ ] PUT /spot/noiselevel/{spotID}
  - [ ] PUT /spot/temperature/{spotID}
  - [ ] PUT /spot/ambiance/{spotID}
- DELETE
  - [X] DELETE /spot/{spotID}
  - [X] DELETE /review/{reviewID}

## Setup

### Onboarding
1. python3 -m venv env
2. source env/bin/activate
3. pip install -r requirements-dev.txt
4. add to a new .env file
  ```
  HOTSPOTS_PATH=***
  LOCAL_DB=1
  TEST_MODE=0
  MONGO_URL=cluster0.empfo.mongodb.net
  MONGO_USER=hot
  MONGO_PASSWORD=***
  MONGO_DEV=hotspots_dev
  MONGO_PROD=hotspots_prod
  ```
    - LOCAL_DB (0 = IS LOCAL, 1 = NOT LOCAL)
    - TEST_MODE (0 = IS TESTING, 1 = NOT TESTING)

### Building
- To build production, type `make prod`.
- To create the env for a new developer, run `make dev_env`.

## MongoDB

### Local
```
mongosh
use hotspots
db.spots.find()
```

### Atlas
```
mongosh "mongodb+srv://cluster0.empfo.mongodb.net/hotspots" --username hot
```