"""
Seed the database with sample data for demo purposes.
Run: python seed_data.py
"""
from app import create_app
from extensions import db
from models import User, Property, PropertyFeature, PropertyImage, TenantPreference, Review, Wishlist
from werkzeug.security import generate_password_hash
from datetime import date, datetime

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # Create users
    admin = User(name='Admin User', email='admin@nestfind.com',
                 password=generate_password_hash('admin123'), role='admin')
    owner1 = User(name='Rajesh Sharma', email='owner@nestfind.com',
                  password=generate_password_hash('owner123'), role='owner')
    owner2 = User(name='Priya Patel', email='priya@nestfind.com',
                  password=generate_password_hash('owner123'), role='owner')
    tenant1 = User(name='Amit Kumar', email='tenant@nestfind.com',
                   password=generate_password_hash('tenant123'), role='tenant')
    tenant2 = User(name='Sneha Rao', email='sneha@nestfind.com',
                   password=generate_password_hash('tenant123'), role='tenant')

    db.session.add_all([admin, owner1, owner2, tenant1, tenant2])
    db.session.flush()

    # Tenant preferences
    pref1 = TenantPreference(user_id=tenant1.id, preferred_city='Pune', min_budget=8000,
                              max_budget=18000, preferred_bhk='2', preferred_type='apartment', is_family=False)
    pref2 = TenantPreference(user_id=tenant2.id, preferred_city='Mumbai', min_budget=15000,
                              max_budget=35000, preferred_bhk='3', preferred_type='apartment', is_family=True)
    db.session.add_all([pref1, pref2])

    # Sample properties
    properties_data = [
        dict(title='Spacious 2BHK in Koregaon Park', city='Pune', location='Koregaon Park, Pune',
             price=16000, bhk=2, property_type='apartment', furnishing='furnished',
             area_sqft=950, description='Beautiful 2BHK apartment in prime Koregaon Park with modern amenities, great views and excellent connectivity.',
             is_verified=True, latitude=18.5362, longitude=73.8929,
             features=dict(balcony=True, parking=True, lift=True, security=True, water_supply=True,
                           gym=False, wifi=True, ac=True, power_backup=True, family_allowed=True, bachelor_allowed=True)),
        dict(title='Cozy 1BHK near IT Park', city='Pune', location='Magarpatta, Pune',
             price=9500, bhk=1, property_type='apartment', furnishing='semi',
             area_sqft=580, description='Ideal for IT professionals. Walking distance to Magarpatta IT Park with all basic amenities.',
             is_verified=True, latitude=18.5074, longitude=73.9282,
             features=dict(balcony=True, parking=False, lift=True, security=True, water_supply=True,
                           wifi=True, ac=False, power_backup=False, family_allowed=False, bachelor_allowed=True)),
        dict(title='Luxury 3BHK Sea View Flat', city='Mumbai', location='Bandra West, Mumbai',
             price=55000, bhk=3, property_type='apartment', furnishing='furnished',
             area_sqft=1450, description='Premium 3BHK with stunning sea views, modular kitchen, and premium fixtures in the heart of Bandra.',
             is_verified=True, latitude=19.0596, longitude=72.8295,
             features=dict(balcony=True, parking=True, lift=True, security=True, water_supply=True,
                           gym=True, swimming_pool=True, wifi=True, ac=True, power_backup=True,
                           family_allowed=True, bachelor_allowed=False)),
        dict(title='Affordable PG near Metro', city='Bangalore', location='Indiranagar, Bangalore',
             price=7000, bhk=1, property_type='pg', furnishing='furnished',
             area_sqft=220, description='Fully furnished PG accommodation with food, WiFi and laundry. Close to metro station.',
             is_verified=True, latitude=12.9784, longitude=77.6408,
             features=dict(balcony=False, parking=False, lift=False, security=True, water_supply=True,
                           wifi=True, ac=True, power_backup=True, family_allowed=False, bachelor_allowed=True, veg_only=True)),
        dict(title='Modern 2BHK in Whitefield', city='Bangalore', location='Whitefield, Bangalore',
             price=22000, bhk=2, property_type='apartment', furnishing='furnished',
             area_sqft=1100, description='Gated community 2BHK with world class amenities in the tech hub of Whitefield.',
             is_verified=False, latitude=12.9698, longitude=77.7499,
             features=dict(balcony=True, parking=True, lift=True, security=True, water_supply=True,
                           gym=True, swimming_pool=True, wifi=True, ac=True, power_backup=True,
                           family_allowed=True, bachelor_allowed=True, pets_allowed=True)),
        dict(title='Heritage Villa in Jubilee Hills', city='Hyderabad', location='Jubilee Hills, Hyderabad',
             price=45000, bhk=4, property_type='villa', furnishing='furnished',
             area_sqft=2800, description='Majestic independent villa with garden, garage, servant quarters and premium interiors in prestigious Jubilee Hills.',
             is_verified=True, latitude=17.4310, longitude=78.4102,
             features=dict(balcony=True, parking=True, lift=False, security=True, water_supply=True,
                           gym=False, swimming_pool=True, wifi=True, ac=True, power_backup=True,
                           family_allowed=True, bachelor_allowed=False, pets_allowed=True)),
    ]

    created_props = []
    for i, pd in enumerate(properties_data):
        feats = pd.pop('features')
        owner = owner1 if i % 2 == 0 else owner2
        prop = Property(owner_id=owner.id, **pd)
        db.session.add(prop)
        db.session.flush()
        feat = PropertyFeature(property_id=prop.id, **feats)
        db.session.add(feat)
        created_props.append(prop)

    # Sample reviews
    r1 = Review(user_id=tenant1.id, property_id=created_props[0].id, rating=5, comment='Excellent apartment! Very clean and well maintained.')
    r2 = Review(user_id=tenant2.id, property_id=created_props[0].id, rating=4, comment='Good location and facilities. Owner is very cooperative.')
    r3 = Review(user_id=tenant1.id, property_id=created_props[2].id, rating=5, comment='Stunning views! Worth every penny.')
    db.session.add_all([r1, r2, r3])

    # Sample wishlists
    w1 = Wishlist(user_id=tenant1.id, property_id=created_props[0].id)
    w2 = Wishlist(user_id=tenant1.id, property_id=created_props[1].id)
    w3 = Wishlist(user_id=tenant2.id, property_id=created_props[2].id)
    w4 = Wishlist(user_id=tenant2.id, property_id=created_props[4].id)
    db.session.add_all([w1, w2, w3, w4])

    db.session.commit()
    print("\n✅ Database seeded successfully!")
    print("\n--- Login Credentials ---")
    print("Admin:  admin@nestfind.com  / admin123")
    print("Owner:  owner@nestfind.com  / owner123")
    print("Tenant: tenant@nestfind.com / tenant123")
