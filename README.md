This project is deployed on Render (Cloud Application Platform).
When the Chemical Equipment Management System is not actively in use, the backend service automatically enters sleep mode to conserve resources.

As a result, when you access the system after inactivity, the backend may require 1–2 minutes to restart.

Please wait for up to 2 minutes for the backend to fully initialize.

# link -: https://chemical-equipment-parameter-visualizer-2l3r.onrender.com/

# Chemical Equipment Management System

A complete full‑stack project using **Django (Backend)** and **React (Frontend)** that allows uploading, storing, and viewing chemical equipment datasets.

Below is a **fully explained, step‑by‑step README.md**, including `.venv` creation, backend setup, frontend setup, API usage, and workflow explanation.

---

# 📌 1. Project Overview

This system allows users to upload CSV files containing chemical equipment details.  
The backend processes and stores the data in a database, while the frontend displays the datasets in a clean UI.

---

# 📂 2. Project Structure (Explained)

```
Deepak /
├── backend/                # Django backend with REST API
│   ├── api/                # API logic (models, views, serializers)
│   ├── manage.py           # Django admin runner
│   ├── requirements.txt    # Python dependencies
│
├── frontend-react/         # React frontend
│   ├── src/                # Main UI code
│   ├── public/             # HTML template
│   ├── package.json        # Frontend dependencies
│
├── sample_equipment_data.csv   # Example dataset
└── README.md                   # Main documentation file
```

Each folder contains separate logic for backend & frontend.

---

# ⚙️ 3. Backend Setup (Django)

Below are the **complete backend setup steps with explanation**, including `.venv` creation.

---

## 🔧 Step 1 — Create a Virtual Environment (`.venv`)

A virtual environment keeps your project packages isolated.

```
cd backend
python3 -m venv .venv
```

### ✔ Activate the environment:

**Windows**

```
.venv\Scripts\activate
```

**Linux/Mac**

```
source .venv/bin/activate
```

You will now see `(.venv)` before your terminal prompt.

---

## 🔧 Step 2 — Install Backend Requirements

```
pip install -r requirements.txt
```

This installs:

- Django
- Django REST Framework
- CORS headers
- Other required dependencies

---

## 🔧 Step 3 — Apply Database Migrations

```
python manage.py migrate
```

This creates all default Django tables inside `db.sqlite3`.

---

## 🔧 Step 4 — Run the Django Server

```
python manage.py runserver
```

Your backend is live at: (only in localhost )
👉 **http://127.0.0.1:8000/**

---

# 🌐 4. Frontend Setup (React)

## 🔧 Step 1 — Install Node Packages

```
cd frontend-react
npm install
```

This installs React, React Router, and all UI packages.

---

## 🔧 Step 2 — Start the Frontend

```
npm start
```

Your frontend will run at: (only in localhost )
👉 **http://localhost:3000/**

---

# 🔗 5. API Documentation (Explained)

## 📤 **1. Upload CSV File**

```
POST /api/upload/
```

**Used by:** UploadForm.js  
Sends CSV file and the backend saves data into the database.

---

## 📄 **2. Get All Datasets**

```
GET /api/datasets/
```

Returns a list of all uploaded datasets.

---

## 📄 **3. Get Single Dataset Items**

```
GET /api/datasets/<id>/
```

Returns all rows belonging to a specific dataset.

---

# 📥 6. CSV Upload Workflow (Step‑by‑Step Explanation)

1. User selects CSV file from frontend
2. React sends file → Django API (`POST /api/upload/`)
3. Django reads CSV using Python
4. Creates new dataset entry
5. Stores each row in database
6. Frontend displays dataset in a table
7. User can click dataset to view details

This ensures smooth data flow between UI ↔ API ↔ Database.

---

# 🛠 7. How to Run the Entire Project at Once

### ✔ Step 1 — Start Backend

```
cd backend
source .venv/bin/activate    # or .venv\Scripts\activate for Windows
python manage.py runserver
```

### ✔ Step 2 — Start Frontend

```
cd frontend-react
npm start
```

### ✔ Step 3 — Open in Browser

(only in localhost )
Frontend: **http://localhost:3000/**  
Backend API: **http://127.0.0.1:8000/api/**

### ✔ Step 4 - Open Desktop and Web by using main.py file

```
cd frontend-pyqt
python main.py --run Desktop   ----For Desktop.
python main.py --run Website   ----For open on the browser.
```

# 🎯 8. Tech Stack

### **Frontend**

- React.js
- Fetch API
- HTML/CSS

### **Backend**

- Python
- Django
- Django REST Framework
- SQLite Database

---

# 🤝 9. Contributing

Open a PR or issue to add new features or report bugs.
