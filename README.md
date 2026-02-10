# 🧪 Chemical Equipment Data Analyzer

A full-stack **web and desktop application** for analyzing chemical equipment data from CSV files.  
The system processes uploaded datasets, computes summary statistics, visualizes results using charts, and allows users to download analysis reports as PDFs.

---

## 🚀 Features

- Upload CSV files containing chemical equipment data
- Automatic data analysis using Pandas
- Summary statistics:
  - Total equipment count
  - Average flowrate
  - Maximum pressure
  - Temperature range
- Data visualization:
  - Bar chart (Flowrate, Pressure, Temperature)
  - Pie chart (Equipment type distribution)
- Stores and displays last 5 uploaded datasets
- Download analysis output as **PDF report**
- Available as:
  - 🌐 Web application
  - 🖥️ Desktop application

---

## 🧰 Tech Stack

### Backend
- Python
- Django
- Django REST Framework
- Pandas
- SQLite

### Frontend (Web)
- React.js
- Chart.js

### Frontend (Desktop)
- PyQt5
- Matplotlib

---

## 📁 Project Structure

```
chemical-project/
│
├── backend/                 # Django backend
│   ├── backend/
│   ├── equipment/
│   ├── db.sqlite3
│   └── manage.py
│
├── frontend-web/            # React web app
│   ├── src/
│   ├── public/
│   └── package.json
│
├── frontend-desktop/        # PyQt5 desktop app
│   ├── app.py
│   ├── dist/                # Generated EXE (optional)
│   └── build/
│
└── README.md
```

---

## ▶️ How to Run the Project

### 1️⃣ Start Backend (Required)

```bash
cd backend
python manage.py runserver
```

Backend runs at:
```
http://127.0.0.1:8000
```

---

### 2️⃣ Run Web Application

```bash
cd frontend-web
npm install
npm start
```

Web app runs at:
```
http://localhost:3000
```

---

### 3️⃣ Run Desktop Application

```bash
cd frontend-desktop
python app.py
```

> ⚠️ Backend must be running before launching the desktop app.

---

## 📄 Sample CSV Format

```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-1,Pump,120,5.2,110
Valve-1,Valve,60,4.1,105
Reactor-1,Reactor,140,7.5,140
```

---

## 📥 PDF Download

- Both **web** and **desktop** versions allow downloading the analysis output as a **PDF report**
- The report includes:
  - Summary statistics
  - Bar chart
  - Pie chart

---

## 📌 Notes

- This project is intended for **educational and academic use**
- SQLite is used for simplicity and portability
- The desktop application communicates with the same Django backend as the web app

---

## 👤 Author

**Arjun Tiwari**
