from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
from extensions import db
from models import Property, PropertyFeature, PropertyImage, Wishlist, Review, TenantPreference
from utils.data_mining import get_content_based_recommendations, get_preference_based_recommendations, get_association_recommendations, find_association_rules
from sqlalchemy import or_, and_

main = Blueprint('main', __name__)

def property_to_dict(p):
    feat = p.features
    images = p.images
    avg_rating = sum(r.rating for r in p.reviews) / len(p.reviews) if p.reviews else 0
    return {
        'id': p.id, 'title': p.title, 'description': p.description,
        'location': p.location, 'city': p.city, 'price': p.price,
        'bhk': p.bhk, 'property_type': p.property_type, 'furnishing': p.furnishing,
        'area_sqft': p.area_sqft, 'is_verified': p.is_verified,
        'created_at': p.created_at.strftime('%Y-%m-%d') if p.created_at else '',
        'avg_rating': round(avg_rating, 1), 'review_count': len(p.reviews),
        'balcony': feat.balcony if feat else False,
        'parking': feat.parking if feat else False,
        'gym': feat.gym if feat else False,
        'wifi': feat.wifi if feat else False,
        'ac': feat.ac if feat else False,
        'lift': feat.lift if feat else False,
        'security': feat.security if feat else False,
        'water_supply': feat.water_supply if feat else False,
        'swimming_pool': feat.swimming_pool if feat else False,
        'power_backup': feat.power_backup if feat else False,
        'family_allowed': feat.family_allowed if feat else True,
        'bachelor_allowed': feat.bachelor_allowed if feat else True,
        'pets_allowed': feat.pets_allowed if feat else False,
        'veg_only': feat.veg_only if feat else False,
        'flooring': feat.flooring if feat else '',
        'ventilation': feat.ventilation if feat else '',
        'images': [{'url': img.image_url, 'caption': img.caption} for img in images],
        'owner_name': p.owner.name if p.owner else 'Unknown',
    }

@main.route('/')
def index():
    featured = Property.query.filter_by(is_active=True, is_verified=True).order_by(Property.created_at.desc()).limit(6).all()
    cities = db.session.query(Property.city).distinct().all()
    cities = [c[0] for c in cities]
    featured_data = [property_to_dict(p) for p in featured]
    return render_template('main/index.html', featured=featured_data, cities=cities)

@main.route('/search')
def search():
    city = request.args.get('city', '')
    min_price = request.args.get('min_price', 0, type=float)
    max_price = request.args.get('max_price', 999999, type=float)
    bhk = request.args.get('bhk', '')
    property_type = request.args.get('property_type', '')
    furnishing = request.args.get('furnishing', '')
    amenities = request.args.getlist('amenities')
    sort_by = request.args.get('sort_by', 'newest')

    query = Property.query.filter_by(is_active=True)
    if city:
        query = query.filter(Property.city.ilike(f'%{city}%'))
    query = query.filter(Property.price >= min_price, Property.price <= max_price)
    if bhk:
        query = query.filter(Property.bhk == int(bhk))
    if property_type:
        query = query.filter(Property.property_type == property_type)
    if furnishing:
        query = query.filter(Property.furnishing == furnishing)

    if sort_by == 'price_asc':
        query = query.order_by(Property.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Property.price.desc())
    else:
        query = query.order_by(Property.created_at.desc())

    properties = query.all()

    # Filter by amenities
    if amenities:
        filtered = []
        for p in properties:
            feat = p.features
            if feat:
                match = all(getattr(feat, a, False) for a in amenities)
                if match:
                    filtered.append(p)
        properties = filtered

    props_data = [property_to_dict(p) for p in properties]

    # AI Recommendations
    recommendations = []
    if current_user.is_authenticated and current_user.preferences:
        pref = current_user.preferences
        user_prefs = {
            'city': pref.preferred_city, 'min_budget': pref.min_budget,
            'max_budget': pref.max_budget, 'bhk': pref.preferred_bhk,
            'property_type': pref.preferred_type, 'is_family': pref.is_family,
            'has_pets': pref.has_pets
        }
        rec_ids = get_preference_based_recommendations(user_prefs, props_data)
        recommendations = [p for p in props_data if p['id'] in rec_ids][:4]

    cities = db.session.query(Property.city).distinct().all()
    cities = [c[0] for c in cities]

    return render_template('main/search.html',
                           properties=props_data,
                           recommendations=recommendations,
                           cities=cities,
                           filters=request.args)

@main.route('/property/<int:property_id>')
def property_detail(property_id):
    prop = Property.query.get_or_404(property_id)
    prop_data = property_to_dict(prop)

    # Similar properties via content-based filtering
    all_props = [property_to_dict(p) for p in Property.query.filter_by(is_active=True).all()]
    similar_ids = get_content_based_recommendations(property_id, all_props, top_n=4)
    similar_props = [p for p in all_props if p['id'] in similar_ids]

    # Wishlist check
    in_wishlist = False
    if current_user.is_authenticated:
        in_wishlist = bool(Wishlist.query.filter_by(user_id=current_user.id, property_id=property_id).first())

    reviews = Review.query.filter_by(property_id=property_id).order_by(Review.created_at.desc()).all()
    reviews_data = [{'user_name': r.user.name, 'rating': r.rating, 'comment': r.comment,
                     'date': r.created_at.strftime('%b %Y')} for r in reviews]

    return render_template('main/property_detail.html',
                           property=prop_data,
                           similar=similar_props,
                           reviews=reviews_data,
                           in_wishlist=in_wishlist)

@main.route('/wishlist/toggle/<int:property_id>', methods=['POST'])
@login_required
def toggle_wishlist(property_id):
    existing = Wishlist.query.filter_by(user_id=current_user.id, property_id=property_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'status': 'removed'})
    else:
        w = Wishlist(user_id=current_user.id, property_id=property_id)
        db.session.add(w)
        db.session.commit()
        return jsonify({'status': 'added'})

@main.route('/wishlist')
@login_required
def wishlist():
    items = Wishlist.query.filter_by(user_id=current_user.id).all()
    props = [property_to_dict(Wishlist.query.get(w.id).property) for w in items]
    return render_template('main/wishlist.html', properties=props)

@main.route('/review/<int:property_id>', methods=['POST'])
@login_required
def add_review(property_id):
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment')
    existing = Review.query.filter_by(user_id=current_user.id, property_id=property_id).first()
    if existing:
        existing.rating = rating
        existing.comment = comment
    else:
        review = Review(user_id=current_user.id, property_id=property_id, rating=rating, comment=comment)
        db.session.add(review)
    db.session.commit()
    flash('Review submitted!', 'success')
    return redirect(url_for('main.property_detail', property_id=property_id))
