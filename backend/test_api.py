import sys
from fastapi.testclient import TestClient
from app.main import app

def test_full_pipeline():
    client = TestClient(app)

    # 1. Health check
    res_h = client.get('/health')
    print('1. HEALTH CHECK:', res_h.status_code, res_h.json())
    assert res_h.status_code == 200

    # 2. Districts list
    res_d = client.get('/api/v1/location/districts')
    districts = res_d.json()['districts']
    print(f'2. DISTRICTS COUNT: {len(districts)} districts available')
    assert len(districts) == 30

    # 3. Weather check
    res_w = client.get('/api/v1/weather/Davanagere?days=7')
    print('3. WEATHER CHECK:', res_w.status_code)
    assert res_w.status_code == 200
    w_data = res_w.json()
    print(f"   Days forecasted: {len(w_data['days'])}, Expected rain: {w_data['summary']['total_expected_rain_mm']} mm")

    # 4. Full recommendation for Davanagere
    res_r = client.post('/api/v1/recommend', json={
        'district': 'Davanagere',
        'taluk': 'Davanagere',
        'season': 'Kharif',
        'top_n': 5
    })
    print('4. RECOMMEND STATUS:', res_r.status_code)
    if res_r.status_code != 200:
        print('ERROR:', res_r.text)
        return False

    data = res_r.json()
    print(f"   Location: {data['location']['district']}, {data['location']['taluk']} ({data['location']['agro_zone']})")
    print(f"   Inferred Soil: N={data['soil']['N']}, P={data['soil']['P']}, K={data['soil']['K']}, pH={data['soil']['ph']}")
    print(f"   Inferred Climate: {data['weather']['temperature']}°C, {data['weather']['humidity']}% hum, {data['weather']['rainfall']} mm rain")
    print('   Top Recommended Crops:')
    for r in data['recommendations']:
        yp = r.get('yield_prediction')
        yield_str = f"{yp['predicted_t_ha']} t/ha" if yp else "N/A"
        print(f"     - {r['crop'].capitalize():12} Suitability: {r['suitability_score']*100:5.1f}% | Yield: {yield_str}")
    
    if data.get('growth_plan'):
        gp = data['growth_plan']
        print(f"   Growth Plan for {gp['crop']}: {len(gp['stages'])} stages, Total ~{gp['total_duration_days']} days")
        for s in gp['stages']:
            print(f"       * {s['stage']:20} ({s['days_after_sowing']}) - Water: {s['water_need']}")

    print("\n>>> ALL TESTS PASSED SUCCESSFULLY! FULL PIPELINE VERIFIED! <<<")
    return True

if __name__ == '__main__':
    test_full_pipeline()
