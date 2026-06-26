Fraud SaaS Dashboard V6

A full-stack *Machine Learning-powered Fraud Detection SaaS* built with Streamlit + FastAPI-style backend. Predict credit card fraud in real-time using 30 anonymized features.

![Dashboard Preview](https://i.imgur.com/your-screenshot-link-here.png) <!-- Replace with actual image/GIF -->

## ✨ Features

- *30-Feature Fraud Prediction* (V1–V30)
- *Streamlit Dashboard* with clean UI
- *User Authentication* (Login/Signup)
- *API Key System* for programmatic access
- *Real-time Analytics* (total requests, fraud/normal cases)
- *Result Explanation* with risk level and confidence
- *Two Models*: Random Forest + XGBoost
- *Docker Support* for easy deployment

## 🚀 Quick Start

### Local Development

```bash
# Clone the repo
git clone https://github.com/oyofaith802-code/fraud-api.git
cd fraud-api

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run streamlit_app.py
Using Docker
docker build -t fraud-saas .
docker run -p 8501:8501 fraud-saas
📡 API Usage
import requests

response = requests.post(
    "https://your-deployed-url/predict",
    json={"features": [0.0, 0.02, ...]},
    headers={"X-API-Key": "fk_..."}
)
print(response.json())
🛠️ Tech Stack
Frontend: Streamlit
Backend: Python + FastAPI-style structure
ML: scikit-learn (Random Forest), XGBoost
Database: SQLite / PostgreSQL support
Deployment: Docker, Streamlit Sharing, Render/Heroku, etc.
📊 Model Performance
Trained on classic anonymized credit card fraud dataset
Supports both Random Forest and XGBoost models
📁 Project Structure
fraud-api/
├── streamlit_app.py      # Main dashboard
├── app.py                # Backend API
├── auth.py               # Authentication
├── models.py             # ML models
├── billing.py            # Usage tracking
├── rf_model.pkl          # Trained models
├── xgb_model.pkl
├── scaler.pkl
├── requirements.txt
├── Dockerfile
└── test_api.py
🤝 Contributing
Contributions are welcome! Feel free to open issues or pull requests.
📧 Contact
GitHub: @oyofaith802-code
Built by Solomon (Jeremiah Solomon)
