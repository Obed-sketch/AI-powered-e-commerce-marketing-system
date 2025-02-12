graph TD
    A[Data Sources] --> B[Data Pipeline]
    B --> C[ML Models]
    C --> D[Marketing Actions]
    D --> E[Performance Tracking]
    E --> B


import pandas as pd
from sklearn.preprocessing import StandardScaler

# Load sample data
data = pd.read_csv('ecommerce_data.csv')

# Preprocessing
def preprocess_data(df):
    # Handle missing values
    df = df.fillna(df.mean())
    
    # Feature engineering
    df['total_spent'] = df['price'] * df['quantity']
    df['last_purchase_days'] = (pd.to_datetime('today') - pd.to_datetime(df['purchase_date'])).dt.days
    
    # RFM features
    rfm = df.groupby('customer_id').agg({
        'last_purchase_days': 'min',
        'order_id': 'count',
        'total_spent': 'sum'
    })
    rfm.columns = ['recency', 'frequency', 'monetary']
    
    # Scaling
    scaler = StandardScaler()
    return scaler.fit_transform(rfm)

processed_data = preprocess_data(data)


## Model Development
# Customer Segmentation (Clustering)
from sklearn.cluster import KMeans

kmeans = KMeans(n_clusters=4)
segments = kmeans.fit_predict(processed_data)

# b. Churn Prediction (Classification)
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split

# Sample churn labels
X_train, X_test, y_train, y_test = train_test_split(processed_data, churn_labels)

model = XGBClassifier()
model.fit(X_train, y_train)

#c. Recommendation System
from surprise import SVD
from surprise import Dataset, Reader

# Load ratings data
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(ratings_df[['user_id', 'item_id', 'rating']], reader)

# Train model
algo = SVD()
trainset = data.build_full_trainset()
algo.fit(trainset)

#4. Marketing Automation Integration
#Email Trigger:
import sendgrid
from sendgrid.helpers.mail import Mail

def send_winback_email(customer_email):
    message = Mail(
        from_email='marketing@store.com',
        to_emails=customer_email,
        subject='We miss you!',
        html_content='<strong>Special 20% discount just for you!</strong>')
    
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    response = sg.send(message)

#5. API Deployment with Flask

from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)
model = joblib.load('churn_model.pkl')

@app.route('/predict_churn', methods=['POST'])
def predict_churn():
    data = request.json
    prediction = model.predict([data['features']])
    return jsonify({'churn_risk': prediction[0]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

#Deployment Pipeline
#Dockerfile:
FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]

#7. Monitoring & Maintenance
# Model performance monitoring
from prometheus_client import start_http_server, Counter

PREDICTION_COUNTER = Counter('churn_predictions', 'Number of predictions made')

@app.route('/predict_churn', methods=['POST'])
def predict_churn():
    PREDICTION_COUNTER.inc()
    # ... prediction logic ...

#Retraining Pipeline:
# Scheduled retraining script
def retrain_model():
    new_data = load_recent_data()
    updated_model = train_model(new_data)
    save_model(updated_model)
    
# Use Airflow or cron job to run weekly


