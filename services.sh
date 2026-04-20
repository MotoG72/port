cat <<EOF > services.sh
#!/system/bin/sh
/vendor/bin/hw/android.hardware.audio.service.mediatek &
/vendor/bin/hw/android.hardware.biometrics.fingerprint@2.1-service-ets &
/vendor/bin/hw/android.hardware.bluetooth@1.1-service-mediatek &
/vendor/bin/hw/android.hardware.nfc@1.2-service &
/vendor/bin/hw/vendor.mediatek.hardware.mms@1.6-service &
/vendor/bin/hw/vtservice_hidl &

echo "FIX NFC, FOD, IMS, Bluetooth and NFC."
EOF
