import os

def check_telegram():
    found_any = False
    for root, dirs, files in os.walk('C:\\Users\\99196\\teamwork_projects\\resume_e_portfolio_update\\job'):
        if '.git' in root or '.agents' in root:
            continue
        for file in files:
            if file.endswith(('.html', '.css', '.js', '.md', '.txt')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines, 1):
                            if 'telegram' in line.lower():
                                print(f"Found 'telegram' in {filepath}:{i} -> {line.strip()}")
                                found_any = True
                except Exception as e:
                    pass
    if not found_any:
        print("Telegram verification passed: No instances of 'telegram' found in any source files.")

if __name__ == '__main__':
    check_telegram()
