$WinRARPath = "C:\Program Files\WinRAR\WinRAR.exe" # Update with your WinRAR installation path
$FolderPath = "C:\BrightCom\GitHub\mstjernfelt\script.IPTVConverter\script.IPTVConverter\"       # Update with the folder path you want to compress
$OutputFileName = "C:\BrightCom\GitHub\mstjernfelt\script.IPTVConverter\script.IPTVConverter.zip"                     # Update with the desired name for the output ZIP file

$WinRARArgs = "a -r ""$OutputFileName"" ""$FolderPath"""

Start-Process -FilePath $WinRARPath -ArgumentList $WinRARArgs -Wait

# $sourceFolder = "script.IPTVConverter"

# Copy-Item -Path $sourceFolder -Destination "C:\Users\MathiasStjernfelt\AppData\Roaming\Kodi\addons\script.IPTVConverter\" -Recurse -Force

# Start-Process "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Kodi\Kodi - Portable.lnk"

# $KodiIP = "localhost"  # Replace with the IP address or hostname of the Kodi device
# $Username = "kodi"  # Replace with your Kodi username
# $Password = "kodi"  # Replace with your Kodi password
# $SecurePassword = ConvertTo-SecureString $Password -AsPlainText -Force

# $RequestBody = @{
#     jsonrpc = "2.0"
#     method = "Addons.ExecuteAddon"
#     params = @{
#         addonid = "script.IPTVConverter"
#     }
#     id = 1
# } | ConvertTo-Json

# $Headers = @{
#     "Content-Type" = "application/json"
# }

# $KodiURL = "http://$($KodiIP):8080/jsonrpc"

# $Credentials = New-Object System.Management.Automation.PSCredential -argumentList $Username, $SecurePassword

# Invoke-RestMethod -Uri $KodiURL -Credential $Credentials -Method Post -Headers $Headers -Body $RequestBody

# Start-Process "http://mathias-msigs66:5555/"

# # $username =''
# # $pwd = ''
# # $hostname = ''
# # $port = ''
# # $jsonmethod = 'Player.GetActivePlayers'
# # $secpwd = ConvertTo-SecureString $pwd -AsPlainText -Force
# # $a=', "params": {"properties": ["title", "album", "artist", "season", "episode", "duration", "showtitle","tvshowid", "thumbnail", "file", "fanart", "streamdetails"], "playerid": 1 }, "id": "VideoGetItem"'
# # $json = '{"jsonrpc":"2.0","id":1,"method":"'+$jsonmethod+$a'}'
# # $url = 'http://'+$hostname+':'+$port+'/jsonrpc'
# # $mycreds = New-Object System.Management.Automation.PSCredential ($username, $secpwd)
# # $webreq = Invoke-WebRequest -Uri $url -Credential $mycreds -Body $json -ContentType application/json -Method POST