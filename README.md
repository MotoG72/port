```markdown
# 📱 G72 Porter Tool v1.0
> **Automated GSI Patching & Mediatek Service Fixer**

This script is designed to optimize and fix common bugs when porting GSIs (Generic System Images), specifically tailored for Mediatek (MTK) devices. It automates file injection, permission fixing, and live service execution.

---

## 🛠️ System Requirements
To run this script correctly in **Termux**, you must install the following dependencies:

### 1. Update the environment
```bash
pkg update && pkg upgrade -y

```
### 2. Install basic tools
```bash
pkg install python git e2fsprogs -y

```
 * **Python**: Required to run the main script.
 * **e2fsprogs**: Contains debugfs, used to read/write inside the .img image.
 * **Git**: To clone the repository and fetch the necessary files.
## 🚀 Installation & Setup
 1. **Clone the repository:**
   ```bash
   git clone [https://github.com/MotoG72/port](https://github.com/MotoG72/port)
   cd port
   
   ```
 2. **Storage Permissions:**
   Ensure Termux has access to your internal storage:
   ```bash
   termux-setup-storage
   
   ```
 3. **Execution Permissions:**
   ```bash
   chmod +x porter.py servicios.sh
   
   ```
## 📖 Usage Guide
The script is managed via command-line flags for a faster workflow:
### A. Patch an external GSI image (-p)
Ideal for preparing the image before flashing. It automatically performs the boot fix, injects the optimized build.prop, and adds the Overlay APK.
```bash
python porter.py -p /sdcard/GSI/system.img

```
### B. Standalone Service Script
You can also run the shell script directly for hardware services without using the Python menu:
```bash
su -c "sh services.sh"

```
## ⚙️ What does the Auto-Patch include?
 * **Boot Fix**: Injects santhm.sh and santhm.rc for persistence during startup.
 * **Build.prop**: Enables VoLTE and sets animation scales to **0.5x** for better UI fluidness.
 * **Overlay APK**: Automatically injects the generated framework-res for the specific product.
 * **Permissions**: Automatically sets UID, GID, and SELinux contexts (u:object_r:system_file:s0).
## ⚠️ Warning
This software interacts directly with system partitions. Use it at your own risk. Always keep a backup of your original system.img.
**Developed by snth** | 2026
```

```
