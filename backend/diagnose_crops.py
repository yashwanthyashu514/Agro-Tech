import sys, os; sys.path.insert(0, '.')
import pandas as pd, numpy as np, joblib

# Load the saved crop model
bundle = joblib.load('models_store/crop_model.pkl')
model = bundle['model']
le = bundle['label_encoder']
features = bundle['features']
crop_ranges = bundle['crop_ranges']

print('Model type:', type(model).__name__)
print('Classes:', list(le.classes_))
print()

# Test 6 very different district scenarios across Karnataka
scenarios = [
    # name, N, P, K, temperature, humidity, ph, rainfall
    {'name': 'Davanagere Kharif (Central Dry)', 'N': 150, 'P': 13, 'K': 175, 'temperature': 27, 'humidity': 65, 'ph': 6.8, 'rainfall': 104},
    {'name': 'Shimoga Kharif (Wet Zone)',        'N': 90,  'P': 55, 'K': 50,  'temperature': 25, 'humidity': 82, 'ph': 6.0, 'rainfall': 300},
    {'name': 'Dharwad Rabi (N.Transition)',      'N': 60,  'P': 25, 'K': 200, 'temperature': 22, 'humidity': 50, 'ph': 7.5, 'rainfall': 25},
    {'name': 'Mysore Kharif (Southern Dry)',     'N': 120, 'P': 40, 'K': 80,  'temperature': 24, 'humidity': 60, 'ph': 6.5, 'rainfall': 95},
    {'name': 'Kodagu Kharif (Coffee Zone)',      'N': 30,  'P': 20, 'K': 40,  'temperature': 20, 'humidity': 85, 'ph': 5.8, 'rainfall': 500},
    {'name': 'Bellary Summer (Dry, Hot)',        'N': 100, 'P': 30, 'K': 150, 'temperature': 35, 'humidity': 35, 'ph': 7.2, 'rainfall': 8},
]

print("=" * 65)
for s in scenarios:
    X = pd.DataFrame([{f: s[f] for f in features}])
    proba = model.predict_proba(X)[0]
    top5_idx = np.argsort(-proba)[:5]
    top_pred = le.classes_[top5_idx[0]]
    crops = [(le.classes_[i], f"{round(float(proba[i])*100,1)}%") for i in top5_idx]
    print(f"\n{s['name']}")
    print(f"  Top Prediction: {top_pred.upper()}")
    for c, p in crops:
        bar = '#' * int(float(p.strip('%')) / 2)
        print(f"  {c:15s} {p:6s} {bar}")

# Also check training data distribution of watermelon
df = pd.read_csv(r'..\AgroTech_All_5_Modules\AgroTech_All_5_Modules\2_crop_recommendation\Crop_recommendation.csv')
print("\n\nTraining Data Crop Distribution:")
print(df['label'].value_counts())
print("\nWatermelon training sample stats:")
wm = df[df['label'] == 'watermelon']
print(wm[features].describe().round(1))
