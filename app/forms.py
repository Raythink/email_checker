from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateTimeField,FileField
from wtforms.validators import DataRequired


class ContactForm(FlaskForm):
    first_name = StringField('名', validators=[DataRequired()])
    last_name = StringField('姓', validators=[DataRequired()])
    tel1 = StringField('电话1')
    tel2 = StringField('电话2')
    # email = StringField('邮箱', validators=[DataRequired(), Email()])
    email = StringField('邮箱', validators=[DataRequired()])
    # email_validate_code = IntegerField('验证码')
    # email_validate_date = DateTimeField('验证时间')
    # email_validate_msg = StringField('MX反馈')

class ImportForm(FlaskForm):
    csv_file = FileField('上载CSV', validators=[DataRequired()])