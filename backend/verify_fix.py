"""
Verify the hybrid scoring engine gives sensible district-specific results.
"""
import sys; sys.path.insert(0, '.')
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

test_cases = [
    {"district": "Davanagere", "taluk": "Davanagere", "season": "Kharif",  "desc": "Central Dry Zone - Kharif"},
    {"district": "Davanagere", "taluk": "Davanagere", "season": "Rabi",    "desc": "Central Dry Zone - Rabi"},
    {"district": "Davanagere", "taluk": "Davanagere", "season": "Summer",  "desc": "Central Dry Zone - Summer"},
    {"district": "Shimoga",    "taluk": "Shimoga",    "season": "Kharif",  "desc": "Wet Zone (High Rainfall) - Kharif"},
    {"district": "Dharwad",    "taluk": "Dharwad",    "season": "Rabi",    "desc": "Northern Transition - Rabi"},
    {"district": "Mysore",     "taluk": "Mysore",     "season": "Kharif",  "desc": "Southern Dry Zone - Kharif"},
    {"district": "Kodagu",     "taluk": "Madikeri",   "season": "Kharif",  "desc": "Malnad/Coffee Zone - Kharif"},
    {"district": "Bellary",    "taluk": "Bellary",    "season": "Kharif",  "desc": "Arid/Semi-arid - Kharif"},
]

print("=" * 70)
print("HYBRID AGRONOMIC RANKING VERIFICATION TEST")
print("=" * 70)

for tc in test_cases:
    res = client.post('/api/v1/recommend', json={
        'district': tc['district'],
        'taluk':    tc['taluk'],
        'season':   tc['season'],
        'top_n':    5
    })

    print(f"\n{tc['desc']} ({tc['district']}, {tc['season']})")
    if res.status_code == 200:
        data = res.json()
        w = data['weather']
        print(f"  Climate: {w['temperature']} C | {w['humidity']}% hum | {w['rainfall']} mm rain")
        print("  Recommendations:")
        for r in data['recommendations']:
            yp = r.get('yield_prediction')
            yield_str = f"{yp['predicted_t_ha']} t/ha" if yp else "no hist data"
            flag = "[*]" if r['rank'] <= 3 else "   "
            print(f"  {flag} #{r['rank']} {r['crop']:15s} {r['suitability_pct']:5.1f}%  |  Season: {r['season']:20s}  |  Yield: {yield_str}")
    else:
        print(f"  ERROR {res.status_code}: {res.text[:200]}")

print("\n" + "="*70)
print("WATERMELON CHECK (should only appear in Summer season):")
# specifically check if watermelon comes up in Kharif - it should NOT be #1
kharif = next(r for r in client.post('/api/v1/recommend', json={
    'district': 'Davanagere', 'season': 'Kharif', 'top_n': 10}).json()['recommendations'])
print(f"  Davanagere Kharif #1 recommendation: {kharif['crop'].upper()} ({kharif['suitability_pct']}%)")
assert kharif['crop'] != 'watermelon', "FAIL: watermelon is still #1 in Kharif!"
print("  PASS: watermelon is no longer incorrectly dominating Kharif season")
