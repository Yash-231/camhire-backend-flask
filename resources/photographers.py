import os
from flask import request
from flask_restful import Resource, reqparse
from flask_jwt import  jwt_required
from models.photographer import PhotographerModel

class Photographers(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help="this is required field", location='form')
    parser.add_argument('speciality', type=str, required=True, help="this is required field", location='form')
    parser.add_argument('description', type=str, required=True, help="this is required field", location='form')

    def get(self, codeword):
        photographer = PhotographerModel.find_by_codeword(codeword)
        if photographer:
            return photographer.json()
        return {"ITEM":"Does not exist"}, 404

    def post(self, codeword):
        photographer = PhotographerModel.find_by_codeword(codeword)
        if photographer:
            return {"codeword":"Already exists"}
        else:
            data = Photographers.parser.parse_args()
            if request.files:
                img = request.files['img']
                if img and (not PhotographerModel.allowed_image(img.filename)==False):
                    data['img']=".".join([codeword, PhotographerModel.allowed_image(img.filename)])
                    img.save("static\\uploads\\img\\"+data['img'])
                else:
                    return {"Error":"Filename is not allowed"}
            photographer = PhotographerModel(codeword, **data)
            try:
                photographer.save_to_db()
            except:
                return {"message":"error occured in database"}, 500
            return photographer.json()

    @jwt_required()
    def delete(self, codeword):
        photographer = PhotographerModel.find_by_codeword(codeword)
        if photographer:
            if photographer.img != 'default.jpg':
                os.remove("static\\uploads\\img\\"+photographer.img)
            photographer.delete_from_db()
        return {'message':"Item Deleted"}

    def put(self, codeword):
        photographer = PhotographerModel.find_by_codeword(codeword)
        data = Photographers.parser.parse_args()
        if photographer:
            if request.files:
                img = request.files['img']
                if img and (not PhotographerModel.allowed_image(img.filename)==False):
                    if photographer.img != 'default.jpg':
                        os.remove("static\\uploads\\img\\"+photographer.img)
                    photographer.img=".".join([codeword, PhotographerModel.allowed_image(img.filename)])
                    img.save("static\\uploads\\img\\"+photographer.img)
                else:
                    return {"Error":"Filename is not allowed"}
            photographer.name  = data['name']
            photographer.speciality = data['speciality']
            photographer.description = data['description']
        else:
            if request.files:
                img = request.files['img']
                if img and (not PhotographerModel.allowed_image(img.filename)==False):
                    data['img']=".".join([codeword, PhotographerModel.allowed_image(img.filename)])
                    img.save("static\\uploads\\img\\"+data['img'])
                else:
                    return {"Error":"Filename is not allowed"}
            photographer = PhotographerModel(codeword, **data)
        try:
            photographer.save_to_db()
        except:
            return {"message": "error occured in database"}, 500
        return photographer.json()

class PhotographerList(Resource):
    def get(self):
        if request.args:
            return {'photographers':[photographer.json() for photographer in PhotographerModel.query.paginate(
                page=int(request.args.get('page')), per_page=int(request.args.get('perpage'))
                ).items]}
        else:
            return {'photographers':[photographer.json() for photographer in PhotographerModel.query.all()]}