import json
with open('last_good_feed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Type: {type(data).__name__}')
if isinstance(data, dict):
    print(f'Top-level keys: {list(data.keys())}')
    
    for key, value in data.items():
        if isinstance(value, list) and len(value) > 0:
            print(f'\n✅ Found list at key: "{key}" ({len(value)} items)')
            first = value[0]
            print('📋 Fields in fixture item:')
            for k in first.keys():
                print(f'  - {k}')
            print('\n📊 Sample values:')
            for k,v in list(first.items())[:12]:
                print(f'  {k}: {v}')
            break
