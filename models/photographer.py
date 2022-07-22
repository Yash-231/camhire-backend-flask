from db import db

class PhotographerModel(db.Model):
    __tablename__ = "photographers"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80))
    img = db.Column(db.String)
    codeword = db.Column(db.String)
    description = db.Column(db.String)
    #speciality = db.Column(db.String)
    quotation = db.Column(db.String)

    def __init__(self, name, img, codeword, description, quotation):
        self.name = name
        self.img = img
        self.codeword = codeword
        self.description = description
        self.quotation = quotation     

    def json(self):
        return {"name":self.name, "img":self.img, "codeword":self.codeword, "description":self.description, "quotation":self.quotation}

    @classmethod
    def find_by_codeword(cls, codeword):
        return cls.query.filter_by(codeword=codeword).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()