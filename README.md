# 🏠 Sifely Cloud - Home Assistant Integration

A **custom integration** for Home Assistant that connects to **Sifely smart locks** using the official Sifely Cloud API. Provides real-time visibility and control over your locks, with enhanced diagnostic and history features.

## 📚 API Documentation
All Sifely Cloud API endpoints used in this integration are based on the official documentation:
🔗 [https://apidocs.sifely.com](https://apidocs.sifely.com)
This includes authentication, lock control, history querying, and diagnostics.



![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg) ![license](https://img.shields.io/github/license/yourname/sifely_cloud.svg)

---

## 📦 Features

- 🔐 **Lock/Unlock support**
- 🪫 **Battery level monitoring**
- 📖 **Historical event logging** (username, method, success/fail)
- 🚨 **Cloud error diagnostics**
- 🧠 **Open/closed state polling**
- 👁 **Privacy Lock** and **Tamper Alert** binary sensors
- 💾 **Persisted history** with CSV logging
- 🕓 **Automatic background polling** (every 5 minutes for history)
- 🧰 Compatible with **Entity Category Diagnostics** for advanced insights

---


## 🖼️ UI Screenshots (Examples)
Below are examples of how entities appear in the Home Assistant UI. These include:

Integration setup screen

Lock control

Battery and diagnostic sensors

Privacy Lock and Tamper Alert binary sensors

Lock history sensor with structured entries




## 🔧 Installation

### Manual Installation

1. Copy the folder `sifely_cloud/` to your Home Assistant `custom_components/` directory:

```bash
config/custom_components/sifely_cloud/
```


2. Restart Home Assistant.

3. Navigate to **Settings > Devices & Services > Integrations**
   Click ➕ Add Integration → Search for **Sifely Cloud**

4. Enter your credentials and Client ID from the Sifely app.

---

## 🛠 Configuration Options

- **Email / Password** – Your Sifely cloud account credentials
- **Client ID** – A unique identifier used to access the Sifely API
  - 📌 How to obtain your Client ID:
  - Go to the Sifely Smart Manager Portal [https://app-smart-manager.sifely.com/Login.html](https://app-smart-manager.sifely.com/Login.html)
  - Log in using your Sifely app username and password
  - After loging in you will be shown your clientId (What you need) and a clientSecret (not needed)
- **Number of Locks (APX)** – Approximate number of locks to query
- **Number of History Entries** – Maximum recent events to retain (default: `20`)

---

## 🛠 Developer Configuration via `const.py`

Advanced users and developers can override default settings by editing the `const.py` file directly. This includes:

- Polling intervals (e.g. history updates every 5 minutes)
- Maximum number of retries
- History record type labels
- Default limits for entities and diagnostics
- Error thresholds before token refresh

📄 All key values and internal constants are defined in:

```bash
custom_components/sifely_cloud/const.py
```

---

## 🧪 Entities Created

| Entity Type     | Description                             |
|-----------------|-----------------------------------------|
| `lock`          | Lock/unlock control for each Sifely lock |
| `sensor`        | Battery sensor + recent history text     |
| `binary_sensor` | Privacy Lock & Tamper Alert flags        |
| `sensor`        | Cloud error diagnostics                  |

---

## 📁 File Persistence

- Historical records are saved to:
```bash
config/custom_components/sifely_cloud/history/history_<lockId>.csv
```

- Only *new* records are appended; existing entries are deduplicated based on `recordId`.

---

## 🔍 Future Roadmap

- [ ] Lock schedule viewer/editor
- [ ] Doorbell / touch event detection (if supported)
- [ ] Configurable polling intervals
- [ ] Auto-restore lock history from cloud on reboot

---

## 🧑‍💻 Contributing / Issues

Got a feature request, bug report, or enhancement idea?

👉 [Open an Issue or Feature Request](https://github.com/kenster1965/sifely_cloud/issues)

Pull requests welcome!

---

## 📜 Disclaimer

This is an independent project and is **not affiliated with Sifely**. Use at your own risk. API behavior may change without notice.

---

## 📄 License

[MIT License](LICENSE)

---


