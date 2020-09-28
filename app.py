import os
import re

import psycopg2
from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})


class DatabaseConnection:
    def __init__(self):
        db = 'postgres'
        if os.getenv('APP_SETTINGS') == 'testing':
            db = 'trial_test_db'
        conn = psycopg2.connect(
            host="localhost", database="daisy", user="walimike", password="password")
        conn.autocommit = True
        self.cursor = conn.cursor()
        print(self.cursor)
        print(db, 'HERE WE GO')

        users_table = """CREATE TABLE IF NOT EXISTS users(
             employee_no VARCHAR(25) PRIMARY KEY,
             user_name VARCHAR(25) UNIQUE NOT NULL,
             user_email VARCHAR(25) UNIQUE NOT NULL,
             user_password VARCHAR(225) NOT NULL
         )"""
        self.cursor.execute(users_table)
        # insert_user1 = "INSERT INTO users (employee_no, user_name, user_email, user_password) values ('moh123', 'nan','nanao@moh.com', 'letmeguess')"
        # self.cursor.execute(insert_user1)

        cases_table = """CREATE TABLE IF NOT EXISTS cases(
             case_no SERIAL PRIMARY KEY,
             disease VARCHAR(25) NOT NULL,
             school VARCHAR(50) NOT NULL,
             parish VARCHAR(25) NOT NULL,
             sub_county VARCHAR(25) NOT NULL,
             district VARCHAR(25) NOT NULL,
             region VARCHAR(25) NOT NULL
         )"""
        self.cursor.execute(cases_table)

        # insert_case1 = "INSERT INTO cases (disease, school, parish, sub_county, district, region) values ('Malaria', 'VINE INTERNATIONAL SCHOOL', 'A', 'B', 'Kampala', 'CENTRAL')"
        # self.cursor.execute(insert_case1)

        # insert_case2 = "INSERT INTO cases (disease, school, parish, sub_county, district, region) values ('Pneumonia', 'VINE INTERNATIONAL SCHOOL', 'A', 'B', 'Kampala', 'CENTRAL')"
        # self.cursor.execute(insert_case2)

        # insert_case3 = "INSERT INTO cases (disease, school, parish, sub_county, district, region) values ('Typhoid', 'VINE INTERNATIONAL SCHOOL', 'A', 'B', 'Kampala', 'CENTRAL')"
        # self.cursor.execute(insert_case3)

        # insert_case1 = "INSERT INTO cases (disease, school, parish, sub_county, district, region) values ('Malaria', 'St.Peters Naalya SSS', 'A', 'B', 'Kampala', 'CENTRAL')"
        # self.cursor.execute(insert_case1)

    def insert_user(self, employee_no, user_name, user_email, user_password):
        insert_user = "INSERT INTO users (employee_no, user_name, user_email, user_password) values ('{}', '{}', '{}', '{}')".format(
            employee_no, user_name, user_email, user_password)
        self.cursor.execute(insert_user)

    def login_user(self, user_name, user_password):
        select_user = "SELECT user_name, user_password FROM users WHERE user_name = '{}' and user_password = '{}'".format(
            user_name, user_password)
        self.cursor.execute(select_user)
        return [user_name, user_password]

    def get_user(self, user_name):
        get_user = "SELECT * FROM users WHERE user_name = '{}'".format(
            user_name)
        self.cursor.execute(get_user)
        result = self.cursor.fetchone()
        return result

    def get_users(self):
        get_users = "SELECT * FROM users ORDER BY employee_no ASC"
        self.cursor.execute(get_users)
        result = self.cursor.fetchall()
        return result

    def get_cases(self):
        get_cases = "SELECT * FROM cases ORDER BY case_no ASC"
        self.cursor.execute(get_cases)
        result = self.cursor.fetchall()
        return result

    # def get_total_no_of_cases(self):
    #     get_total = "SELECT count(*) FROM cases"
    #     self.cursor.execute(get_total)
    #     result = self.cursor.fetchone()
    #     return result

    # def get_total_no_of_schools(self):
    #     get_total = "SELECT COUNT(DISTINCT school) FROM cases"
    #     self.cursor.execute(get_total)
    #     result = self.cursor.fetchone()
    #     return result


db = DatabaseConnection()


class User():
    """Users class defining the user model"""

    def __init__(self, employee_no, user_name, user_email, user_password):
        self.employee_no = employee_no
        self.user_name = user_name
        self.user_email = user_email
        self.user_password = user_password


class Case():
    """Users class defining the user model"""

    def __init__(self, disease, school, parish, sub_county, district, region):
        self.disease = disease
        self.school = school
        self.parish = parish
        self.sub_county = sub_county
        self.district = district
        self.region = region


# def get_cases(self):
#     get_cases = "SELECT * FROM cases ORDER BY case_no ASC"
#     self.cursor.execute(get_cases)
#     result = self.cursor.fetchall()
#     return result


class User_Controller:

    @staticmethod
    def login():
        user_input = request.get_json(force=True)
        username = user_input.get("user_name")
        password = user_input.get("user_password")

        user = db.get_user(username)
        if user:
            return jsonify({
                'success': f"You have successfully been logged in as {username}"
            }), 200
        return jsonify({'message': f"{username} does not exist"}), 400

    @staticmethod
    def sign_up():
        """Register a user"""
        user_input = request.get_json(force=True)
        employee_no = user_input.get("employee_no")
        user_name = user_input.get("user_name")
        user_email = user_input.get("user_email")
        user_password = user_input.get("user_password")
        users = db.get_users()
        for user in users:
            if user_name == user[1]:
                return jsonify({'message': f"User {user_name} already exists"}), 400
            if user_email == user[2]:
                return jsonify({'message': "Email belongs to another account"}), 400
        new_user = User(employee_no, user_name, user_email, user_password)
        db.insert_user(new_user.employee_no, new_user.user_name, new_user.user_email,
                       new_user.user_password)
        return jsonify({"message": f"User {user_name} successfully created"}), 201


class Case_Controller:
    @staticmethod
    def get_all_cases():
        cases_list = []
        cases = db.get_cases()
        for case in cases:
            case_dict = {
                "case_no": case[0],
                "disease": case[1],
                "school": case[2],
                "parish": case[3],
                "sub_county": case[4],
                "district": case[5],
                "region": case[6]
            }
            cases_list.append(case_dict)
        return jsonify({'cases': cases_list, 'length': len(cases_list)}), 200


@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    return User_Controller.login()


@app.route('/api/v1/auth/signup', methods=['POST'])
def user_signup():
    return User_Controller.sign_up()

@app.route('/api/v1/cases', methods=['GET'])
def get_all_cases():
    return Case_Controller.get_all_cases()

@app.route('/')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(debug=True)
