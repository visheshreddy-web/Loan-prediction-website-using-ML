import flask 
import pickle
import pandas as pd
import numpy as np
import mysql.connector
from mysql.connector import Error
from sklearn.preprocessing import StandardScaler
from flask import Flask, request, render_template,redirect,url_for,flash


#load models at top of app to load into memory only one time
with open('models/loan_application_model_lr.pickle', 'rb') as f:
    clf_lr = pickle.load(f)


# with open('models/knn_regression.pkl', 'rb') as f:
#     knn = pickle.load(f)    
ss = StandardScaler()


genders_to_int = {'MALE':1,
                  'FEMALE':0}

married_to_int = {'YES':1,
                  'NO':0}

education_to_int = {'GRADUATED':1,
                  'NOT GRADUATED':0}

dependents_to_int = {'0':0,
                      '1':1,
                      '2':2,
                      '3+':3}

self_employment_to_int = {'YES':1,
                          'NO':0}                      

property_area_to_int = {'RURAL':0,
                        'SEMIRURAL':1, 
                        'URBAN':2}




app = flask.Flask(__name__, template_folder='templates')
@app.route('/')
def main():
    return (flask.render_template('index.html'))
@app.route('/reject')
def reject():
    return (flask.render_template('reject.html'))
@app.route('/accept')
def accept():
    return (flask.render_template('accept.html'))
@app.route('/report')
def report():
    return (flask.render_template('report.html'))
@app.route("/Loan_Application", methods=['GET', 'POST'])
def Loan_Application():
    
    if flask.request.method == 'GET':
        return (flask.render_template('Loan_Application.html'))
    
    if flask.request.method =='POST':
        
        #get input
        #gender as string
        genders_type = flask.request.form['genders_type']
        #marriage status as boolean YES: 1 , NO: 0
        marital_status = flask.request.form['marital_status']
        #Dependents: No. of people dependent on the applicant (0,1,2,3+)
        dependents = flask.request.form['dependents']
        
        #dependents = dependents_to_int[dependents.upper()]
        
        #education status as boolean Graduated, Not graduated.
        education_status = flask.request.form['education_status']
        #Self_Employed: If the applicant is self-employed or not (Yes, No)
        self_employment = flask.request.form['self_employment']
        #Applicant Income
        applicantIncome = float(flask.request.form['applicantIncome'])
        #Co-Applicant Income
        coapplicantIncome = float(flask.request.form['coapplicantIncome'])
        #loan amount as integer
        loan_amnt = float(flask.request.form['loan_amnt'])
        #term as integer: from 10 to 365 days...
        term_d = int(flask.request.form['term_d'])
        # credit_history
        credit_history = int(flask.request.form['credit_history'])
        # property are
        property_area = flask.request.form['property_area']
        #property_area = property_area_to_int[property_area.upper()]

        #create original output dict
        output_dict= dict()
        output_dict['Applicant Income'] = applicantIncome
        output_dict['Co-Applicant Income'] = coapplicantIncome
        output_dict['Loan Amount'] = loan_amnt
        output_dict['Loan Amount Term']=term_d
        output_dict['Credit History'] = credit_history
        output_dict['Gender'] = genders_type
        output_dict['Marital Status'] = marital_status
        output_dict['Education Level'] = education_status
        output_dict['No of Dependents'] = dependents
        output_dict['Self Employment'] = self_employment
        output_dict['Property Area'] = property_area
        


        x = np.zeros(21)
    
        x[0] = applicantIncome/70
        x[1] = coapplicantIncome/70
        x[2] = loan_amnt/70
        x[3] = term_d
        x[4] = credit_history
        
        

        print('------this is array data to predict-------')
        print('X = '+str(x))
        print('------------------------------------------')

        pred = clf_lr.predict([x])[0]
        x[0] = applicantIncome*70
        x[1] = coapplicantIncome*70
        x[2] = loan_amnt*70
        
        if pred==1:
            res = '🎊🎊Congratulations! your Loan Application has been Approved!🎊🎊'
        else:
                res = '😔😔Unfortunatly your Loan Application has been Denied😔😔'
        

 
        #render form again and add prediction
        return flask.render_template('Loan_Application.html', 
                                     original_input=output_dict,
                                     result=res,flag=pred)

        

#app = Flask(__name__)

# Replace with your MySQL connection details
db_config = {
    'user': 'admin',
    'password': '1234@QWer',
    'host': 'localhost',
    'database': 'main'
}

# Connect to MySQL database
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Register user
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return (flask.render_template('register.html'))
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        gender = request.form['gender']
        birthdate = request.form['birthdate']

        # Insert data into database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, password, first_name, last_name, gender, birthdate) VALUES (%s, %s, %s, %s, %s, %s, %s)", (username, email, password, first_name, last_name, gender, birthdate))
        conn.commit()
        conn.close()

        # Redirect to home page
        #flash('Registration successful!', 'success')  # Flash a success message
    return redirect(url_for('main'))
db_config = {
    'user': 'admin',
    'password': '1234@QWer',
    'host': 'localhost',
    'database': 'main'
}

# Connect to MySQL database
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']

        # Validate user credentials
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            # Authentication successful
            return redirect(url_for('Loan_Application'))  # Redirect to the main page after successful login
        else:
            # Authentication failed
            error = 'Invalid username or password'
            return render_template('login.html', error=error)

if __name__ == '__main__':
    app.run(debug=True)