from flask_sqlalchemy import SQLAlchemy, Model
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey


class CustomModel(Model):
    def as_dict(self):
        temp = {}
        for x in self.__table__.columns:
            if str(type(getattr(self, x.name))) == "<class 'datetime.datetime'>":
                temp[x.name] = str(getattr(self, x.name))
            else:
                temp[x.name] = getattr(self, x.name)
        return temp


db = SQLAlchemy(model_class=CustomModel)


class SaveData(db.Model):

    save_seq = db.Column(db.Integer, primary_key=True, nullable=False)

    device_id = db.Column(db.String, nullable=False)

    data = db.Column(db.JSON, nullable=False)

    app_version = db.Column(db.String, nullable=False)

    add_date = db.Column(db.DateTime, nullable=False)



class CustomLevel(db.Model):
    level_seq = db.Column(db.Integer, primary_key=True, nullable=False)

    level_id = db.Column(db.String, nullable=False)

    maker_device_id = db.Column(db.String, nullable=False)
    level_data = db.Column(db.JSON, nullable=False)

    app_version = db.Column(db.String, nullable=False)

    title = db.Column(db.String, nullable=False)

    add_date = db.Column(db.DateTime, nullable=False)

    is_public = db.Column(db.Boolean, nullable=False)


