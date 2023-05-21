import csv
import io

from sqlalchemy.exc import IntegrityError

from app import db


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    tel1 = db.Column(db.String(20))
    tel2 = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True)
    email_validate_code = db.Column(db.Integer)
    email_validate_date = db.Column(db.DateTime)
    email_validate_msg = db.Column(db.String(100))

    @staticmethod
    def from_csv(file_path):
        good_count=0
        err_list=[]
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:

                #数据合法性检查
                email = row.get('email',"")
                if email=="":
                    # 无email记录
                    continue

                first_name = row.get('first_name', "")
                last_name = row.get('last_name',"")
                tel1 =  row.get('tel1',"")
                tel2 = row.get('tel2',"")

                try:

                    contact = Contact(
                        first_name=first_name,
                        last_name=last_name,
                        tel1=tel1,
                        tel2=tel2,
                        email=email
                    )
                    db.session.add(contact)
                    db.session.commit()
                    good_count=good_count+1
                except IntegrityError as e:
                    #重复条目
                    err_list.append(row)
                    db.session.rollback()
        return good_count,err_list

    @staticmethod
    def to_csv():
        contacts = Contact.query.all()
        headers = ['id', 'first_name', 'last_name', 'tel1', 'tel2', 'email', 'email_validate_code',
                   'email_validate_date', 'email_validate_msg']
        rows = [[getattr(contact, header) for header in headers] for contact in contacts]
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerows(rows)
        return output.getvalue()

    def __repr__(self):
        return f'<Contact {self.first_name} {self.last_name}>'
