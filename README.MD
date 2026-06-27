# 🚀 Fraud SaaS Dashboard V6

A full-stack Machine Learning-powered Fraud Detection SaaS built with Streamlit and a FastAPI-style backend. Predict credit card fraud in real time using 30 anonymized features from the classic Kaggle Credit Card Fraud Detection dataset.

---

## ✨ Features

* 30-feature fraud prediction (V1–V28, Time, Amount)
* Interactive Streamlit dashboard
* Real-time fraud risk prediction
* Risk explanation (Low, Medium, High)
* Prediction confidence score
* Random Forest model
* XGBoost model
* Usage analytics dashboard
* Prediction history
* Docker support
* REST API for integration

---

## 🚀 Quick Start

### Clone the repository

```bash
git clone https://github.com/oyofaith802-code/fraud-api.git
cd fraud-api
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the dashboard

```bash
streamlit run streamlit_app.py
```

---

## 🐳 Docker

Build the image:

```bash
docker build -t fraud-saas .
```

Run the container:

```bash
docker run -p 8501:8501 fraud-saas
```

---

## 📡 API Example

```python
import requests

response = requests.post(
    "https://your-api-url/predict",
    json={
        "features":[0.0]*30
    }
)

print(response.json())
```

---

## 🛠 Tech Stack

* Python
* Streamlit
* FastAPI
* scikit-learn
* XGBoost
* NumPy
* Pandas
* SQLite
* Docker

---

## 📊 Model

Dataset:

Kaggle Credit Card Fraud Detection Dataset

Models:

* Random Forest
* XGBoost

Input Features:

* V1
* V2
* V3
* V4
* V5
* V6
* V7
* V8
* V9
* V10
* V11
* V12
* V13
* V14
* V15
* V16
* V17
* V18
* V19
* V20
* V21
* V22
* V23
* V24
* V25
* V26
* V27
* V28
* Time
* Amount

---

## 📁 Project Structure

```text
fraud-api/
├── app.py
├── streamlit_app.py
├── auth.py
├── billing.py
├── database.py
├── models.py
├── admin.py
├── rf_model.pkl
├── xgb_model.pkl
├── scaler.pkl
├── requirements.txt
├── Dockerfile
├── runtime.txt
├── test_api.py
└── README.md
```

---

## 🤝 Contributing

Pull requests and suggestions are welcome.

---

## 👨‍💻 Author

Jeremiah Solomon

GitHub:
https://github.com/oyofaith802-code

---

Built with ❤️ using Python, Streamlit, FastAPI and Machine Learning.
