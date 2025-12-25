
import os

file_path = '.env'
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Target line part to replace
    old_cors = 'CORS_ORIGINS=["http://localhost:3000","http://localhost:8080","http://localhost:8000"]'
    new_cors = 'CORS_ORIGINS=["http://localhost:3000","http://localhost:8080","http://localhost:8000","http://localhost:3002"]'
    
    if new_cors not in content:
        if old_cors in content:
            new_content = content.replace(old_cors, new_cors)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("Successfully updated CORS_ORIGINS")
        else:
            # Fallback for slight variations or if already updated partially differently
            # We'll just append it if not found, or regex replace if needed, but simple replace is safer for now
            # If line exists but different, let's try to find the key
            lines = content.splitlines()
            new_lines = []
            updated = False
            for line in lines:
                if line.startswith('CORS_ORIGINS=') and 'http://localhost:3002' not in line:
                    # Append strictly inside the brackets
                    if line.strip().endswith(']'):
                        line = line.strip()[:-1] + ',"http://localhost:3002"]'
                        updated = True
                new_lines.append(line)
            
            if updated:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(new_lines))
                print("Successfully updated CORS_ORIGINS via parsing")
            else:
                print("CORS_ORIGINS might already be correct or format unexpected")
    else:
        print("CORS_ORIGINS already correct")

except Exception as e:
    print(f"Error: {e}")
