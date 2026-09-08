@echo off
:: Ye file sirf EK BAAR chalani hai, wo bhi "Run as Administrator" karke.
:: Right-click is file par > "Run as administrator"

echo Firewall mein port 8000 allow kiya ja raha hai...
netsh advfirewall firewall add rule name="Malik Garments Server" dir=in action=allow protocol=TCP localport=8000

echo.
echo Done! Ab phone se app khul sakegi.
echo Is file ko dobara chalane ki zarurat nahi hai.
echo.
pause
