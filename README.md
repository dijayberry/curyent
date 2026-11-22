# Curyent - Event Service Provider Platform

Curyent is a Flask-based web application that connects event clients with service providers like DJs, photographers, caterers, event venues, and tent rental companies.

## Features

- **User Registration & Authentication** with WhatsApp OTP verification
- **Multiple Service Provider Roles**: DJ, Photographer, Caterer, Event Venue, Tent Rental
- **Booking System** with M-Pesa payment integration
- **Real-time Chat** between clients and providers
- **Notifications System** for booking updates and payouts
- **Profile Management** with ratings and feedback
- **Search** across all service providers

## Tech Stack

- **Backend**: Python 3.11 + Flask
- **Database**: SQLite (5 databases for different modules)
- **Payments**: M-Pesa (C2B and B2C)
- **Messaging**: WhatsApp via Wasender API
- **Frontend**: HTML/CSS/JavaScript

## Prerequisites

- Python 3.11 or higher
- Git

## Local Development

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd curuent
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # or
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python curuent.py
   ```

5. **Open** http://localhost:5000 in your browser

## Environment Variables

The following environment variables can be configured:

| Variable | Description | Required |
|----------|-------------|----------|
| `WASENDER_API_KEY` | Wasender API key for WhatsApp messages | Optional (debug mode without it) |
| `MPESA_CONSUMER_KEY` | Safaricom Daraja API consumer key | Optional |
| `MPESA_CONSUMER_SECRET` | Safaricom Daraja API consumer secret | Optional |
| `MPESA_SHORTCODE` | M-Pesa shortcode for payments | Optional |
| `MPESA_CALLBACK_URL` | Public URL for M-Pesa C2B callback | Optional |
| `SECRET_KEY` | Flask secret key for sessions | Optional (defaults to built-in key) |

## Deployment to PythonAnywhere (Free, No Credit Card)

PythonAnywhere is a free Python hosting platform that doesn't require a credit card.

### Step 1: Create a PythonAnywhere Account

1. Go to [https://www.pythonanywhere.com/](https://www.pythonanywhere.com/)
2. Click **"Sign up"** (top right)
3. Choose the **"Beginner"** plan (it's **free**)
4. Fill in your username (e.g., `dijayberry`), email, and password
5. Check your email to confirm your account
6. Log in to PythonAnywhere

### Step 2: Upload Your Code

1. In PythonAnywhere, click the **"Consoles"** tab
2. Click **"Open bash"** to open a terminal
3. Run these commands:
   ```bash
   git clone https://github.com/dijayberry/curyent.git
   cd curyent
   pip install -r requirements.txt
   ```

### Step 3: Configure the Web App

1. Click the **"Web"** tab
2. Click **"Add a new web app"**
3. Choose **"Manual configuration"** and select **Python 3.11**
4. Click **"Configure"**
5. Click the **"WSGI configuration file"** link
6. Replace all the content with the contents of `wsgi.py` from your project
7. Click **"Save"**

### Step 4: Set Environment Variables

1. In the **"Web"** tab, click **"Variables"** under **"Code"** section
2. Add these environment variables:
   - `MPESA_CONSUMER_KEY`: `xtaExvFW27YoYlReLwIqGAFBf6PfLPBhlmx0PQ1TK9V6Wb7s`
   - `MPESA_CONSUMER_SECRET`: `Go0k2BkhrAlKuuAUOWh6dPUSiE6kWhRnSA6bI2mGWrghwZUXjvJyQyC7mZejLii7`
   - `MPESA_SHORT_CODE`: `5735986`
   - `MPESA_ENVIRONMENT`: `production`
   - `WASENDER_API_KEY`: `6d2cd6b6f85f4defd517d1b6b8cba0f42c5f3cf957bad3a91de74b7b4c16ab7a`
3. Click **"Save"**

### Step 5: Reload the Web App

1. Click the **"Reload"** button at the top of the **"Web"** tab
2. Your app will be live at: **https://dijayberry.pythonanywhere.com**

### Free Domain

Your app will be available at:

**https://dijayberry.pythonanywhere.com**

This free domain includes:
- Automatic HTTPS/SSL certificate
- No credit card required
- Free forever (with monthly quota limits)

### Setting up Custom Domain (www.curyent.com) — Optional

If you later want to use a custom domain like `www.curyent.com`:

1. **In PythonAnywhere**, go to the **"Web"** tab → **"Domains"** section
2. Add your custom domain
3. **Configure DNS** at your domain registrar to point to PythonAnywhere's servers
4. PythonAnywhere will provide the DNS records you need

## Deployment to Render (Requires Credit Card)

> **Note:** Render requires a credit card even for the free tier. See PythonAnywhere above for a free alternative.

### Option 1: Manual Deployment

1. **Push your code to GitHub**
2. **Go to** [Render Dashboard](https://dashboard.render.com/)
3. **Click "New +" → "Web Service"**
4. **Connect your GitHub repository**
5. **Configure**:
   - **Name**: curyent
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn curyent:app --bind 0.0.0.0:$PORT`
   - **Instance Type**: Free
6. **Add environment variables** (optional, for M-Pesa and WhatsApp)
7. **Click "Create Web Service"**

### Option 2: Deploy with render.yaml

1. **Push your code to GitHub** with the `render.yaml` file
2. **Go to** [Render Dashboard](https://dashboard.render.com/)
3. **Click "New +" → "From Git Repo"**
4. **Select your repository**
5. Render will automatically detect and apply the configuration

## Database Notes

- The application uses SQLite databases stored in the `base/` directory
- Databases are created automatically on first run
- For production, consider migrating to PostgreSQL for better scalability
- The `/reset-databases` endpoint can reset all databases (use with caution)

## Production Considerations

- **File Uploads**: Currently stored locally. For production, consider using cloud storage (AWS S3, Cloudinary)
- **Database**: SQLite works for small-scale deployments. For high traffic, migrate to PostgreSQL
- **Background Tasks**: The payout scheduler runs as a daemon thread. For production, consider using Celery with Redis
- **Secrets**: Never commit API keys to version control. Use environment variables

## License

Private project
