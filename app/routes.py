import datetime
import os
import random

from sqlalchemy.exc import IntegrityError
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_paginate import Pagination, get_page_parameter
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin

from app.email_tool import EmailTool
from app.models import Contact
from app import db, app
from app.forms import ContactForm, ImportForm
from app.user import User
from app import load_user


# app = Blueprint('', __name__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # get username and password from request
        username = request.form['username']
        password = request.form['password']

        # authenticate user
        user = load_user('eadmin')
        if user and username == user.get_id() and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))

    else:
        return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# 主页，显示所有联系人
@app.route('/')
@app.route('/index')
def index():
    return contacts()


@app.route('/validate_run')
def validate_run():
    count = request.args.get('count', '')
    count = int(count)
    msg = "start job"
    if 1 <= count <= 100:
        msg = validate_job(count)
    else:
        msg = "count error"
    return msg


@app.route('/contacts')
@login_required
def contacts():
    search_term = request.args.get('search_term', '')
    email_validate_code = request.args.get('email_validate_code', '')
    if search_term == '':
        # contact_list = Contact.query.filter().all()

        if email_validate_code != '':
            filter = Contact.email_validate_code == email_validate_code
        else:
            filter = True
    else:
        if email_validate_code != '':
            filter = (Contact.first_name.ilike(f'%{search_term}%') | \
                      Contact.last_name.ilike(f'%{search_term}%') | \
                      Contact.tel1.ilike(f'%{search_term}%') | \
                      Contact.tel2.ilike(f'%{search_term}%') | \
                      Contact.email.ilike(f'%{search_term}%')) & (Contact.email_validate_code == email_validate_code)
        else:
            filter = Contact.first_name.ilike(f'%{search_term}%') | \
                     Contact.last_name.ilike(f'%{search_term}%') | \
                     Contact.tel1.ilike(f'%{search_term}%') | \
                     Contact.tel2.ilike(f'%{search_term}%') | \
                     Contact.email.ilike(f'%{search_term}%')

    contact_list = db.session.query(Contact).filter(filter)

    # 分页参数
    page = request.args.get(get_page_parameter(), type=int, default=1)

    pagesize = app.config.get('ITEMS_PER_PAGE')
    pagination = Pagination(page=page, per_page=pagesize, total=contact_list.count(), search=search_term,
                            record_name='contacts')
    # config.PER_PAGE这个参数写在了配置文件中，代表每页有多少条数据，start和end主要用于数据库里取数据的范围
    start = (page - 1) * pagesize
    end = start + pagesize
    show_list = contact_list.slice(start, end).all()

    return render_template('contacts.html', contacts=show_list, search_term=search_term, pagination=pagination)


# 添加联系人
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = ContactForm()
    if form.validate_on_submit():
        # Check if email already exists in database
        if Contact.query.filter_by(email=form.email.data).first():
            flash('电子邮件地址已存在，请使用其他电子邮件地址。')
            print("Email exists")
            return render_template('add.html', form=form, title='添加联系人')

        # # Validate email field
        # ret = validate_email(form.email.data)
        # if not ret:
        #     print("电子邮件地址格式错误")
        #     flash('电子邮件地址格式错误，请输入有效的电子邮件地址。')
        #     return render_template('add.html', form=form, title='添加联系人')
        # elif ret is None:
        #     print("电子邮件地址服务器验证失败")
        #     flash('电子邮件地址 服务器验证失败，请输入有效的电子邮件地址。')
        #     return render_template('add.html', form=form, title='添加联系人')

        contact = Contact(first_name=form.first_name.data,
                          last_name=form.last_name.data,
                          tel1=form.tel1.data,
                          tel2=form.tel2.data,
                          email=form.email.data)
        db.session.add(contact)
        db.session.commit()
        flash('添加成功！')
        return redirect(url_for('index'))
    else:
        flash('输入验证失败，请修改')
    return render_template('add.html', form=form, title='添加联系人')


# 编辑联系人
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    contact = Contact.query.get(id)
    if not contact:
        flash('联系人不存在')
        return redirect(url_for('index'))
    form = ContactForm(obj=contact)
    if form.validate_on_submit():
        form.populate_obj(contact)
        try:
            db.session.commit()
            flash('联系人已更新。')
            return redirect(url_for('index'))
        except IntegrityError:
            db.session.rollback()
            flash('电子邮件地址已存在，请使用其他电子邮件地址。')
    return render_template('edit.html', form=form)


