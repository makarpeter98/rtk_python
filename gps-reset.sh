#!/bin/bash
# gps-reset.sh
# Futtasd: sudo ./gps-reset.sh
set -euo pipefail

DEVICE="/dev/ttyACM0"
GPSD_SOCKET="/var/run/gpsd.sock"
LOG="/tmp/gpsd-restart.log"

echo "1) Ellenőrzés: létezik-e az eszköz: $DEVICE"
if [ ! -e "$DEVICE" ]; then
  echo "HIBA: $DEVICE nem található. Ellenőrizd a csatlakozást." >&2
  exit 2
fi

echo "2) Leállítjuk a systemd gpsd szolgáltatást (ha fut)."
systemctl stop gpsd.service || true

echo "3) Megöljük a $DEVICE-t foglaló folyamatokat (ha vannak)."
# fuser -k sends SIGKILL to processes using the device
fuser -k "$DEVICE" 2>/dev/null || true
# plus extra catch-all
pkill -f gpsd 2>/dev/null || true
sleep 0.3

echo "4) Töröljük a régi socketet (ha van)."
rm -f "$GPSD_SOCKET" || true

echo "5) Jogosultságok ellenőrzése / dialout csoport hozzáadás (ha szükséges)."
# csak javaslat: ha nem akarod automatikusan hozzáadni, vedd ki az 'usermod' sort
if ! id "$SUDO_USER" &>/dev/null; then
  echo "Nem találtam SUDO_USER-t — ha nem root-ként futtatsz, győződj meg róla, hogy a felhasználó a dialout csoport tagja."
else
  echo "Hozzáadom $SUDO_USER felhasználót a dialout csoporthoz (ha még nincs benne)."
  usermod -aG dialout "$SUDO_USER" || true
fi

echo "6) Indítjuk a gpsd-t manuálisan erre az eszközre, log: $LOG"
# gpsd -N = foreground, -n = ne várjon kliensre; de a & visszarakja háttérbe
/usr/sbin/gpsd -n -F "$GPSD_SOCKET" "$DEVICE" > "$LOG" 2>&1 &

GPSD_PID=$!
sleep 0.7

echo "gpsd PID: $GPSD_PID"
sleep 1

echo "7) Gyors ellenőrzések"
echo "- systemctl status gpsd.service (meg fogja mutatni, hogy a systemd verzió nem fut-e)"
systemctl status gpsd.service --no-pager || true

echo "- Van-e olvasható NMEA kimenet a device-on (kísérlet: 1 másodperc olvasás)"
timeout 1 cat "$DEVICE" | sed -n '1,10p' || true

echo "- gpsd log (utolsó 20 sor):"
tail -n 20 "$LOG" || true

echo "8) Ajánlott: futtasd a cgps -s vagy gpsmon parancsot új terminálban:"
echo "   cgps -s"
echo "   -- vagy --"
echo "   gpsmon $DEVICE"

echo
echo "Ha inkább a systemd szolgáltatást használod tartósan, szerkeszd az /etc/default/gpsd (vagy /etc/default/gpsd) fájlt és állítsd be:"
echo "  DEVICES=\"$DEVICE\""
echo "majd:"
echo "  systemctl enable --now gpsd.service"

echo
echo "Kész. Ha továbbra is N/A a cgps, menj ki szabad térre, vagy várj 1-2 percet a fixre."
exit 0
