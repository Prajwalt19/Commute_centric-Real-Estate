from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from extensions import db
from models import Property, TenantPreference, ContactInquiry
from utils.data_mining import predict_price

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/predict-price', methods=['POST'])
def predict_price_api():
    data = request.get_json()
    all_props = Property.query.filter_by(is_active=True).all()
    training_data = [{'bhk': p.bhk, 'area_sqft': p.area_sqft or 500,
                      'furnishing': p.furnishing or 'unfurnished', 'price': p.price} for p in all_props]
    result = predict_price(data, training_data)
    return jsonify(result)

@api.route('/save-preferences', methods=['POST'])
@login_required
def save_preferences():
    data = request.get_json()
    pref = current_user.preferences
    if not pref:
        pref = TenantPreference(user_id=current_user.id)
        db.session.add(pref)
    pref.preferred_city = data.get('city')
    pref.min_budget = data.get('min_budget')
    pref.max_budget = data.get('max_budget')
    pref.preferred_bhk = data.get('bhk')
    pref.preferred_type = data.get('property_type')
    pref.is_family = data.get('is_family', False)
    pref.has_pets = data.get('has_pets', False)
    pref.is_veg = data.get('is_veg', False)
    db.session.commit()
    return jsonify({'status': 'saved'})

@api.route('/contact', methods=['POST'])
@login_required
def contact_owner():
    data = request.get_json()
    inq = ContactInquiry(
        property_id=data.get('property_id'),
        tenant_id=current_user.id,
        message=data.get('message')
    )
    db.session.add(inq)
    db.session.commit()
    return jsonify({'status': 'sent'})

@api.route('/properties/search')
def search_properties():
    city = request.args.get('city', '')
    props = Property.query.filter_by(is_active=True)
    if city:
        props = props.filter(Property.city.ilike(f'%{city}%'))
    results = [{'id': p.id, 'title': p.title, 'city': p.city,
                'price': p.price, 'bhk': p.bhk} for p in props.limit(20).all()]
    return jsonify(results)
