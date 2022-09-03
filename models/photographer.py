import imp
from db import db
from storage import s3, S3_BUCKET_NAME

class PhotographerModel(db.Model):
    __tablename__ = "photographers"
    id = db.Column(db.Integer, primary_key = True)
    codeword = db.Column(db.String, unique=True)
    name = db.Column(db.String(80))
    speciality = db.Column(db.String)
    description = db.Column(db.String)
    prof_img = db.Column(db.String)
    quotation = db.Column(db.String)
    images = db.Column(db.String)
    videos = db.Column(db.String)
 
    def __init__(
        self, codeword, name, speciality, description, quotation="",
        images="", videos="", prof_img="photographers/default_prof_img.jpg"
        ):
        self.codeword = codeword
        self.name = name
        self.speciality = speciality
        self.description = description
        self.quotation = quotation
        self.images = images
        self.videos = videos
        self.prof_img = prof_img

    def allowed_images(filename):
        if "." not in filename or filename=="" or "," in filename:
            return False
        ext=filename.rsplit(".", 1)[1]
        if ext.lower() in ['png', 'jpg', 'jpeg', 'gif']:
            return ext.lower()
        else:
            return False

    def allowed_videos(filename):
        if "." not in filename or filename=="" or "," in filename:
            return False
        ext=filename.rsplit(".", 1)[1]
        if ext.lower() in ['avi', 'mov', 'mp4', 'flv', 'aaf', 'mkv', 'wmv', 'mpeg']:
            return ext.lower()
        else:
            return False
        
    def allowed_docs(filename):
        if "." not in filename or filename=="":
            return False
        ext=filename.rsplit(".", 1)[1]
        if ext.lower() in ['pdf', 'doc', 'docx', 'odt']:
            return ext.lower()
        else:
            return False

    def delete_directory(key):
        # response = s3.list_objects_v2(Bucket=AWS_BUCKET_NAME, Prefix=f"photographers/{codeword}/")
        # files_in_folder = response["Contents"]
        # files_to_delete = []
        # for file in files_in_folder:
        #     files_to_delete.append({"Key": file["Key"]})
        # response = s3.delete_objects(Bucket=AWS_BUCKET_NAME, Delete={"Objects": files_to_delete})
        paginator = s3.get_paginator("list_objects_v2")
        response = paginator.paginate(Bucket=S3_BUCKET_NAME, Prefix=key, PaginationConfig={"PageSize": 1000})
        for page in response:
            files_to_delete = []
            files = page.get("Contents")
            for file in files:
                files_to_delete.append({"Key": file["Key"]})
            s3.delete_objects(Bucket=S3_BUCKET_NAME, Delete={"Objects": files_to_delete})
        # os.system(f"aws s3 rm s3://{S3_BUCKET_NAME}/ --recursive --exclude \"*\" --include \"photographers/{codeword}/*\"")

    def delete_keys(keys):
        files_to_delete = []
        temp = keys.split(", ")
        for key in temp:
            files_to_delete.append({"Key": key})
        s3.delete_objects(Bucket=S3_BUCKET_NAME, Delete={"Objects": files_to_delete})

    def json(self):
        return {
            "id":self.id, "name":self.name, "codeword":self.codeword, "speciality":self.speciality,
            "description":self.description, "prof_img":self.prof_img, "quotation":self.quotation,
            "images":list(filter(None, self.images.split(", "))),
            "videos":list(filter(None, self.videos.split(", ")))
            }

    @classmethod
    def find_by_codeword(cls, codeword):
        return cls.query.filter_by(codeword=codeword).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()