# PythonAnywhere WSGI configuration file
# This file tells PythonAnywhere how to run your Flask app

import sys
import os

# Add your project directory to the Python path
project_home = '/home/dijayberry/curyent'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables for M-Pesa and WhatsApp
os.environ['MPESA_CONSUMER_KEY'] = 'xtaExvFW27YoYlReLwIqGAFBf6PfLPBhlmx0PQ1TK9V6Wb7s'
os.environ['MPESA_CONSUMER_SECRET'] = 'Go0k2BkhrAlKuuAUOWh6dPUSiE6kWhRnSA6bI2mGWrghwZUXjvJyQyC7mZejLii7'
os.environ['MPESA_SHORT_CODE'] = '5735986'
os.environ['MPESA_ENVIRONMENT'] = 'production'
os.environ['WASENDER_API_KEY'] = '6d2cd6b6f85f4defd517d1b6b8cba0f42c5f3cf957bad3a91de74b7b4c16ab7a'

# Import the Flask app
from curyent import app as application  # PythonAnywhere expects 'application'
