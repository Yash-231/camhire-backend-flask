import sqlite3

from flask_restful import Resource, reqparse
from flask_jwt import  jwt_required
from flask import send_from_directory, abort
from models.photographer import PhotographerModel

class Photographers(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help="this is required field")
    parser.add_argument('img', type=str, required=True, help="this is required field")
    #parser.add_argument('codeword', type=str, required=True, help="this is required field")
    parser.add_argument('description', type=str, required=True, help="this is required field")
    parser.add_argument('quotation', type=str, required=True, help="this is required field")

    def get(self, codeword):
        photographer = PhotographerModel.find_by_codeword(codeword)
        if photographer:
            return photographer.json()
        return {"ITEM":"Does not exist"}, 404

    def post(self, codeword):
        photographer = PhotographerModel.find_by_codeword(codeword)
        if photographer:
            return {codeword:"Already exists"}
        else:
            data = Photographers.parser.parse_args()
            photographer = PhotographerModel(data)
            try:
                photographer.save_to_db()
            except:
                return {"message":"error occured in database"}, 500
            return photographer.json(), 201

    @jwt_required()
    def delete(self, codeword):
        photographer = PhotographerModel.find_by_codeword(codeword)
        if photographer:
            photographer.delete_from_db()
        return {'message':"Item Deleted"}

    def put(self, codeword):
        photographer = PhotographerModel.find_by_codeword(codeword)
        data = Photographers.parser.parse_args()
        if photographer:
            photographer = PhotographerModel(data)
        else:
            photographer.description = data['description']
        photographer.save_to_db()
        return photographer.json()

class PhotographerList(Resource):
    def get(self):
        return {'photographer':[photographer.json() for photographer in PhotographerModel.query.all()]}
    #list(map(lambda x:x.json,ItemModel.query.all())