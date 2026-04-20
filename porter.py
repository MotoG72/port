import os
import subprocess

GSI_IMG = "/sdcard/GSI/gsi.img"
TMP_DIR = "/sdcard/GSI/tmp"

def run_debugfs(cmd):
    full_process = f"echo '{cmd}' | debugfs -w {GSI_IMG}"
    result = subprocess.run(
        full_process, 
        shell=True, 
        capture_output=True, 
        text=True
    )
    return result.stdout, result.stderr

def apply_fix_perms(remote_path, mode_hex="0x81a4"):
    run_debugfs(f"sif {remote_path} uid 0")
    run_debugfs(f"sif {remote_path} gid 0")
    run_debugfs(f"sif {remote_path} mode {mode_hex}")
    run_debugfs(f"ea_set {remote_path} security.selinux u:object_r:system_file:s0")

def check_file_exists(remote_path):
    out, _ = run_debugfs(f"stat {remote_path}")
    return "Inode:" in out

def menu_boot_fix():
    os.makedirs(TMP_DIR, exist_ok=True)
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
        run_debugfs(f"rm {remote}")
        run_debugfs(f"write {local} {remote}")
        apply_fix_perms(remote, mode)

def menu_build_prop():
    os.makedirs(TMP_DIR, exist_ok=True)
    local_prop = f"{TMP_DIR}/build.prop"
    
    run_debugfs(f"dump /system/build.prop {local_prop}")
    
    if not os.path.exists(local_prop):
        return

    props = [
        "\n# Vicky Fixes",
        "persist.vendor.mtk.volte.enable=1",
        "persist.vendor.radio.volte_state=1",
        "vendor.ril.mtk_hvolte_indicator=1",
        "persist.vendor.ril.mtk_hvolte_indicator=1",
        "persist.sys.window_animation_scale=0.5",
        "persist.sys.transition_animation_scale=0.5",
        "persist.sys.animator_duration_scale=0.5"
    ]

    with open(local_prop, "a") as f:
        for p in props: f.write(f"{p}\n")
    
    run_debugfs("rm /system/build.prop")
    run_debugfs(f"write {local_prop} /system/build.prop")
    apply_fix_perms("/system/build.prop", "0x81a4")

def menu_overlay():
    apk_path = input("Paste the full APK path: ").strip()
    if not os.path.exists(apk_path):
        return

    apk_name = os.path.basename(apk_path)
    remote_path = f"/system/product/overlay/{apk_name}"

    run_debugfs(f"rm {remote_path}")
    run_debugfs(f"write {apk_path} {remote_path}")
    apply_fix_perms(remote_path, "0x81a4")

def menu_check():
    targets = ["/system/build.prop", "/system/etc/santhm.sh", "/system/etc/init/santhm.rc"]
    for t in targets:
        run_debugfs(f"stat {t}")
        run_debugfs(f"ea_get {t} security.selinux")

def main():
    if not os.path.exists(GSI_IMG):
        return

    while True:
        os.system("clear")
        print("\n========================================")
        print("   G72 PORTER v1.0 - MENU")
        print("========================================")
        print("1. Fix HAL")
        print("2. Fix VoLTE + LAG")
        print("3. Overlay APK")
        print("4. Verify (Stats)")
        print("5. Exit")
        
        opc = input("\nSelect an option: ")
        if opc == '1': menu_boot_fix()
        elif opc == '2': menu_build_prop()
        elif opc == '3': menu_overlay()
        elif opc == '4': menu_check()
        elif opc == '5': break

if __name__ == "__main__":
    main()
