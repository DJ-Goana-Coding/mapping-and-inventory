#!/data/data/com.termux/files/usr/bin/bash

echo "=== OPPO / COLOROS SAFE AUTO-DEBLOAT ==="
echo "Installing ADB tools..."
pkg install -y android-tools

echo "Ensuring device is connected..."
adb devices

echo "Starting automatic safe debloat..."

SAFE_PACKAGES=(
    # --- Oppo / ColorOS bloat ---
    "com.coloros.assistantscreen"
    "com.coloros.backuprestore"
    "com.coloros.childrenspace"
    "com.coloros.gamespace"
    "com.coloros.healthcheck"
    "com.coloros.musicparty"
    "com.coloros.videoeditor"
    "com.coloros.weather.service"
    "com.coloros.weather2"
    "com.coloros.smartdrive"
    "com.coloros.smartsidebar"
    "com.coloros.soundrecorder"
    "com.coloros.filemanager"   # safe to remove if you use another file manager
    "com.coloros.gallery3d"     # safe if you use another gallery

    # --- Oppo Internet / Browser ---
    "com.heytap.browser"
    "com.oppo.market"
    "com.oppo.operationManual"

    # --- Facebook preloads ---
    "com.facebook.appmanager"
    "com.facebook.services"
    "com.facebook.system"

    # --- Google bloat (safe to remove) ---
    "com.google.android.apps.tachyon"        # Google Duo
    "com.google.android.apps.youtube.music"  # YouTube Music
    "com.google.android.videos"              # Google Movies
    "com.google.android.music"               # Google Music (legacy)
    "com.google.android.apps.docs"           # Google Drive app
    "com.google.android.apps.maps"           # Google Maps (safe if unused)
    "com.google.android.apps.photos"         # Google Photos (safe if unused)

    # --- Partner bloat ---
    "com.netflix.partner.activation"
    "com.netflix.mediaclient"

    # --- Analytics / tracking ---
    "com.oppo.logkit"
    "com.coloros.oppoguardelf"
    "com.coloros.athena"
)

for PKG in "${SAFE_PACKAGES[@]}"; do
    echo "Uninstalling: $PKG"
    adb shell pm uninstall --user 0 "$PKG"
done

echo "=== AUTO-DEBLOAT COMPLETE ==="
echo "Reboot recommended."
