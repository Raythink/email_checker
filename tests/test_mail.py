
from validate_email import validate_email

is_valid = validate_email('example@hotmail.com', check_mx=True)

if is_valid:
    print('Email is valid')
else:
    print('Email is invalid')