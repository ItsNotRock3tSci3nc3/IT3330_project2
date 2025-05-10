from flask import Flask, render_template, request, url_for, redirect
import mysql.connector
from mysql.connector import errorcode
import pygal
from pygal.style import *
import sys

#create a flask app object and set app variables
app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SECRECT_KEY"] = 'your secret key'
app.secret_key = 'your secret key'

#create a connection object to the module2 database
def get_db_connection():
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            port="6603",
            database="hr"
        )
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your username or password.")
            exit()
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist.")
            exit()
        else:
            print(err)
            print("ERROR: Service not available")
            exit()

    return mydb

@app.route('/')
def index():
    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)
    #Homepage: list all dependents with their details and associated employee.
    try:
        # Join dependents with employees to get employee name and ID for each dependent
        query = """
            SELECT d.dependent_id AS dep_id, d.first_name, d.last_name, d.relationship, d.employee_id, e.first_name AS emp_first, e.last_name AS emp_last
            FROM dependents d
            JOIN employees e ON d.employee_id = e.employee_id;
        """
        cursor.execute(query)
        dependents = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching dependents: {e}", file=sys.stderr)
        dependents = []  # Fallback to empty list if query fails

    cursor.close()
    return render_template('index.html', dependents=dependents)


@app.route('/edit/<int:dep_id>', methods=['GET', 'POST'])
def edit_dependent(dep_id):
    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)
    """Edit a dependent's details."""
    if request.method == 'POST':
        # Form was submitted: process update
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        relationship = request.form.get('relationship')
        try:
            update_query = """
                UPDATE dependents
                SET first_name=%s, last_name=%s, relationship=%s
                WHERE dependent_id=%s;
            """
            cursor.execute(update_query, (first_name, last_name, relationship, dep_id))
            mydb.commit()
        except Exception as e:
            print(f"Error updating dependent: {e}", file=sys.stderr)
            # In a real app, you might flash an error message here
        return redirect(url_for('index'))
    else:
        # GET request: show the edit form with current dependent data
        try:
            cursor.execute(
                "SELECT dependent_id, first_name, last_name, relationship, employee_id FROM dependents WHERE dependent_id=%s",
                (dep_id,)
            )
            dependent = cursor.fetchone()
        except Exception as e:
            print(f"Error fetching dependent: {e}", file=sys.stderr)
            dependent = None
        if dependent is None:
            return "Dependent not found.", 404
        
        cursor.close()
        return render_template('edit_dependent.html', dependent=dependent)


@app.route('/delete/<int:dep_id>', methods=['POST'])
def delete_dependent(dep_id):
    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)
    try:
        cursor.execute("DELETE FROM dependents WHERE dependent_id=%s", (dep_id,))
        mydb.commit()
        cursor.close()
        return '', 204  # Success, no content
    except Exception as e:
        print(f"Error deleting dependent: {e}", file=sys.stderr)
        cursor.close()
        return 'Error deleting dependent', 500

if __name__ == '__main__':
    # Run the Flask development server on localhost
    app.run(debug=True)