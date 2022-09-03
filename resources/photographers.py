from flask import request
from flask_restful import Resource, reqparse
from flask_jwt import  jwt_required
from models.photographer import PhotographerModel
from storage import s3, S3_BUCKET_NAME
from werkzeug.utils import secure_filename

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
            img = request.files.get('prof_img')
            quotation = request.files.get('quotation')
            uploaded_images = request.files.getlist('images')
            uploaded_videos = request.files.getlist('videos')
            if img:
                if PhotographerModel.allowed_images(img.filename)==False:
                    return {"Error":"Filename is not allowed"}
            if quotation:
                if PhotographerModel.allowed_docs(quotation.filename)==False:
                    return {"Error":"Filename is not allowed"}
            if uploaded_images:
                for file in uploaded_images:
                    if PhotographerModel.allowed_images(file.filename)==False:
                        return {"Error":"Filename is not allowed"}
            if uploaded_videos:   
                for file in uploaded_videos:
                    if PhotographerModel.allowed_videos(file.filename)==False:
                        return {"Error":"Filename is not allowed"}
            if img:
                data['prof_img'] = f'photographers/{codeword}/prof_img/{secure_filename(img.filename)}'
                s3.put_object(Body=img, Bucket=S3_BUCKET_NAME, Key=data['prof_img'])
            if quotation:
                data['quotation'] = f'photographers/{codeword}/quotation/{secure_filename(quotation.filename)}'
                s3.put_object(Body=quotation, Bucket=S3_BUCKET_NAME, Key=data['quotation'])
            if uploaded_images:
                data["images"] = ""
                for file in uploaded_images:
                    data["images"] += ", " + f'photographers/{codeword}/images/{secure_filename(file.filename)}'
                    s3.put_object(Body=file, Bucket=S3_BUCKET_NAME, Key=f'photographers/{codeword}/images/{secure_filename(file.filename)}')
                data["images"] = data["images"][2:]
            if uploaded_videos:
                data["videos"] = ""
                for file in uploaded_videos:
                    data["videos"] += ", " + f'photographers/{codeword}/videos/{secure_filename(file.filename)}'
                    s3.put_object(Body=file, Bucket=S3_BUCKET_NAME, Key=f'photographers/{codeword}/videos/{secure_filename(file.filename)}')
                data["videos"] = data["videos"][2:]
            photographer = PhotographerModel(codeword, **data)
            try:
                photographer.save_to_db()
            except:
                if data['prof_img'] != "photographers/default_prof_img.jpg":
                    s3.delete_object(Bucket=S3_BUCKET_NAME, Key=data['prof_img'])
                if data["quotation"]:
                    s3.delete_object(Bucket=S3_BUCKET_NAME, Key=data['quotation'])
                if data["images"]:
                    PhotographerModel.delete_keys(data["images"])
                if data["videos"]:
                    PhotographerModel.delete_keys(data["videos"])
                return {"message":"error occured in database"}, 500
            return photographer.json()

    #@jwt_required()
    def delete(self, codeword):
        photographer = PhotographerModel.find_by_codeword(codeword)
        if photographer:
            PhotographerModel.delete_directory(f"photographers/{codeword}/")
            photographer.delete_from_db()
            return {'message':"Item Deleted"}
        return {"ITEM":"Does not exist"}, 404

    def put(self, codeword):
        photographer = PhotographerModel.find_by_codeword(codeword)
        data = Photographers.parser.parse_args()
        if photographer:
            photographer.name  = data['name']
            photographer.speciality = data['speciality']
            photographer.description = data['description']
            img = request.files.get('prof_img')
            quotation = request.files.get('quotation')
            if img:
                if PhotographerModel.allowed_images(img.filename)==False:
                    return {"Error":"Filename is not allowed"}
                else:
                    temp_prof_img = photographer.prof_img
                    photographer.prof_img = f'photographers/{codeword}/prof_img/{secure_filename(img.filename)}'
            if quotation:
                if PhotographerModel.allowed_docs(quotation.filename)==False:
                    return {"Error":"Filename is not allowed"}
                else:
                    temp_quotation = photographer.quotation
                    photographer.quotation = f'photographers/{codeword}/quotation/{secure_filename(quotation.filename)}'
            try:
                photographer.save_to_db()
            except:
                return {"message": "error occured in database"}, 500
            if img:
                if temp_prof_img != "photographers/default_prof_img.jpg":
                    s3.delete_object(Bucket=S3_BUCKET_NAME, Key=temp_prof_img)
                s3.put_object(Body=img, Bucket=S3_BUCKET_NAME, Key=photographer.prof_img)
            if quotation:
                if temp_quotation != "":
                    s3.delete_object(Bucket=S3_BUCKET_NAME, Key=temp_quotation)
                s3.put_object(Body=quotation, Bucket=S3_BUCKET_NAME, Key=photographer.quotation)
            return photographer.json()
        else:
            return Photographers.post(self, codeword)


