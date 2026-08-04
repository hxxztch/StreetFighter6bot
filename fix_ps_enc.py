path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the ps_cmd to use base64 encoding to avoid encoding issues
old_cmd = """'[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; '
        f'try {{ $r = Invoke-WebRequest -Uri \"{url}\" -Method Get -TimeoutSec {timeout} -UseBasicParsing; '
        f'[PSCustomObject]@{{StatusCode=$r.StatusCode; Content=$r.Content; Headers=$r.Headers.ToString()}} | ConvertTo-Json -Compress }} '
        f'catch {{ Write-Error $_.Exception.Message; exit 1 }}'"""

new_cmd = """'[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; '
        f'try {{ $r = Invoke-WebRequest -Uri \"{url}\" -Method Get -TimeoutSec {timeout} -UseBasicParsing; '
        f'$b = [System.Text.Encoding]::UTF8.GetBytes($r.Content); $b64 = [Convert]::ToBase64String($b); '
        f'[PSCustomObject]@{{StatusCode=$r.StatusCode; ContentBase64=$b64; Headers=$r.Headers.ToString()}} | ConvertTo-Json -Compress }} '
        f'catch {{ Write-Error $_.Exception.Message; exit 1 }}'"""

content = content.replace(old_cmd, new_cmd)

# Fix the decoding after subprocess - decode base64
old_result = """if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout.strip())"""

new_result = """if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout.strip())
            if "ContentBase64" in data:
                import base64
                data["Content"] = base64.b64decode(data["ContentBase64"]).decode("utf-8", errors="replace")
                del data["ContentBase64"]
            return data"""

content = content.replace(old_result, new_result)

# Also fix the encoding parameter in subprocess.run
old_run = """result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=timeout + 5, encoding="utf-8"
        )"""

new_run = """result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=timeout + 5
        )"""

content = content.replace(old_run, new_run)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Encoding fix applied - uses base64 to bypass encoding issues")
