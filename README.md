# CURYENT - Event Networking Platform

**CURYENT** connects event clients with professional service providers — DJs, photographers, caterers, event venues, and tent rental companies — all in one place. Plan your perfect event by discovering, booking, and communicating with trusted providers seamlessly.

**Live site**: https://dijayberry.pythonanywhere.com

## How to Use CURYENT

### For Event Clients (People Planning Events)

**1. Get Started**
- Visit the CURYENT website and click **Sign In**
- Register with your phone number and verify via SMS OTP
- Choose your role as **Client**

**2. Discover Service Providers**
- Browse through curated sections: **DJs**, **Venues**, **Photographers**, **Tents**, and **Caterers**
- Use the **search bar** to find specific providers by name or type
- Click **View All** on any section to see every available provider

**3. Book a Provider**
- View provider profiles to see their services, ratings, and availability
- Submit a booking request with your event details (date, time, location, budget)
- Pay securely using **M-Pesa**

**4. Communicate & Manage**
- Use the built-in **Chat** to discuss event details directly with your provider
- Track all your bookings in the **Bookings** page
- Receive **Notifications** for booking status updates (accepted, declined, completed)

**5. Rate & Review**
- After your event, leave ratings and feedback to help other clients make informed decisions

---

### For Service Providers (DJs, Photographers, Caterers, etc.)

**1. Create Your Profile**
- Register and choose your professional role: **DJ**, **Photographer**, **Caterer**, **Venue**, or **Tent Rental**
- Complete your profile with photos, services offered, pricing, and location
- Build your online presence to attract more clients

**2. Receive Booking Requests**
- Clients browsing your category can view your profile and send booking requests
- Get notified instantly when a new booking comes in

**3. Manage Your Bookings**
- View all incoming booking requests in your **Bookings** dashboard
- **Accept** or **decline** requests based on your availability
- Track upcoming events and past bookings

**4. Chat with Clients**
- Discuss event requirements, customize packages, and confirm details through real-time chat
- No need to switch to WhatsApp or another app — everything stays in CURYENT

**5. Get Paid**
- Receive payments directly via **M-Pesa** when clients confirm bookings
- Track your earnings and payout history

**6. Build Your Reputation**
- Collect ratings and reviews from satisfied clients
- Higher ratings improve your visibility and attract more bookings

---

### For Administrators

**1. Access the Admin Panel**
- Go to `/admin/login` and enter the admin password

**2. Manage the Platform**
- **Dashboard**: View overall statistics — total users, bookings, conversations, and more
- **Databases**: Browse and manage all data across 6 databases
- **Users**: Add, edit, or remove user accounts
- **Bookings**: Monitor and change booking statuses
- **UI Settings**: Customize button text, section titles, colors, and labels without touching code
- **System**: Reset databases and manage system operations

---

## Benefits

### For Event Clients
- **One-stop solution**: Find all event services in one platform instead of searching multiple websites
- **Verified providers**: Book from registered and rated professionals
- **Secure payments**: Pay through M-Pesa with confidence
- **Direct communication**: Chat with providers to clarify details before committing
- **Transparent ratings**: Read reviews from other clients before booking
- **Easy booking**: Submit requests and track status without phone calls or visits

### For Service Providers
- **More visibility**: Get discovered by clients actively looking for your services
- **No marketing cost**: Your profile works for you 24/7 without advertising expenses
- **Streamlined workflow**: Manage bookings, chat, and payments in one place
- **Build reputation**: Collect reviews that grow your credibility over time
- **Direct payments**: Receive money through M-Pesa without middlemen
- **Professional image**: A curated profile showcases your work and services

### For the Project
- **Growing network**: More users and providers create a stronger, more useful platform for everyone
- **Data-driven decisions**: Admin panel provides insights into user behavior and platform health
- **Customizable interface**: UI settings allow the platform to evolve without code changes
- **Community trust**: Rating and review system builds a self-regulating ecosystem
- **Scalable foundation**: Built with modular architecture that supports adding new service categories

## Tech Stack

- **Backend**: Python 3.11 + Flask
- **Database**: SQLite (6 databases for different modules)
- **Payments**: M-Pesa (C2B and B2C)
- **Messaging**: SMS via Africa's Talking API
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
| `AFRICASTALKING_USERNAME` | Africa's Talking username for SMS | Optional (debug mode without it) |
| `AFRICASTALKING_API_KEY` | Africa's Talking API key for SMS | Optional |
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
   - `AFRICASTALKING_USERNAME`: `cury`
   - `AFRICASTALKING_API_KEY`: `(your Africa's Talking API key)`
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
