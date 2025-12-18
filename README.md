# 🛒 Django Marketplace Template — Full Featured Classifieds Platform  
Modern, fast, and mobile-first marketplace built with **Django 5**.

This template includes everything needed to launch a classified ads marketplace, listing platform, or online directory. Perfect for developers, agencies, or buyers who want a ready-to-use base with clean UI and extendable architecture.

---

## ✨ Features

### 🏷 Listings & Categories
- Main categories + unlimited subcategories
- Modern listing cards with images, labels (New / Top), price, rating
- Full listing page with:
  - Image gallery
  - Phone, location, seller info
  - Description
  - Comments
  - Similar listings

### 👤 User Accounts
- Login, register, logout
- **Google Sign-In** (`django-allauth` ready)
- User profile with:
  - Avatar
  - Rating
  - Seller type (Seller / Store / Business)
  - Date joined
  - Saved listings
  - User’s ads

### 📱 Responsive UI
- Fully mobile friendly
- Bottom navigation bar (mobile only)
- Sidebar mobile menu
- Clean and consistent style (Bootstrap 5 + custom UI)

### 🛠 Admin Features
- Manage listings, images, categories, and users
- Works out of the box — no configuration needed

---

### 💾 Fixtures (Demo Data)
Ready-made category sets are included:

- `categories_basic.json`
- `categories_full.json`

The data loading step is **included** in the installation guide below.

---

## 🚀 Installation (Local Setup)

Follow these steps to run the project locally and see the demo content exactly as shown in the screenshots.

```bash
# Clone the repository
git clone <your-repo-url>
cd marketplace

# 1. Create and Activate Virtual Environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Apply Migrations (Create Database Tables)
python manage.py migrate

# 4. LOAD DEMO DATA
# This command loads categories and listings to make the site look like the demo:
python manage.py loaddata fixtures/categories_full.json

# 5. Create Superuser (Admin Account)
python manage.py createsuperuser

# 6. Run Server
python manage.py runserver

Access Points:

Frontend: http://127.0.0.1:8000/

Admin Panel: http://127.0.0.1:8000/admin/

🗂 Project Structure
board_project/
│
├── board/                # Main app (Listings, Models, Views)
│   ├── models.py         # Listing, Image, Category, Comments
│   ├── views.py
│   ├── urls.py
│   ├── templates/board/  # All pages (home, categories, listing, account)
│   └── forms.py
│
├── media/                # Uploaded images
├── static/               # UI assets
├── fixtures/             # Demo data (JSON)
├── templates/            # Global templates (login/register)
└── requirements.txt
📸 Screenshots
All demo screenshots included in /demo_screens/.

Recommended set: home_page.png category_page.png listing_detail.png my_account.png post_ad.png admin_panel.png mobile_view.png mobile_menu.png

🧑‍💻 Tech Stack
Django 5

django-allauth

Pillow

Bootstrap 5

SQLite (default, easily switchable to PostgreSQL/MySQL)

📦 Deployment Ready (Production Configuration)
The project is designed for immediate production deployment and is compatible with:

Render.com

Railway.app

Heroku

DigitalOcean

Any VPS

Environment variables are already separated, requiring minimal modification for production launch (DEBUG=False and SECRET_KEY must be set via environment variables).

📋 License
This is a template. You may resell it, use it for commercial projects, or build products on top.