class PhotographerList(Resource):
    def get(self):
        if request.args:
            return {'photographers':[photographer.json() for photographer in PhotographerModel.query.paginate(
                page=int(request.args.get('page')), per_page=int(request.args.get('perpage'))
                ).items]}
        else:
            return {'photographers':[photographer.json() for photographer in PhotographerModel.query.all()]}


class PhotographerImages(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('keys', type=str, required=True, help="this is required field")

    def post(self, codeword):
        photographer = PhotographerModel.find_by_codeword(codeword)
        if photographer:
            uploaded_images = request.files.getlist('images')
            key_str = ""
            if uploaded_images:
                for file in uploaded_images:
                    if PhotographerModel.allowed_images(file.filename)==False:
                        return {"Error":"Filename is not allowed"}
                for file in uploaded_images:
                    if secure_filename(file.filename) not in photographer.images:
                        key_str += f'photographers/{codeword}/images/{secure_filename(file.filename)}' + ", "
                    s3.put_object(Body=file, Bucket=S3_BUCKET_NAME, Key=f'photographers/{codeword}/images/{secure_filename(file.filename)}')
                if key_str:
                    key_str = key_str[:-2]
                    if photographer.images:
                        photographer.images += ", " + key_str
                    else:
                        photographer.images = key_str
            else:
                return {"message":"no images uploaded"}
            try:
                photographer.save_to_db()
                return {"message":"Images uploaded successfully"}
            except:
                PhotographerModel.delete_keys(key_str)
                return {"message": "error occured in database"}, 500
        else:
            return {"message":"Item doesn't exist"}

    def delete(self, codeword):
        photographer = PhotographerModel.find_by_codeword(codeword)
        if photographer and photographer.images:
            data = PhotographerImages.parser.parse_args()
            if data["keys"] == "*":
                photographer.images = ""
                try:
                    photographer.save_to_db()
                except:
                    return {"message": "error occured in database"}, 500
                PhotographerModel.delete_directory(f"photographers/{codeword}/images/")
            else:
                inp_list = data["keys"].split(", ")
                my_list = photographer.images.split(", ")
                for key in inp_list:
                    if key not in my_list:
                        return {"message":"key doesn't exist"}
                for key in inp_list:
                    my_list.remove(key)
                photographer.images = ", ".join(my_list)
                try:
                    photographer.save_to_db()
                except:
                    return {"message": "error occured in database"}, 500
                PhotographerModel.delete_keys(data["keys"])
            return {"message":"Deletion Successful!"}
        else:
            return {"message":"No items to delete or incorrect username"}


class PhotographerVideos(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('keys', type=str, required=True, help="this is required field")

    def post(self, codeword):
        photographer = PhotographerModel.find_by_codeword(codeword)
        if photographer:
            uploaded_videos = request.files.getlist('videos')
            key_str = ""
            if uploaded_videos:
                for file in uploaded_videos:
                    if PhotographerModel.allowed_videos(file.filename)==False:
                        return {"Error":"Filename is not allowed"}
                for file in uploaded_videos:
                    if secure_filename(file.filename) not in photographer.videos:
                        key_str += f'photographers/{codeword}/videos/{secure_filename(file.filename)}' + ", "
                    s3.put_object(Body=file, Bucket=S3_BUCKET_NAME, Key=f'photographers/{codeword}/videos/{secure_filename(file.filename)}')
                if key_str:
                    key_str = key_str[:-2]
                    if photographer.videos:
                        photographer.videos += ", " + key_str
                    else:
                        photographer.videos = key_str
            else:
                return {"message":"no videos uploaded"}
            try:
                photographer.save_to_db()
                return {"message":"Videos uploaded successfully"}
            except:
                PhotographerModel.delete_keys(key_str)
                return {"message": "error occured in database"}, 500
        else:
            return {"message":"Item doesn't exist"}

    def delete(self, codeword):
        photographer = PhotographerModel.find_by_codeword(codeword)
        if photographer and photographer.videos:
            data = PhotographerVideos.parser.parse_args()
            if data["keys"] == "*":
                photographer.videos = ""
                try:
                    photographer.save_to_db()
                except:
                    return {"message": "error occured in database"}, 500
                PhotographerModel.delete_directory(f"photographers/{codeword}/videos/")
            else:
                inp_list = data["keys"].split(", ")
                my_list = photographer.videos.split(", ")
                for key in inp_list:
                    if key not in my_list:
                        return {"message":"key doesn't exist"}
                for key in inp_list:
                    my_list.remove(key)
                photographer.videos = ", ".join(my_list)
                try:
                    photographer.save_to_db()
                except:
                    return {"message": "error occured in database"}, 500
                PhotographerModel.delete_keys(data["keys"])
            return {"message":"Deletion Successful!"}
        else:
            return {"message":"No item to delete or incorrect username"}