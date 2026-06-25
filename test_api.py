import requests

url = "https://fraud-api-1d91.onrender.com/predict"

headers = {
    "api-key": "my_secret_12345"
}

data = {
    "V1": 0.1, "V2": -1.2, "V3": 0.3, "V4": 1.1,
    "V5": -0.4, "V6": 0.2, "V7": -0.9, "V8": 0.5,
    "V9": -0.3, "V10": 0.7, "V11": 0.1, "V12": -0.2,
    "V13": 0.4, "V14": -1.1, "V15": 0.6, "V16": -0.5,
    "V17": 0.8, "V18": -0.7, "V19": 0.2, "V20": -0.1,
    "V21": 0.3, "V22": -0.4, "V23": 0.5, "V24": -0.6,
    "V25": 0.7, "V26": -0.2, "V27": 0.1, "V28": -0.3,
    "Amount": 250,
    "Time": 50000
}

res = requests.post(url, json=data, headers=headers)

print(res.json())