# 删除联系人
@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    contact = Contact.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    flash('联系人已删除。')
    return redirect(url_for('contacts'))


# 删除全部联系人
@app.route('/delete_all', methods=['POST'])
@login_required
def delete_all():
    Contact.query.delete()
    db.session.commit()
    flash('所有联系人已删除。')
    return redirect(url_for('contacts'))


# 验证Email是否有效
@app.route('/validate/<int:id>', methods=['POST'])
@login_required
def validate(id):
    contact = Contact.query.get(id)
    if not contact:
        flash('联系人不存在')
        return redirect(url_for('contacts'))

    email = contact.email
    # 取得email地址
    # 验证
    tool = EmailTool()
    code, msg = tool.check_validity(email)
    contact.email_validate_code = code
    contact.email_validate_msg = msg
    contact.email_validate_date = datetime.datetime.now()

    try:
        db.session.commit()
        flash(f'验证完成: {msg}')
    except IntegrityError:
        db.session.rollback()
        flash('电子邮件地址已存在，请使用其他电子邮件地址。')
    return redirect(url_for('contacts'))


def validate_job(count):
    myfilter = (Contact.email_validate_code == None)
    # contact_list = db.session.query(Contact).filter(myfilter).limit(count)
    #
    random_number = random.randint(10000, 90000)
    # # print(random_number)
    # contact_list.update({Contact.email_validate_code: random_number})
    # db.session.commit()
    #
    subquery = db.session.query(Contact.id).filter(myfilter).limit(count).subquery()
    query = db.session.query(Contact).filter(Contact.id.in_(subquery))
    query.update({Contact.email_validate_code: random_number}, synchronize_session=False)
    db.session.commit()

    myfilter = (Contact.email_validate_code == random_number)
    contact_list = db.session.query(Contact).filter(myfilter).limit(count).all()

    tool = EmailTool()
    error_list = []
    total = len(contact_list)
    valid_ok = 0
    valid_hardbounce = 0
    for contact in contact_list:
        email = contact.email
        code, msg = tool.check_validity(email)
        contact.email_validate_code = code
        contact.email_validate_msg = msg
        contact.email_validate_date = datetime.datetime.now()
        if code == 250:
            valid_ok = valid_ok + 1
        elif code < 0:
            valid_hardbounce = valid_hardbounce + 1
        try:
            db.session.commit()
            # flash(f'验证完成: {msg}')
        except Exception as e:
            db.session.rollback()
            error_list.append(f"Email:{email} Err={type(e).__name__}")

    msg = f"总共 {total} 个记录，有效 {valid_ok} 个；硬退信 {valid_hardbounce} 个, 软退信 {total - valid_ok - valid_hardbounce} 个"
    return (msg)


@app.route('/validate_batch', methods=['POST'])
@login_required
def validate_batch():
    if request.method == 'POST':
        count = int(request.form.get('count'), 10)
        if count < 1 or count > 100:
            flash(f"数量过大或过小:{count}")
            return redirect(url_for('contacts'))

        msg = validate_job(count)
        flash(msg)
    return redirect(url_for('contacts'))


# 导出所有联系人到 CSV 文件
@app.route('/export')
@login_required
def export():
    csv_data = Contact.to_csv()
    response = Response(csv_data, mimetype='text/csv')
    response.headers.set('Content-Disposition', 'attachment', filename='contacts.csv')
    return response


# 导入Email数据
@app.route('/import_emails', methods=['POST'])
@login_required
def import_emails():
    # Get email list
    email_list = [email.strip() for email in request.form['email_list'].split('\n')]
    # Store to Contacts
    for email in email_list:
        contact = Contact(email=email)
        db.session.add(contact)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash(f'Email {email} 已存在，未导入。')
    flash(f'成功导入 {len(email_list)} 个Email。')
    return redirect(url_for('contacts'))


# 导入联系人数据
@app.route('/import', methods=['GET', 'POST'])
@login_required
def import_data():
    form = ImportForm(obj={})
    if request.method == 'POST':
        file = request.files['csv_file']
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            good_count, err_list = Contact.from_csv(file_path)
            flash(f'联系人成功导入 {good_count} 个。另有 {len(err_list)} 行email重复被丢弃')
            return redirect(url_for('index'))
    return render_template('import.html', form=form)
