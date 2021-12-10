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
  - [X] GET /flavors/ GetFlavors
  - [X] GET /flavors/{flavorID} GetFlavorDetail
  - [X] POST /flavors/create CreateFlavor
  - [X] POST /flavors/update UpdateFlavor
  - [ ] POST /flavors/delete DeleteFlavor
- Review Endpoints
  - [ ] POST /review/create CreateReview

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