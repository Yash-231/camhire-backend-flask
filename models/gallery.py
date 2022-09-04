from db import db

class GalleryModel(db.Model):
    __tablename__ = "gallery"
    theme = db.Column(db.String, primary_key = True)
    img = db.Column(db.String)
    video = db.Column(db.String)
    heading = db.Column(db.String)
    description = db.Column(db.String)
    created_by = db.Column(db.String)
    
    def __init__(self, theme, img, video, heading, description, created_by):
        self.theme = theme
        self.img = img
        self.video = video
        self.heading = heading
        self.description = description
        self.created_by = created_by

    def allowed_images(filename):
        if "." not in filename or filename=="":
            return False
        ext=filename.rsplit(".", 1)[1]
        if ext.lower() in ['png', 'jpg', 'jpeg', 'gif']:
            return ext.lower()
        else:
            return False

    def allowed_videos(filename):
        if "." not in filename or filename=="":
            return False
        ext=filename.rsplit(".", 1)[1]
        if ext.lower() in ['avi', 'mov', 'mp4', 'flv', 'aaf', 'mkv', 'wmv', 'mpeg']:
            return ext.lower()
        else:
            return False
        
    def json(self):
        return {"theme":self.theme, "img":self.img}
        
    def json_data(self):
        return {"theme":self.theme, "video":self.video, "heading":self.heading, "description":self.description, "created_by":self.created_by}

    @classmethod
    def find_by_theme(cls, theme):
        return cls.query.filter_by(theme=theme).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()