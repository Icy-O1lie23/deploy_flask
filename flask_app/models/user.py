from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash

class User:
    db = "sasquatch_reports"

    def __init__(self, data):
        self.user_id = data['user_id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password_hash = data['password_hash']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod
    def save(cls, data):
        query = "INSERT INTO users (first_name, last_name, email, password_hash, created_at, updated_at) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password_hash)s, NOW(), NOW());"
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def get_by_email(cls, email):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        data = {'email': email}
        result = connectToMySQL(cls.db).query_db(query, data)
        if result:
            return cls(result[0])
        else:
            return None  
        
    @classmethod
    def get_by_id(cls, user_id):
        query = "SELECT * FROM users WHERE user_id = %(user_id)s;"
        data = {'user_id': user_id}
        result = connectToMySQL(cls.db).query_db(query, data)
        if result:
            return cls(result[0])
        else:
            return None


    @staticmethod
    def validate_user(user):
        is_valid = True
        if "@" not in user['email'] or "." not in user['email']:
            flash("Invalid email address!")
            is_valid = False
        if len(user['first_name']) > 255:
            flash("First name must be less than 255 characters.")
            is_valid = False
        if len(user['last_name']) > 255:
            flash("Last name must be less than 255 characters.")
            is_valid = False
        if len(user['password']) > 255:
            flash("Password must be less than 255 characters.")
            is_valid = False
        if user['password'] != user['confirm_password']:
            flash("Passwords do not match!")
            is_valid = False
        return is_valid
