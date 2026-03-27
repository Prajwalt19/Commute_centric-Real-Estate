# NestFind — Smart Rental Property Search Platform

A full-stack web app built with Flask, SQLAlchemy, and Data Mining (scikit-learn) for intelligent rental property search and recommendations.

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Seed the database (demo data)
```bash
python seed_data.py
```

### 3. Run the app
```bash
python app.py
```

Visit: http://localhost:5000

---

## 🔑 Demo Login Credentials

| Role   | Email                   | Password   |
|--------|-------------------------|------------|
| Admin  | admin@nestfind.com      | admin123   |
| Owner  | owner@nestfind.com      | owner123   |
| Tenant | tenant@nestfind.com     | tenant123  |

---

## 🗂️ Project Structure

```
rental_platform/
├── app.py                   # Flask app factory
├── config.py                # Configuration (DB, uploads, etc.)
├── requirements.txt         # Python dependencies
├── seed_data.py             # Demo data seeder
├── models/
│   └── __init__.py          # All SQLAlchemy models
├── routes/
│   ├── auth.py              # Login, Register, Logout
│   ├── main.py              # Home, Search, Property Detail, Wishlist
│   ├── owner.py             # Owner Dashboard, Add/Edit Property
│   ├── admin.py             # Admin Dashboard, Users, Properties, Analytics
│   └── api.py               # REST API endpoints
├── utils/
│   └── data_mining.py       # All AI/ML features
├── templates/
│   ├── base.html            # Base layout with nav & footer
│   ├── auth/                # Login, Register
│   ├── main/                # Home, Search, Detail, Wishlist
│   ├── owner/               # Owner Dashboard, Add/Edit Property
│   └── admin/               # Admin Dashboard, Properties, Users, Analytics
└── static/
    ├── css/main.css         # Complete design system
    ├── js/main.js           # Frontend interactions
    └── images/              # Uploaded property photos
```

---

## 🤖 Data Mining Features

### 1. Recommendation System
- **Content-Based Filtering** (`get_content_based_recommendations`): Uses cosine similarity on property features (price, BHK, area, amenities) to find similar properties on the Property Detail page.
- **Preference-Based Filtering** (`get_preference_based_recommendations`): Scores properties against saved tenant preferences (city, budget, BHK, type) to show personalized results on the Search page.

### 2. Price Prediction
- **Random Forest Regressor** (`predict_price`): Trained on existing property prices. Predicts fair rental price based on BHK, area, and furnishing. Used in the Owner Add Property form with the **AI Price Predictor** button.

### 3. User Clustering
- **K-Means Clustering** (`cluster_users`): Groups tenants into segments (Budget Seekers, Mid-Range Families, Premium Tenants, Luxury Seekers) based on their budget and BHK preferences. Visualized in the Admin Dashboard.

### 4. Association Rules
- **Apriori-Style Mining** (`find_association_rules`): Discovers patterns in wishlist behavior — "users who saved Property A also saved Property B". Displayed in Admin Dashboard and used for cross-property recommendations.

---

## 🏗️ Tech Stack

| Layer        | Technology              |
|--------------|-------------------------|
| Frontend     | HTML5, CSS3, JavaScript  |
| Backend      | Python 3.10+, Flask 3.0  |
| Database     | SQLite (dev) / MySQL (prod) |
| ORM          | SQLAlchemy + Flask-SQLAlchemy |
| Auth         | Flask-Login + Bcrypt     |
| Data Mining  | pandas, scikit-learn, numpy |
| Charts       | Chart.js (admin panel)   |

---

## 🔌 API Endpoints

| Method | Endpoint                        | Description                  |
|--------|---------------------------------|------------------------------|
| POST   | /api/predict-price              | AI price prediction          |
| POST   | /api/save-preferences           | Save tenant preferences      |
| POST   | /api/contact                    | Send inquiry to owner        |
| GET    | /api/properties/search          | Search properties (JSON)     |
| POST   | /wishlist/toggle/<id>           | Add/remove from wishlist     |
| POST   | /review/<id>                    | Submit property review       |

---

## ⚙️ Production Deployment

1. Set environment variables:
   ```
   SECRET_KEY=your-secret-key
   DATABASE_URL=mysql://user:pass@host/dbname
   ```
2. Use `gunicorn app:create_app()` for production
3. Configure a web server (nginx) as reverse proxy
4. Set up static file serving via nginx

---

## 📸 Features Overview

- **Home**: Hero search, featured properties, AI features showcase
- **Search**: Advanced filters (city, price, BHK, type, amenities), AI recommendations panel
- **Property Detail**: Gallery, amenities, tenant preferences, similar properties (AI), reviews, contact owner
- **Owner Dashboard**: Stats, property management, inquiry inbox
- **Add Property**: Full form with AI price predictor tool
- **Admin Dashboard**: Platform stats, pending verifications, K-Means clusters, association rules
- **Admin Analytics**: Chart.js visualizations for price distribution, BHK mix, top cities
- **Wishlist**: Saved properties management
