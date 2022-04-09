from flask_restx import reqparse

spotParser = reqparse.RequestParser()
spotParser.add_argument('spotName', type=str, location='form')
spotParser.add_argument('spotImage', type=str, location='form')
spotParser.add_argument('spotAddress', type=str, location='form')
spotParser.add_argument('spotCapacity', type=str, location='form')

reviewParser = reqparse.RequestParser()
reviewParser.add_argument('spotID', type=str, location='form')
reviewParser.add_argument('reviewTitle', type=str, location='form')
reviewParser.add_argument('reviewText', type=str, location='form')
reviewParser.add_argument('reviewRating', type=int, location='form')

# each will be a number from 1 to 10
factorParser = reqparse.RequestParser()
factorParser.add_argument('factorAvailability', type=int, location='form')
factorParser.add_argument('factorNoiseLevel', type=int, location='form')
factorParser.add_argument('factorTemperature', type=int, location='form')
factorParser.add_argument('factorAmbiance', type=int, location='form')
