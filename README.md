# Django Marketplace

A modern, full-featured marketplace web application built with Django.
Users can post listings, browse categories, save ads, leave reviews, and manage seller profiles.
The project is production-ready and easily customizable for any country or niche.

---

## 🚀 Features

### 👤 Authentication & Accounts
- User registration and login
- Email-based authentication
- Password reset
- User profile page (My Account)

### 🏷 Listings
- Create, edit, delete listings
- Multiple images per listing
- Categories and subcategories
- Price, condition, listing type
- Optional labels (e.g. Featured, Urgent)
- Saved (bookmarked) listings

### 📍 Location Support
Each listing supports detailed location data:
- Province
- City
- Location (neighborhood / area)
- Postal code

Listings can be filtered and displayed by location.
The system is fully adaptable for any country.

### 🧭 Nearby Listings (Optional)
- Location-based listings using browser geolocation
- City / province detection
- Optional radius filtering
- Separate `/nearby/` page

### 👥 Seller Profiles
- Public seller profile page
- Seller bio and avatar
- Seller type:
  - Individual
  - Store
  - Business
- Seller listings overview

### ⭐ Reviews & Ratings
- Buyers can leave ratings and reviews
- One review per user (updates overwrite previous)
- Automatic average rating calculation
- Rating badges displayed on listings and profiles

### 🔐 Privacy Controls
Each user can control visibility of personal contact information:
- Email
- Phone number

If enabled, contact details are hidden from public profiles.

---

## 🧱 Tech Stack

- Python 3.12
- Django 5
- SQLite (default, easily replaceable with PostgreSQL)
- Bootstrap 5
- Django Allauth
- Gunicorn (production)

---

## 📂 Project Structure

django-marketplace/
│
├── board/ # Main app (listings, profiles, reviews)
├── templates/ # HTML templates
├── static/ # Static assets
├── media/ # Uploaded images
├── build.sh # Render deployment script
├── requirements.txt
├── manage.py
└── README.md


---

## ⚙️ Customization Guide

### 📍 Locations (Provinces, Cities, Postal Codes)

Location fields are defined in:

board/models.py → Listing model


You can easily:
- Rename "Province" to "State", "Region", etc.
- Replace province choices with your own
- Remove postal code if not needed
- Adapt the marketplace for any country

### 🏪 Seller Types

Seller types are configurable via choices:

- Individual
- Store
- Business

Defined in:
board/models.py → UserProfile.seller_type



Used across:
- Seller profile page
- Listing cards
- Seller badges

### 🔐 Privacy Settings

Users can hide personal information using:
UserProfile.hide_personal_info

When enabled:
- Email and phone are hidden on public seller profiles
- Buyers see a “Contact info is hidden” notice

---

## 🛠 Installation (Local Development)

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/django-marketplace.git
cd django-marketplace
2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
4. Environment variables


Create .env file based on example:
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_password
DEFAULT_FROM_EMAIL=support@yourmarketplace.com

5. Run migrations and server
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
☁️ Deployment (Render.com)
This project is production-ready and includes a build script.

build.sh
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
Render Settings
Build Command: bash build.sh

Start Command:
gunicorn project_name.wsgi:application

Python Version: 3.12

Environment Variables (Render)
DEBUG=False
SECRET_KEY=production-secret-key
ALLOWED_HOSTS=yourapp.onrender.com
📌 Notes
SQLite is used by default for simplicity

PostgreSQL can be enabled by changing DATABASE_URL

Static files are collected automatically

Media uploads are supported

📜 License
This project is provided as a marketplace template.
You are free to customize, extend, and use it in commercial projects.