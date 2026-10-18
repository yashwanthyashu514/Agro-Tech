import joblib, pandas as pd, numpy as np

CSV = r'd:\Agrotech\AgroTech_All_5_Modules\2_crop_recommendation\Crop_recommendation.csv'
df = pd.read_csv(CSV)
features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']

print('Training data crop distribution:')
print(df['label'].value_counts())
print()
print('Watermelon training sample stats:')
wm = df[df['label'] == 'watermelon']
print(wm[features].describe().round(1))
print()
print('All crop means (sorted by temperature):')
means = df.groupby('label')[features].mean().round(1)
print(means.sort_values('temperature'))
print()

# Davanagere-like: temp 24-30, humidity 60-75, rainfall 80-120
print('Crops in Davanagere-like conditions (temp 24-30, humidity 60-75, rainfall 80-120):')
cand = df[(df['temperature'].between(24,30)) & (df['humidity'].between(60,75)) & (df['rainfall'].between(80,120))]
print(cand['label'].value_counts())
