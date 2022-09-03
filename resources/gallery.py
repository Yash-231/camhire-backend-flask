from flask import request
from flask_restful import Resource, reqparse
from flask_jwt import  jwt_required
from models.gallery import GalleryModel
from storage import s3, S3_BUCKET_NAME

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
            if request.files.get('img') and request.files.get('video'):
                img = request.files.get('img')
                video = request.files.get('video')
                if (not GalleryModel.allowed_images(img.filename)==False) and (not GalleryModel.allowed_videos(video.filename)==False):
                    data['img']=".".join([f"gallery/{heading}", GalleryModel.allowed_images(img.filename)])
                    data['video']=".".join([f"gallery/{heading}", GalleryModel.allowed_videos(video.filename)])
                    s3.put_object(Body=video, Bucket=S3_BUCKET_NAME, Key=data['video'])
                    s3.put_object(Body=img, Bucket=S3_BUCKET_NAME, Key=data['img'])
                else:
                    return {"Error":"Filename is not allowed"}
            else:
                return {"message":"Image and Video are required!"}
            gallery = GalleryModel(heading, **data)
            try:
                gallery.save_to_db()
            except:
                s3.delete_object(Bucket=S3_BUCKET_NAME, Key=data['video'])
                s3.delete_object(Bucket=S3_BUCKET_NAME, Key=data['img'])
                return {"message":"error occured in database"}, 500
            return gallery.json()

    #@jwt_required()
    def delete(self, heading):
        gallery = GalleryModel.find_by_heading(heading)
        if gallery:
            s3.delete_object(Bucket=S3_BUCKET_NAME, Key=gallery.img)
            s3.delete_object(Bucket=S3_BUCKET_NAME, Key=gallery.video)
            gallery.delete_from_db()
            return {'message':"Item Deleted"}
        return {"message":"heading does not exist"}, 404

    def put(self, heading):
        gallery = GalleryModel.find_by_heading(heading)
        data = Gallery.parser.parse_args()
        if gallery:
            gallery.theme  = data['theme']
            gallery.description = data['description']
            gallery.created_by = data['created_by']
            img = request.files.get('img')
            video = request.files.get('video')
            if img:
                if GalleryModel.allowed_images(img.filename)==False:
                    return {"Error":"Filename is not allowed"}
                else:
                    temp_img = gallery.img
                    gallery.img = ".".join([f"gallery/{heading}", GalleryModel.allowed_images(img.filename)])
            if video:
                if GalleryModel.allowed_videos(video.filename)==False:
                    return {"Error":"Filename is not allowed"}
                else:
                    temp_video = gallery.video
                    gallery.video = ".".join([f"gallery/{heading}", GalleryModel.allowed_videos(video.filename)])
            try:
                gallery.save_to_db()
            except:
                return {"message": "error occured in database"}, 500
            if img:
                s3.delete_object(Bucket=S3_BUCKET_NAME, Key=temp_img)
                s3.put_object(Body=img, Bucket=S3_BUCKET_NAME, Key=gallery.img)
            if video:
                s3.delete_object(Bucket=S3_BUCKET_NAME, Key=temp_video)
                s3.put_object(Body=video, Bucket=S3_BUCKET_NAME, Key=gallery.video)
            return gallery.json()
        else:
            return Gallery.post(self, heading)

class GalleryList(Resource):
    def get(self):
        if request.args:
            return {'Galleries':[gallery.json() for gallery in GalleryModel.query.paginate(
                page=int(request.args.get('page')), per_page=int(request.args.get('perpage'))
                ).items]}
        else:
            return {'Galleries':[gallery.json() for gallery in GalleryModel.query.all()]}