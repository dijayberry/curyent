# PythonAnywhere WSGI configuration file
# This file tells PythonAnywhere how to run your Flask app

import sys
import os

# Add your project directory to the Python path
project_home = '/home/dijayberry/curyent'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables for M-Pesa and SMS (Africa's Talking)
os.environ['MPESA_CONSUMER_KEY'] = 'xtaExvFW27YoYlReLwIqGAFBf6PfLPBhlmx0PQ1TK9V6Wb7s'
os.environ['MPESA_CONSUMER_SECRET'] = 'Go0k2BkhrAlKuuAUOWh6dPUSiE6kWhRnSA6bI2mGWrghwZUXjvJyQyC7mZejLii7'
os.environ['MPESA_SHORT_CODE'] = '5735986'
os.environ['MPESA_ENVIRONMENT'] = 'production'
os.environ['AFRICASTALKING_USERNAME'] = 'cury'
os.environ['AFRICASTALKING_API_KEY'] = 'atsk_3bcc67f1e1091266aa496d3a8be27b1644f2c2305246eadec2989517cbe2d6b1fd9d07a6'

# Import the Flask app
from curyent import app as application  # PythonAnywhere expects 'application'
