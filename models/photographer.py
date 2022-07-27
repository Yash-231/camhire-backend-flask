from db import db

class PhotographerModel(db.Model):
    __tablename__ = "photographers"
    id = db.Column(db.Integer, primary_key = True)
    codeword = db.Column(db.String, unique=True)
    name = db.Column(db.String(80))
    speciality = db.Column(db.String)
    description = db.Column(db.String)
    img = db.Column(db.String)

    def __init__(self, codeword, name, speciality, description, img="default.jpg"):
        self.codeword = codeword
        self.name = name
        self.speciality = speciality
        self.description = description
        self.img = img

    def allowed_image(filename):
        if "." not in filename or filename=="":
            return False
        ext=filename.rsplit(".", 1)[1]
        if ext.lower() in ['png', 'jpg', 'jpeg', 'gif']:
            return ext.lower()
        else:
            return False
        
    def json(self):
        return {"id":self.id, "name":self.name, "codeword":self.codeword, "speciality":self.speciality, "description":self.description, "img":self.img}

    @classmethod
    def find_by_codeword(cls, codeword):
        return cls.query.filter_by(codeword=codeword).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()