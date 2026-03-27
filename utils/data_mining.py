"""
Data Mining Module
- Recommendation System (Content-based + Preference filtering)
- Price Prediction (Random Forest)
- User Clustering (K-Means)
- Association Rules (Apriori-style)
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestRegressor
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')


def get_content_based_recommendations(property_id, all_properties, top_n=5):
    if not all_properties or len(all_properties) < 2:
        return []
    df = pd.DataFrame([{
        'id': p['id'], 'price': p['price'], 'bhk': p['bhk'],
        'area_sqft': p.get('area_sqft', 0) or 0,
        'balcony': int(p.get('balcony', 0)), 'parking': int(p.get('parking', 0)),
        'gym': int(p.get('gym', 0)), 'wifi': int(p.get('wifi', 0)),
        'ac': int(p.get('ac', 0)), 'lift': int(p.get('lift', 0)),
    } for p in all_properties])
    feature_cols = ['price', 'bhk', 'area_sqft', 'balcony', 'parking', 'gym', 'wifi', 'ac', 'lift']
    scaler = StandardScaler()
    X = scaler.fit_transform(df[feature_cols].fillna(0))
    similarity = cosine_similarity(X)
    prop_ids = df['id'].tolist()
    if property_id not in prop_ids:
        return []
    idx = prop_ids.index(property_id)
    sim_scores = sorted(enumerate(similarity[idx]), key=lambda x: x[1], reverse=True)
    sim_scores = [s for s in sim_scores if prop_ids[s[0]] != property_id][:top_n]
    return [prop_ids[i[0]] for i in sim_scores]


def get_preference_based_recommendations(user_prefs, all_properties, top_n=6):
    if not all_properties:
        return []
    scored = []
    for p in all_properties:
        score = 0
        if user_prefs.get('city') and user_prefs['city'].lower() in p.get('city', '').lower():
            score += 30
        price = p.get('price', 0)
        min_b = user_prefs.get('min_budget', 0) or 0
        max_b = user_prefs.get('max_budget', float('inf')) or float('inf')
        if min_b <= price <= max_b:
            score += 25
        if user_prefs.get('bhk') and str(user_prefs['bhk']) == str(p.get('bhk')):
            score += 20
        if user_prefs.get('property_type') and user_prefs['property_type'] == p.get('property_type'):
            score += 15
        if user_prefs.get('is_family') and p.get('family_allowed'):
            score += 5
        if user_prefs.get('has_pets') and p.get('pets_allowed'):
            score += 5
        scored.append((p['id'], score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [pid for pid, _ in scored[:top_n]]


def predict_price(features, training_data):
    if len(training_data) < 5:
        base = 5000
        bhk_mult = features.get('bhk', 1) * 3000
        area_mult = (features.get('area_sqft', 500) / 100) * 500
        furnishing_bonus = {'furnished': 5000, 'semi': 2500, 'unfurnished': 0}.get(features.get('furnishing', 'unfurnished'), 0)
        predicted = base + bhk_mult + area_mult + furnishing_bonus
        return {'predicted_price': round(predicted, -2), 'range_low': round(predicted * 0.85, -2),
                'range_high': round(predicted * 1.15, -2), 'confidence': 'low', 'method': 'heuristic'}
    df = pd.DataFrame(training_data)
    df['furnishing_enc'] = df['furnishing'].map({'furnished': 2, 'semi': 1, 'unfurnished': 0}).fillna(0)
    df['area_sqft'] = df['area_sqft'].fillna(df['area_sqft'].median())
    X = df[['bhk', 'area_sqft', 'furnishing_enc']].fillna(0)
    y = df['price']
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, y)
    input_df = pd.DataFrame([{
        'bhk': features.get('bhk', 1),
        'area_sqft': features.get('area_sqft', 500),
        'furnishing_enc': {'furnished': 2, 'semi': 1, 'unfurnished': 0}.get(features.get('furnishing', 'unfurnished'), 0),
    }])
    predicted = model.predict(input_df)[0]
    return {
        'predicted_price': round(predicted, -2),
        'range_low': round(predicted * 0.85, -2),
        'range_high': round(predicted * 1.15, -2),
        'confidence': 'high' if len(training_data) > 20 else 'medium',
        'method': 'random_forest'
    }


def cluster_users(users_data, n_clusters=4):
    if len(users_data) < n_clusters:
        return [{'user_id': u['id'], 'cluster': 0, 'cluster_label': 'General'} for u in users_data]
    df = pd.DataFrame(users_data)
    feature_cols = ['min_budget', 'max_budget', 'preferred_bhk']
    df[feature_cols] = df[feature_cols].fillna(df[feature_cols].median())
    scaler = StandardScaler()
    X = scaler.fit_transform(df[feature_cols])
    kmeans = KMeans(n_clusters=min(n_clusters, len(users_data)), random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X)
    cluster_labels = {0: 'Budget Seekers', 1: 'Mid-Range Families', 2: 'Premium Tenants', 3: 'Luxury Seekers'}
    return [{'user_id': u['id'], 'cluster': int(clusters[i]),
             'cluster_label': cluster_labels.get(int(clusters[i]), f'Group {clusters[i]+1}')}
            for i, u in enumerate(users_data)]


def find_association_rules(wishlists, min_support=0.1):
    if not wishlists or len(wishlists) < 3:
        return []
    user_items = defaultdict(set)
    for w in wishlists:
        user_items[w['user_id']].add(w['property_id'])
    transactions = list(user_items.values())
    n = len(transactions)
    item_counts = defaultdict(int)
    pair_counts = defaultdict(int)
    for t in transactions:
        items = list(t)
        for item in items:
            item_counts[item] += 1
        for i in range(len(items)):
            for j in range(i+1, len(items)):
                pair_counts[tuple(sorted([items[i], items[j]]))] += 1
    rules = []
    for (a, b), count in pair_counts.items():
        support = count / n
        if support >= min_support:
            conf_ab = count / item_counts[a] if item_counts[a] > 0 else 0
            conf_ba = count / item_counts[b] if item_counts[b] > 0 else 0
            if conf_ab >= 0.3:
                rules.append({'if': a, 'then': b, 'confidence': round(conf_ab, 2), 'support': round(support, 2)})
            if conf_ba >= 0.3:
                rules.append({'if': b, 'then': a, 'confidence': round(conf_ba, 2), 'support': round(support, 2)})
    rules.sort(key=lambda x: x['confidence'], reverse=True)
    return rules[:20]


def get_association_recommendations(property_id, rules, top_n=3):
    return [r['then'] for r in rules if r['if'] == property_id][:top_n]
