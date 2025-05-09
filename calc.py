from flask import Flask, request, jsonify, send_file
from math import *
import os

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
            if denominator == 0: # Should not happen with positive interest rate, but for safety
                return "Error: Cannot calculate payment with provided details."
            monthly_payment = loan_amount * (numerator / denominator)

        total_repayment = monthly_payment * total_payments

        return {
            'monthly_payment': monthly_payment,
            'total_repayment': total_repayment
        }
    except Exception as e:
        return f"Error during calculation: {e}"


def perform_calculation(num1, num2, operator, mode='basic'):
    """
    Performs a calculation based on the given numbers, operator, and mode.
    (This function is primarily for basic/currency modes now)
    Args:
        num1 (float): The first number.
        num2 (float): The second number.
        operator (str): The operator (+, -, *, /, %, ^, sqrt, log, convert).
        mode (str, optional): The calculator mode ('basic', 'currency'). Defaults to 'basic'.
    Returns:
        float: The result of the calculation, or an error message.
    """
    try:
        if mode == 'basic':
            if operator == '+':
                return num1 + num2
            elif operator == '-':
                return num1 - num2
            elif operator == '*':
                return num1 * num2
            elif operator == '/':
                if num2 == 0:
                    return "Error: Division by zero"
                return num1 / num2
            elif operator == '%':
                if num2 == 0:
                    return "Error: Division by zero"
                return num1 % num2
            elif operator == '^':
                return num1 ** num2
            elif operator == 'sqrt':
                if num2 < 0:
                    return "Error: Square root of a negative number"
                return num2 ** 0.5
            elif operator == 'log':
                if num1 <= 0 or num2 <= 0:
                    return "Error: Logarithm of non-positive number"
                # Added a check for valid base (num1) as log base 1 is undefined
                if num1 == 1:
                     return "Error: Logarithm base cannot be 1"
                return log(num2, num1)  # Log base num1 of num2
            else:
                return "Error: Invalid operator for basic mode"
        elif mode == 'currency':
            # Placeholder for currency conversion logic
            # In a real application, you would use an API or a database
            # to get the exchange rate and perform the conversion.
            if operator == 'convert':
                if num1 == 0:
                    return "Error: Invalid exchange rate"
                return num2 * num1  # num1 is the exchange rate, num2 is the amount
            else:
                return "Error: Invalid operator for currency mode.  Use 'convert'"
        else:
            return "Error: Invalid mode" # This case should ideally not be reached with the current route logic
    except Exception as e:
        return f"Error: {e}"


@app.route('/', methods=['GET', 'POST'])
def calculate():
    """
    Handles the main endpoint for performing calculations.
    Accepts GET to serve the calculator, and POST to perform calculations.
    Handles different calculation modes ('basic', 'currency', 'loan').
    """
    if request.method == 'GET':
        # Serve the index.html file from the root directory
        return send_file('index.html')
    elif request.method == 'POST':
        data = request.get_json()
        mode = data.get('mode', 'basic')

        if mode == 'loan':
            loan_amount = data.get('loan_amount')
            annual_interest_rate = data.get('annual_interest_rate')
            loan_term_years = data.get('loan_term_years')

            # Basic validation for loan inputs
            if any(arg is None for arg in [loan_amount, annual_interest_rate, loan_term_years]):
                 return jsonify({'error': 'Missing loan arguments (loan_amount, annual_interest_rate, loan_term_years)'}), 400
            try:
                loan_amount = float(loan_amount)
                annual_interest_rate = float(annual_interest_rate)
                loan_term_years = float(loan_term_years)
            except ValueError:
                 return jsonify({'error': 'Invalid input: loan arguments must be numbers'}), 400


            result = calculate_loan(loan_amount, annual_interest_rate, loan_term_years)

            if isinstance(result, str) and result.startswith("Error"):
                return jsonify({'error': result}), 400
            else:
                # Return the calculated monthly payment and total repayment
                return jsonify(result), 200 # result is already a dictionary

        elif mode in ['basic', 'currency']:
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
        else:
            return jsonify({'error': 'Invalid mode specified'}), 400


if __name__ == "__main__":
    # Adjust host and port if necessary for your environment
    app.run(debug=True, host='0.0.0.0', port=5000)