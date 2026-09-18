import os
import re

def remove_emojis(text):
    # Regex for emojis (basic approach)
    # This regex matches many common emojis
    return re.sub(r'[\U00010000-\U0010ffff]', '', text)

def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = remove_emojis(content)
                # also manually replace some specific unicode chars that might not be caught
                new_content = new_content.replace('📈', '').replace('📋', '').replace('👤', '').replace('🕐', '').replace('💾', '').replace('🛍️', '').replace('🖥️', '').replace('🚪', '').replace('📅', '').replace('🛡️', '').replace('▪', '')
                
                if new_content != content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Removed emojis from {path}")

if __name__ == "__main__":
    process_directory('c:/Users/SENA/Desktop/bluebird_flask/templates')
    print("Done")
