from flask import Flask, request, jsonify, send_file
from math import *
import os
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

app = Flask(__name__)

def calculate_loan(loan_amount, annual_interest_rate, loan_term_years):
    """
    Calculates the monthly payment and total repayment for a loan.
    Args:
        loan_amount (float): The principal loan amount.
        annual_interest_rate (float): The annual interest rate as a percentage.
        loan_term_years (float): The loan term in years.
    Returns:
        dict: A dictionary containing 'monthly_payment' and 'total_repayment',
              or a string error message.
    """
    if loan_amount < 0 or annual_interest_rate < 0 or loan_term_years <= 0:
        return "Error: Loan amount, interest rate, and term must be positive numbers."

    # Convert annual interest rate to monthly rate
    monthly_interest_rate = (annual_interest_rate / 100) / 12

    # Convert loan term in years to months
    total_payments = loan_term_years * 12

    try:
        if monthly_interest_rate == 0:
            # Simple principal division if interest rate is zero
            monthly_payment = loan_amount / total_payments
        else:
            # Loan payment formula
            # M = P [ i(1 + i)^n ] / [ (1 + i)^n – 1]
            numerator = monthly_interest_rate * (1 + monthly_interest_rate) ** total_payments
            denominator = (1 + monthly_interest_rate) ** total_payments - 1
            if denominator == 0:  # Handle the edge case
                return "Error: Cannot calculate payment with zero denominator."
            monthly_payment = loan_amount * (numerator / denominator)

        total_repayment = monthly_payment * total_payments
        return {
            'monthly_payment': round(monthly_payment, 2),
            'total_repayment': round(total_repayment, 2)
        }
    except Exception as e:
        return f"Error: An unexpected error occurred: {e}"
def perform_calculation(num1, num2, operator, mode):
    """Performs a basic arithmetic calculation based on the given operator.

    Args:
        num1 (float): The first number.
        num2 (float): The second number.
        operator (str): The operator (+, -, *, /, ^, root).
        mode (str):  Indicates the type of calculation ('basic' or 'currency')

    Returns:
        float: The result of the calculation, or an error message string.
    """
    try:
        if operator == '+':
            result = num1 + num2
        elif operator == '-':
            result = num1 - num2
        elif operator == '*':
            result = num1 * num2
        elif operator == '/':
            if num2 == 0:
                return "Error: Division by zero is not allowed."
            result = num1 / num2
        elif operator == '^':
            result = num1 ** num2
        elif operator == 'root':
            if num2 == 0:
                return "Error: Cannot take 0th root."
            if num2 < 0:
                return "Error: Cannot take root of negative number."
            result = num1 ** (1 / num2)
        else:
            return "Error: Invalid operator. Please use +, -, *, /, ^, or root."
        return result
    except Exception as e:
        return f"Error: An unexpected error occurred during calculation: {e}"



@app.route('/', methods=['GET'])
def index():
    """
    Serves the main HTML file.  This is crucial for Flask to know
    how to route the user to your web application.
    """
    return send_file('index.html') #  index.html is in the same directory as calc.py


@app.route('/calculate', methods=['POST'])
def calculate():
    """
    Handles calculation requests, including basic arithmetic, loan calculations,
    and now, graph plotting.
    """
    data = request.get_json()
    mode = data.get('mode')

    if mode == 'loan':
        loan_amount = data.get('loan_amount')
        annual_interest_rate = data.get('annual_interest_rate')
        loan_term_years = data.get('loan_term_years')

        if any(arg is None for arg in [loan_amount, annual_interest_rate, loan_term_years]):
            return jsonify({'error': 'Missing loan calculation arguments.'}), 400

        try:
            loan_amount = float(loan_amount)
            annual_interest_rate = float(annual_interest_rate)
            loan_term_years = float(loan_term_years)
        except ValueError:
            return jsonify({'error': 'Invalid input: Loan parameters must be numbers.'}), 400

        result = calculate_loan(loan_amount, annual_interest_rate, loan_term_years)

        if isinstance(result, str) and result.startswith("Error"):
            return jsonify({'error': result}), 400
        else:
            return jsonify(result), 200

    elif mode == 'basic' or mode == 'currency':
        # Existing logic for basic and currency modes
        num1 = data.get('num1')
        num2 = data.get('num2')
        operator = data.get('operator')

        if any(arg is None for arg in [num1, num2, operator]):
            return jsonify({'error': 'Missing basic/currency arguments (num1, num2, operator)'}), 400

        # Convert num1 and num2 to float for calculations
        try:
            num1 = float(num1)
            num2 = float(num2)
        except ValueError:
            return jsonify({'error': 'Invalid input: num1 and num2 must be numbers'}), 400

        result = perform_calculation(num1, num2, operator, mode)

        if isinstance(result, str) and result.startswith("Error"):
            return jsonify({'error': result}), 400
        else:
            return jsonify({'result': result}), 200

    elif mode == 'graph':
        # handle graphing
        expression = data.get('expression')
        xmin = data.get('xmin', -10)  # default values
        xmax = data.get('xmax', 10)
        num_points = 400

        if not expression:
            return jsonify({'error': 'Missing expression for graphing.'}), 400

        x = np.linspace(xmin, xmax, num_points)
        try:
            # Use a safer alternative to eval
            y = [eval(expression.replace("^","**"), {"x": val,
                                                     "sin": sin,
                                                     "cos": cos,
                                                     "tan": tan,
                                                     "exp": exp,
                                                     "log": log,
                                                     "sqrt": sqrt}) for val in x]
        except Exception as e:
            return jsonify({'error': f'Error evaluating expression: {e}'}), 400

        # Generate the graph
        plt.figure(figsize=(8, 6))
        plt.plot(x, y)
        plt.xlabel('x')
        plt.ylabel('f(x)')
        plt.title(f'Graph of {expression}')
        plt.grid(True)

        # Save the graph to a BytesIO object
        img_buf = BytesIO()
        plt.savefig(img_buf, format='png')
        img_buf.seek(0)
        plt.close() # Important:  Close to prevent memory leak

        # Return the image as a file using send_file
        return send_file(img_buf, mimetype='image/png')

    else:
        return jsonify({'error': 'Invalid mode specified'}), 400



if __name__ == "__main__":
    # Adjust host and port if necessary for your environment
    app.run(debug=True, host='0.0.0.0', port=5000)
