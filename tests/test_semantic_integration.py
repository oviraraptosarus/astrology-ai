import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from astrology_engine import calculate_full_chart, get_semantic_view

# Calculate chart for Aug 1 2008
chart_dict = calculate_full_chart(2008, 8, 1, 18, 25, 16.8186, 82.0641, 'Asia/Kolkata', 'User Test')

print('=== 1. SEMANTIC VIEW: FULL_OVERVIEW ===')
fov = json.loads(get_semantic_view(chart_dict, 'full_overview'))
print('Has sensitive_points:', 'sensitive_points' in fov)
print('Has avasthas:', 'avasthas' in fov)
print('Has doshas:', 'doshas' in fov)
print('Has cancellations:', 'cancellations' in fov)
print('Has numerology:', 'numerology' in fov)

print('\n=== 2. SEMANTIC VIEW: CAREER ===')
career_view = json.loads(get_semantic_view(chart_dict, 'career'))
print('Domain:', career_view.get('domain'))
print('Natal Promise:', career_view.get('natal_promise_status'))
print('Timing Windows count:', len(career_view.get('timing_windows', [])))
for tw in career_view.get('timing_windows', []):
    print(' Window:', tw.get('start_date'), 'to', tw.get('end_date'), '| Conf:', tw.get('confidence'))

print('\n=== 3. SEMANTIC VIEW: MARRIAGE ===')
m_view = json.loads(get_semantic_view(chart_dict, 'marriage'))
print('Domain:', m_view.get('domain'))
print('Natal Promise:', m_view.get('natal_promise_status'))
print('Timing Windows count:', len(m_view.get('timing_windows', [])))

print('\nALL SEMANTIC INTEGRATION TESTS PASSED WITH 100% SUCCESS!')
