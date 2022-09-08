import os
from flask import Flask, send_from_directory, abort
from flask_restful import Api
from flask_jwt import JWT
from resources.gallery import Gallery, GalleryList
from resources.items import Item, ItemList
from resources.photographers import Photographers, PhotographerList, PhotographerVideos, PhotographerImages
from resources.user import UserRegister
from security import authenticate, identity
from resources.store import Store, StoreList
from flask_cors import CORS
from db import db

application = Flask(__name__)
cors = CORS(application, resources={r"*": {"origins": "*"}})
api = Api(application)

#DOWNLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + 'pdf/'
#DIR_PATH = os.path.dirname(os.path.realpath(__file__))
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#application.config['data_of_photographers'] = DOWNLOAD_FOLDER
application.secret_key = os.getenv('FLASK_SECRET_KEY')

jwt = JWT(application, authenticate, identity)

items = []

@application.before_first_request
def create_table():
    db.create_all()

db.init_app(application)
api.add_resource(Item,'/item/<string:name>')
api.add_resource(ItemList,'/items')
api.add_resource(StoreList,'/stores')
api.add_resource(Store,'/store/<string:name>')
api.add_resource(Photographers,'/photographer/<codeword>')
api.add_resource(PhotographerList,'/photographers')
api.add_resource(PhotographerImages,'/photographer/<codeword>/images')
api.add_resource(PhotographerVideos,'/photographer/<codeword>/videos')
api.add_resource(UserRegister,'/register')
api.add_resource(Gallery, '/gallery/<theme>')
api.add_resource(GalleryList, '/gallery')

@application.route("/")
def index():
    return "Application running successfully!"

# @application.route("/get-quote/<pdf_name>")
# def get_quote(pdf_name):
#     try:
#         return send_from_directory(application.config['data_of_photographers'], path=pdf_name, as_attachment=True)
#     except:
#         abort(404)

# @application.route("/photographer/get-image/<img_name>")
# def photographer_images(img_name):
#     try:
#         return send_from_directory("static\\uploads\\img", path=img_name, as_attachment=False)
#     except FileNotFoundError:
#         return abort(404)
    
# @application.route("/gallery/get-image/<img_name>")
# def gallery_images(img_name):
#     try:
#         return send_from_directory("static\\gallery\\img", path=img_name, as_attachment=False)
#     except FileNotFoundError:
#         return abort(404)

# @application.route("/gallery/get-video/<video_name>")
# def gallery_videos(video_name):
#     try:
#         return send_from_directory("static\\gallery\\video", path=video_name, as_attachment=False)
#     except FileNotFoundError:
#         return abort(404)

# added comment for testing
if __name__=="__main__":
    application.run(debug=True, host="0.0.0.0", port='8000')