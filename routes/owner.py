from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from extensions import db
from models import Property, PropertyFeature, PropertyImage, ContactInquiry
from utils.data_mining import predict_price
from werkzeug.utils import secure_filename
import os

owner = Blueprint('owner', __name__, url_prefix='/owner')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def require_owner(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ('owner', 'admin'):
            flash('Access denied. Owner account required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@owner.route('/dashboard')
@login_required
@require_owner
def dashboard():
    props = Property.query.filter_by(owner_id=current_user.id).order_by(Property.created_at.desc()).all()
    inquiries = ContactInquiry.query.join(Property).filter(Property.owner_id == current_user.id).order_by(ContactInquiry.created_at.desc()).limit(10).all()
    stats = {
        'total': len(props),
        'active': sum(1 for p in props if p.is_active),
        'verified': sum(1 for p in props if p.is_verified),
        'total_inquiries': ContactInquiry.query.join(Property).filter(Property.owner_id == current_user.id).count(),
        'unread': ContactInquiry.query.join(Property).filter(Property.owner_id == current_user.id, ContactInquiry.is_read == False).count(),
    }
    return render_template('owner/dashboard.html', properties=props, inquiries=inquiries, stats=stats)

@owner.route('/property/add', methods=['GET', 'POST'])
@login_required
@require_owner
def add_property():
    if request.method == 'POST':
        f = request.form
        prop = Property(
            owner_id=current_user.id,
            title=f.get('title'), description=f.get('description'),
            location=f.get('location'), city=f.get('city'),
            price=float(f.get('price', 0)), bhk=int(f.get('bhk', 1)),
            property_type=f.get('property_type'), furnishing=f.get('furnishing'),
            area_sqft=float(f.get('area_sqft', 0)) if f.get('area_sqft') else None,
            latitude=float(f.get('latitude', 0)) if f.get('latitude') else None,
            longitude=float(f.get('longitude', 0)) if f.get('longitude') else None,
        )
        db.session.add(prop)
        db.session.flush()

        feat = PropertyFeature(
            property_id=prop.id,
            balcony='balcony' in f, parking='parking' in f, lift='lift' in f,
            security='security' in f, water_supply='water_supply' in f,
            gym='gym' in f, swimming_pool='swimming_pool' in f,
            wifi='wifi' in f, ac='ac' in f, power_backup='power_backup' in f,
            flooring=f.get('flooring'), ventilation=f.get('ventilation'),
            family_allowed='family_allowed' in f, bachelor_allowed='bachelor_allowed' in f,
            pets_allowed='pets_allowed' in f, veg_only='veg_only' in f,
        )
        db.session.add(feat)

        # Handle image uploads
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        images = request.files.getlist('images')
        captions = f.getlist('captions')
        for i, img_file in enumerate(images):
            if img_file and allowed_file(img_file.filename):
                filename = secure_filename(f"{prop.id}_{i}_{img_file.filename}")
                filepath = os.path.join(upload_folder, filename)
                img_file.save(filepath)
                cap = captions[i] if i < len(captions) else ''
                img_record = PropertyImage(property_id=prop.id,
                                          image_url=f'/static/images/{filename}', caption=cap)
                db.session.add(img_record)

        db.session.commit()
        flash('Property listed successfully!', 'success')
        return redirect(url_for('owner.dashboard'))

    # AI price suggestion
    all_props = Property.query.filter_by(is_active=True).all()
    training_data = [{'bhk': p.bhk, 'area_sqft': p.area_sqft or 0,
                      'furnishing': p.furnishing or 'unfurnished', 'price': p.price} for p in all_props]

    return render_template('owner/add_property.html', training_data=training_data)

@owner.route('/property/edit/<int:property_id>', methods=['GET', 'POST'])
@login_required
@require_owner
def edit_property(property_id):
    prop = Property.query.get_or_404(property_id)
    if prop.owner_id != current_user.id and current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('owner.dashboard'))
    if request.method == 'POST':
        f = request.form
        prop.title = f.get('title')
        prop.description = f.get('description')
        prop.location = f.get('location')
        prop.city = f.get('city')
        prop.price = float(f.get('price', 0))
        prop.bhk = int(f.get('bhk', 1))
        prop.property_type = f.get('property_type')
        prop.furnishing = f.get('furnishing')
        prop.area_sqft = float(f.get('area_sqft')) if f.get('area_sqft') else None
        if prop.features:
            feat = prop.features
            feat.balcony = 'balcony' in f
            feat.parking = 'parking' in f
            feat.lift = 'lift' in f
            feat.security = 'security' in f
            feat.water_supply = 'water_supply' in f
            feat.gym = 'gym' in f
            feat.ac = 'ac' in f
            feat.wifi = 'wifi' in f
            feat.power_backup = 'power_backup' in f
            feat.family_allowed = 'family_allowed' in f
            feat.bachelor_allowed = 'bachelor_allowed' in f
            feat.pets_allowed = 'pets_allowed' in f
            feat.veg_only = 'veg_only' in f
        db.session.commit()
        flash('Property updated!', 'success')
        return redirect(url_for('owner.dashboard'))
    return render_template('owner/edit_property.html', property=prop)

@owner.route('/property/delete/<int:property_id>', methods=['POST'])
@login_required
@require_owner
def delete_property(property_id):
    prop = Property.query.get_or_404(property_id)
    if prop.owner_id != current_user.id and current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('owner.dashboard'))
    prop.is_active = False
    db.session.commit()
    flash('Property removed.', 'info')
    return redirect(url_for('owner.dashboard'))

@owner.route('/inquiry/<int:inquiry_id>/read', methods=['POST'])
@login_required
@require_owner
def mark_read(inquiry_id):
    inquiry = ContactInquiry.query.get_or_404(inquiry_id)
    inquiry.is_read = True
    db.session.commit()
    return redirect(url_for('owner.dashboard'))
