import os
import re

base_path = r'c:\Users\nisharu deen\Downloads\PROJECT\factory_digital_twin\android\app\src\main\res\layout'

files = [
    'fragment_bottleneck.xml',
    'fragment_home.xml',
    'fragment_setup_review.xml',
    'fragment_simulate.xml',
    'fragment_step1_type.xml',
    'fragment_step2_machines.xml',
    'fragment_step3_specs.xml',
    'fragment_unity3d.xml'
]

for f in files:
    p = os.path.join(base_path, f)
    if not os.path.exists(p):
        print('MISSING:', p)
        continue
    with open(p, 'r', encoding='utf-8') as f_in:
        content = f_in.read()
    
    # Check if app namespace already exists
    if 'xmlns:app="http://schemas.android.com/apk/res-auto"' not in content:
        # insert after xmlns:android
        content = re.sub(
            r'(xmlns:android="http://schemas\.android\.com/apk/res/android")',
            r'\1\n    xmlns:app="http://schemas.android.com/apk/res-auto"',
            content,
            count=1
        )
    
    # replace android:selectedItemId with app:selectedItemId
    content = content.replace('android:selectedItemId=', 'app:selectedItemId=')
    
    with open(p, 'w', encoding='utf-8') as f_out:
        f_out.write(content)
        
print('Layouts updated!')
