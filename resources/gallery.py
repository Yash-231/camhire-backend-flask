from flask import request
import os
from flask_restful import Resource, reqparse
from flask_jwt import  jwt_required
from models.gallery import GalleryModel

class Gallery(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('theme', type=str, required=True, help="this is required field", location='form')
    parser.add_argument('description', type=str, required=True, help="this is required field", location='form')
    parser.add_argument('created_by', type=str, required=True, help="this is required field", location='form')

    def get(self, heading):
        gallery = GalleryModel.find_by_heading(heading)
        if gallery:
            return gallery.json()
        return {"ITEM":"Does not exist"}, 404

    def post(self, heading):
        gallery = GalleryModel.find_by_heading(heading)
        if gallery:
            return {"heading":"Already exists"}
        else:
            data = Gallery.parser.parse_args()
            if request.files:
                if request.files.get('img'):
                    img = request.files['img']
                    if not GalleryModel.allowed_images(img.filename)==False:
                        data['img']=".".join([heading, GalleryModel.allowed_images(img.filename)])
                        img.save("static\\gallery\\img\\"+data['img'])
                    else:
                        return {"Error":"Filename is not allowed"}
                if request.files.get('video'):
                    video = request.files['video']
                    if not GalleryModel.allowed_videos(video.filename)==False:
                        data['video']=".".join([heading, GalleryModel.allowed_videos(video.filename)])
                        video.save("static\\gallery\\video\\"+data['video'])
                    else:
                        return {"Error":"Filename is not allowed"}
            gallery = GalleryModel(heading, **data)
            try:
                gallery.save_to_db()
            except:
                return {"message":"error occured in database"}, 500
            return gallery.json()

    @jwt_required()
    def delete(self, heading):
        gallery = GalleryModel.find_by_heading(heading)
        if gallery:
            if gallery.img != 'default.jpg':
                os.remove("static\\gallery\\img\\"+gallery.img)
            if gallery.video != 'default.mp4':
                os.remove("static\\gallery\\video\\"+gallery.video)
            gallery.delete_from_db()
            return {'message':"Item Deleted"}
        return {"message":"heading does not exist"}, 404

    def put(self, heading):
        gallery = GalleryModel.find_by_heading(heading)
        data = Gallery.parser.parse_args()
        if gallery:
            if request.files:
                if request.files.get('img'):
                    img = request.files['img']
                    if not GalleryModel.allowed_images(img.filename)==False:
                        if gallery.img != 'default.jpg':
                            os.remove("static\\gallery\\img\\"+gallery.img)
                        gallery.img=".".join([heading, GalleryModel.allowed_images(img.filename)])
                        img.save("static\\gallery\\img\\"+gallery.img)
                    else:
                        return {"Error":"Filename is not allowed"}
                if request.files.get('video'):
                    video = request.files['video']
                    if not GalleryModel.allowed_videos(video.filename)==False:
                        if gallery.video != 'default.mp4':
                            os.remove("static\\gallery\\video\\"+gallery.video)
                        gallery.video=".".join([heading, GalleryModel.allowed_videos(video.filename)])
                        video.save("static\\gallery\\video\\"+gallery.video)
                    else:
                        return {"Error":"Filename is not allowed"}
            gallery.theme  = data['theme']
            gallery.description = data['description']
            gallery.created_by = data['created_by']
        else:
            if request.files:
                if request.files.get('img'):
                    img = request.files['img']
                    if not GalleryModel.allowed_images(img.filename)==False:
                        data['img']=".".join([heading, GalleryModel.allowed_images(img.filename)])
                        img.save("static\\gallery\\img\\"+data['img'])
                    else:
                        return {"Error":"Filename is not allowed"}
                if request.files.get('video'):
                    video = request.files['video']
                    if not GalleryModel.allowed_videos(video.filename)==False:
                        data['video']=".".join([heading, GalleryModel.allowed_videos(video.filename)])
                        video.save("static\\gallery\\video\\"+data['video'])
                    else:
                        return {"Error":"Filename is not allowed"}
            gallery = GalleryModel(heading, **data)
        try:
            gallery.save_to_db()
        except:
            return {"message": "error occured in database"}, 500
        return gallery.json()

class GalleryList(Resource):
    def get(self):
        if request.args:
            return {'Galleries':[gallery.json() for gallery in GalleryModel.query.paginate(
                page=int(request.args.get('page')), per_page=int(request.args.get('perpage'))
                ).items]}
        else:
            return {'Galleries':[gallery.json() for gallery in GalleryModel.query.all()]}