# Welcome to Professor Callahan’s Ice Cream Emporium

[![Build Status](https://app.travis-ci.com/ColdScoop/ice-cream-store.svg?branch=main)](https://app.travis-ci.com/ColdScoop/ice-cream-store)

## Requirements

- CREATE
  - flavor
- READ
  - list of flavors
  - flavor
- UPDATE
  - flavor
- DELETE
  - flavor

## Design

- Flavor Endpoints
  - [X] GET /flavors Gets all flavors
  - [X] GET /flavors/{flavorID} Gets details of one flavor
  - [X] POST /flavors Creates a flavor
  - [X] PUT /flavors Updates a flavor
  - [X] DELETE /flavors Deletes a flavor
- Review Endpoints
  - [X] POST /reviews Creates a review

## Details

### Ideas
- Flavor Offerings
  - Gingerbread House
  - Peppermint
  - Chocolate Chip Cookie Dough
  - Chocolate
  - Vanilla
  - Caramel
  - Mint Chocolate Chip
  - Butter Pecan
  - Strawberry
  - Cookies ‘N Cream (Oreo)
  - Neapolitan
  - Rocky Road

### Objects
- Flavor
  - flavorID
  - flavorName
  - flavorImage
  - flavorDescription
  - flavorNutrition
  - flavorPrice
  - flavorAvailability

- Review
  - reviewID
  - flavorID
  - reviewText

## Setup

### Onboarding
1. python3 -m venv env
2. source env/bin/activate
3. pip install -r requirements-dev.txt

### Building
- To build production, type `make prod`.
- To create the env for a new developer, run `make dev_env`.

## MongoDB

### Local
```
mongosh
```

### Atlas
```
mongosh "mongodb+srv://cluster0.xjsf0.mongodb.net/myFirstDatabase" --username prof
```