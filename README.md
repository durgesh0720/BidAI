BID.ai - Real-Time Marketplace Platform

BID.ai is a Django-based web application designed as a marketplace where users can create product listings, redeem credits for views, and monitor performance in real-time. It features a responsive UI with Tailwind CSS, WebSocket integration for live updates, and role-based access control (e.g., admin dashboard for staff/superusers).

## Table of Contents
- [Features](#features)
- [Bonus Criteria](#bonus-criteria)
- [Technologies](#technologies)
- [Setup Instructions](#setup-instructions)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features
- **User Authentication**: Login/logout functionality with role-based access (regular users, staff, superusers).
- **Product Management**: Users can add products via a sleek form accessible from the navbar.
- **Credit Redemption**: Users can redeem credits (1 credit = 1 view) for their own products, with a modern UI and progress bar.
- **Real-Time Updates**: WebSocket integration via Django Channels and Redis for live dashboard updates (e.g., wallet balance, product views).
- **Admin Dashboard**: Staff/superusers can view total listings, purchases, and users, with a Chart.js bar chart and tables for top sellers and recent purchases.
- **Responsive Navbar**: Tailwind-styled navbar with conditional "Admin Dashboard" link for staff/superusers.

## Bonus Criteria
- **Professional UI/UX**: Tailwind CSS ensures a modern, responsive design across all pages (e.g., hover effects, shadows, progress bars).
- **Real-Time Features**: WebSocket updates for admin dashboard metrics and user dashboard balance.
- **Chart Visualization**: Bar chart in admin dashboard visualizes key metrics (listings, purchases, users).

## Technologies
- **Backend**: Django 4.x, Django Channels, Redis
- **Frontend**: HTML, Tailwind CSS 2.2.19, Chart.js
- **Database**: SQLite (default; configurable for PostgreSQL)
- **Server**: Daphne (ASGI) for WebSocket support
- **Environment**: Python 3.11+, Virtualenv

## Setup Instructions
Follow these steps to set up BID.ai locally on Windows (adaptable for other OS).

### Prerequisites
- Python 3.11+
- Redis Server (for WebSockets)
- Git

### Installation
#### Clone the Repository:
```bash
git clone https://github.com/durgesh0720/bidai.git
cd bidai
```

#### Set Up Virtual Environment:
```bash
python -m venv env
source env/bin/activate  # On Windows use: env\Scripts\activate
```

#### Install Dependencies:
```bash
pip install -r requirements.txt
```

#### Sample `requirements.txt`:
```text
django==4.2
daphne==4.0
channels==4.0
channels-redis==4.1
redis==5.0
```

#### Install Redis:
Download Redis for Windows (e.g., from GitHub) or use WSL:
```bash
sudo apt install redis-server
```

#### Start Redis:
```bash
redis-server
```

#### Configure Environment:
Ensure `bidai/settings.py` has:
```python
INSTALLED_APPS = ['daphne', 'channels', 'marketplace', ...]
ASGI_APPLICATION = 'bidai.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {'hosts': [('127.0.0.1', 6379)]},
    },
}
```

#### Run Migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

#### Create Superuser:
```bash
python manage.py createsuperuser
```

#### Run the Server:
```bash
set DJANGO_SETTINGS_MODULE=bidai.settings
daphne -b 0.0.0.0 -p 8000 bidai.asgi:application
```

#### Access the App:
Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.
Login as a regular user or superuser to test features.

## Project Structure
```
bidai/
├── bidai/              # Project settings and ASGI config
│   ├── asgi.py
│   ├── settings.py
│   └── urls.py
├── marketplace/        # Main app
│   ├── migrations/
│   ├── templates/marketplace/
│   │   ├── admin_dashboard.html
│   │   ├── add_product.html
│   │   └── redeem_credits.html
│   ├── models.py      # Product, Wallet, Transaction models
│   ├── views.py       # Views for dashboard, product, credits
│   ├── forms.py       # ProductForm
│   ├── routing.py     # WebSocket routing
│   ├── consumers.py   # WebSocket consumers
│   └── urls.py
├── templates/          # Base template
│   └── base.html
├── static/             # Static files (if any)
├── manage.py
└── requirements.txt
```

## Usage
### Regular User:
- Login → Dashboard → "Add Product" (navbar) → Create a product.
- Redeem credits for your product at `/redeem-credits/<product_id>/`.

### Admin/Superuser:
- Login → "Admin Dashboard" (navbar) → View real-time metrics, charts, top sellers, and recent purchases.

### WebSocket Updates:
- Product views and wallet balance update live on dashboards.

## Contributing
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit changes (`git commit -m "Add feature"`).
4. Push to the branch (`git push origin feature-name`).
5. Open a Pull Request.

## Customization
- **Repository URL**: Replace `https://github.com/yourusername/bidai.git` with your actual repo.
- **Models**: Assumed `Product`, `Wallet`, `Transaction`—adjust if your models differ.
- **Max Credits**: Progress bar assumes 100; update if your max is different.

