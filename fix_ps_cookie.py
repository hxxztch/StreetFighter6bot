path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = "_ps_fetch(url, timeout=15, cookie=None):"
idx = content.find(old)
if idx < 0:
    print("NOT FOUND")
else:
    # Find the function body
    func_start = content.find("def _ps_fetch")
    next_func = content.find("\ndef _", func_start + 1)
    if next_func < 0:
        next_func = content.find("\ndef scrape_", func_start + 1)
    if next_func < 0:
        next_func = len(content)

    # New function
    new_func = '''def _ps_fetch(url, timeout=15, cookie=None):
    cookie_var = ""
    if cookie:
        # Pass cookie via PowerShell variable to avoid escaping hell
        cookie_var = "$c='" + cookie + "';"
    ps_sc = (
        "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; "
        + cookie_var +
        "$wc=New-Object System.Net.WebClient; "
        "if($c){$wc.Headers.Add('Cookie',$c)}; "
        "$wc.Headers.Add('User-Agent','Mozilla/5.0 Chrome/126'); "
        "try{$data=$wc.DownloadString('" + url + "'); "
        "$b=[System.Text.Encoding]::UTF8.GetBytes($data);$b64=[Convert]::ToBase64String($b); "
        "[PSCustomObject]@{StatusCode=200;ContentBase64=$b64}|ConvertTo-Json -Compress}catch{exit 1}"
    )
'''

    content = content[:func_start] + new_func + content[next_func:]
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("_ps_fetch rewritten with WebClient (safe cookie handling)!")

