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

## Deployment to Render

### Option 1: Manual Deployment

1. **Push your code to GitHub**
2. **Go to** [Render Dashboard](https://dashboard.render.com/)
3. **Click "New +" → "Web Service"**
4. **Connect your GitHub repository**
5. **Configure**:
   - **Name**: curuent
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

### Free Domain (No Cost)

Render automatically assigns a free subdomain to your app. After deployment, your app will be available at:

**https://curyent.onrender.com**

This free domain includes:
- Automatic HTTPS/SSL certificate
- No setup required — works immediately after deployment
- M-Pesa callback URL is pre-configured to `https://curyent.onrender.com/api/mpesa/callback`

### Setting up Custom Domain (www.curyent.com) — Optional

If you later want to use a custom domain like `www.curyent.com`, follow these steps:

1. **Add the domain in Render**:
   - Go to your service in the Render Dashboard
   - Click on the **"Settings"** tab
   - Scroll to **"Custom Domains"**
   - Click **"Add Custom Domain"**
   - Enter `www.curyent.com` and click **Add**

2. **Configure DNS**:
   - Render will provide a CNAME record value (e.g., `xyz-abc.onrender.com`)
   - Go to your domain registrar's DNS settings for `curyent.com`
   - Add a **CNAME record**:
     - **Type**: CNAME
     - **Name**: `www`
     - **Value**: the CNAME value provided by Render
   - Wait for DNS propagation (usually 5-30 minutes)

3. **Enable HTTPS**:
   - Render automatically provisions SSL certificates for custom domains
   - After DNS is configured, Render will issue the certificate automatically
   - Your site will be accessible at `https://www.curyent.com`

4. **Update M-Pesa callback URL**:
   - Update `MPESA_CALLBACK_URL` in Render Dashboard under **Environment** variables to `https://www.curyent.com/api/mpesa/callback`

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
