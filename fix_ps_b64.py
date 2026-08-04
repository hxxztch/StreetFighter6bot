import base64
path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = """def _ps_fetch(url, timeout=15, cookie=None):
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
    )"""

new = """def _ps_fetch(url, timeout=15, cookie=None):
    cookie_b64 = ""
    if cookie:
        cookie_b64 = base64.b64encode(cookie.encode("utf-8")).decode("ascii")
        cookie_b64 = "$cb64='" + cookie_b64 + "';"
    ps_sc = (
        "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; "
        + cookie_b64 +
        "$wc=New-Object System.Net.WebClient; "
        "if($cb64){$c=[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($cb64));$wc.Headers.Add('Cookie',$c)}; "
        "$wc.Headers.Add('User-Agent','Mozilla/5.0 Chrome/126'); "
        "try{$data=$wc.DownloadString('" + url + "'); "
        "$b=[System.Text.Encoding]::UTF8.GetBytes($data);$b64=[Convert]::ToBase64String($b); "
        "[PSCustomObject]@{StatusCode=200;ContentBase64=$b64}|ConvertTo-Json -Compress}catch{exit 1}"
    )"""

content = content.replace(old, new)
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Cookie now passed via base64 to avoid PowerShell string escaping!")
