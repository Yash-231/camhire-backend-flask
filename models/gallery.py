from db import db

class GalleryModel(db.Model):
    __tablename__ = "gallery"
    heading = db.Column(db.String, primary_key = True)
    theme = db.Column(db.String)
    img = db.Column(db.String)
    video = db.Column(db.String)
    description = db.Column(db.String)
    created_by = db.Column(db.String)
    
    def __init__(self, heading, theme, description, created_by, img, video):
        self.heading = heading
        self.theme = theme
        self.img = img
        self.video = video
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
        return {"heading":self.heading, "theme":self.theme, "img":self.img, "video":self.video, "description":self.description, "created_by":self.created_by}
        
    @classmethod
    def find_by_heading(cls, heading):
        return cls.query.filter_by(heading=heading).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()