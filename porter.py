import os
import subprocess
import argparse
import sys

TMP_DIR = "/sdcard/GSI/tmp"
DEFAULT_APK = "./port/framework-res__auto_generated_rro_product.apk"

def run_debugfs(img_path, cmd):
    full_process = f"echo '{cmd}' | debugfs -w {img_path}"
    result = subprocess.run(full_process, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr

def apply_fix_perms(img_path, remote_path, mode_hex="0x81a4"):
    run_debugfs(img_path, f"sif {remote_path} uid 0")
    run_debugfs(img_path, f"sif {remote_path} gid 0")
    run_debugfs(img_path, f"sif {remote_path} mode {mode_hex}")
    run_debugfs(img_path, f"ea_set {remote_path} security.selinux u:object_r:system_file:s0")

def auto_patch(img_path):
    if not os.path.exists(img_path):
        print(f"Error: Image {img_path} not found.")
        return

    os.makedirs(TMP_DIR, exist_ok=True)
    
    # 1. Boot Fix (SH/RC)
    sh_path, rc_path = f"{TMP_DIR}/santhm.sh", f"{TMP_DIR}/santhm.rc"
    with open(sh_path, "w") as f:
        f.write("#!/system/bin/sh\n"
                "/vendor/bin/hw/android.hardware.audio.service.mediatek &\n"
                "/vendor/bin/hw/android.hardware.biometrics.fingerprint@2.1-service-ets &\n"
                "/vendor/bin/hw/android.hardware.bluetooth@1.1-service-mediatek &\n"
                "/vendor/bin/hw/android.hardware.nfc@1.2-service &\n"
                "/vendor/bin/hw/vendor.mediatek.hardware.mms@1.6-service &\n"
                "/vendor/bin/hw/vtservice_hidl &\n")
    with open(rc_path, "w") as f:
        f.write("on property:sys.boot_completed=1\n"
                "    exec u:r:shell:s0 root root -- /system/bin/sh /system/etc/santhm.sh\n")

    for local, remote, mode in [(sh_path, "/system/etc/santhm.sh", "0x81ed"), 
                                 (rc_path, "/system/etc/init/santhm.rc", "0x81a4")]:
        run_debugfs(img_path, f"rm {remote}")
        run_debugfs(img_path, f"write {local} {remote}")
        apply_fix_perms(img_path, remote, mode)

    # 2. Build Prop Fix
    local_prop = f"{TMP_DIR}/build.prop"
    run_debugfs(img_path, f"dump /system/build.prop {local_prop}")
    if os.path.exists(local_prop):
        props = ["\n# Vicky Fixes", "persist.vendor.mtk.volte.enable=1", "persist.vendor.radio.volte_state=1",
                 "vendor.ril.mtk_hvolte_indicator=1", "persist.vendor.ril.mtk_hvolte_indicator=1",
                 "persist.sys.window_animation_scale=0.5", "persist.sys.transition_animation_scale=0.5",
                 "persist.sys.animator_duration_scale=0.5"]
        with open(local_prop, "a") as f:
            for p in props: f.write(f"{p}\n")
        run_debugfs(img_path, "rm /system/build.prop")
        run_debugfs(img_path, f"write {local_prop} /system/build.prop")
        apply_fix_perms(img_path, "/system/build.prop", "0x81a4")

    # 3. Overlay APK
    if os.path.exists(DEFAULT_APK):
        remote_apk = f"/system/product/overlay/{os.path.basename(DEFAULT_APK)}"
        run_debugfs(img_path, f"rm {remote_apk}")
        run_debugfs(img_path, f"write {DEFAULT_APK} {remote_apk}")
        apply_fix_perms(img_path, remote_apk, "0x81a4")
    else:
        print(f"Warning: APK {DEFAULT_APK} not found. Skipping overlay.")

def main():
    parser = argparse.ArgumentParser(description="G72 Porter Tool", add_help=False)
    parser.add_argument("-p", "--patch", metavar="IMG_PATH", help="Path to GSI image to patch automatically")
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")

    args = parser.parse_args()

    if args.patch:
        auto_patch(args.patch)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
