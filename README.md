# ❤️ Real-Time Heart Rate Monitoring System

A real-time heart rate monitoring system using Arduino and Python that visualizes live BPM data, logs readings, and generates a professional report automatically.

---

## 🚀 Features

* 📡 Real-time heart rate monitoring using Pulse Sensor
* 📈 Live BPM graph visualization
* 🧾 Automatic CSV logging
* 📊 Smart PDF report generation
* 🧠 Intelligent analysis (average, trend, variation)
* 📂 Organized output folder
* 🔗 Includes GitHub & LinkedIn integration in reports

---

## 🛠️ Tech Stack

* Arduino (Pulse Sensor)
* Python
* Matplotlib
* PySerial
* ReportLab

---

## 📂 Project Structure

```
Heart-Rate-Monitoring-System/
├── Arduino/
│   └── heart_rate_monitor.ino
├── Python/
│   └── app.py
├── assets/
│   ├── graph.png
│   └── report.png
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ How to Run

### 1. Upload Arduino Code

* Connect your Arduino
* Upload the `.ino` file

---

### 2. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

---

### 3. Run the Application

```bash
python3 app.py
```

---

## 🧪 Usage

1. Place your finger on the sensor
2. Wait 20–30 seconds
3. Close the graph window

👉 A PDF report will be generated automatically

---

## 🔌 Wiring

### Pulse Sensor
- VCC → 5V  
- GND → GND  
- Signal → A0  

### LCD (I2C)
- VCC → 5V  
- GND → GND  
- SDA → A4  
- SCL → A5  

### Buzzer
- + → D11  
- - → GND  

---

### 📌 Note
Keep your finger steady for 20–30 seconds before closing the window to ensure an accurate report.
## ⚠️ Important Note

Keep your finger steady for 20–30 seconds before closing the window to ensure an accurate report.

---

## 📊 Output

The system generates:

* CSV log file
* BPM chart image
* PDF report

(All stored in the `output/` folder)

---

## 👤 Author

**Ahmed Gamal**

🔗 GitHub: https://github.com/AGamal-X
🔗 LinkedIn: https://www.linkedin.com/in/ahmdgamall/

---

## ⭐ Project Highlights

This project demonstrates:

* Real-time data processing
* Hardware-software integration
* Data visualization
* Automated reporting

---

## 📌 Future Improvements

* GUI interface
* Mobile app integration
* Cloud data storage
* AI-based anomaly detection

---

