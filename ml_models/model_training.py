"""
CampusEats ML Model Training
Predicts order value using Random Forest
"""

import sqlite3
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import pickle
import os
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("="*60)
print("CampusEats ML Model Training Pipeline")
print("="*60)

# Database path
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'campuseats.db')

# ========== LOAD DATA ==========
print("\n[1/5] Loading data from database...")
conn = sqlite3.connect(db_path)

query = '''
    SELECT 
        o.order_id,
        o.student_id,
        o.stall_id,
        o.total_amount,
        o.order_date,
        o.is_exam_period,
        s.total_spending,
        st.category_id,
        COALESCE(AVG(r.rating), 3.5) as avg_stall_rating,
        COUNT(DISTINCT prev_o.order_id) as student_order_count
    FROM orders o
    JOIN students s ON o.student_id = s.student_id
    JOIN stalls st ON o.stall_id = st.stall_id
    LEFT JOIN ratings r ON o.stall_id = r.stall_id
    LEFT JOIN orders prev_o ON o.student_id = prev_o.student_id 
        AND prev_o.order_date < o.order_date
    GROUP BY o.order_id
'''

df = pd.read_sql_query(query, conn)
conn.close()
print(f"✓ Loaded {len(df)} records")

# ========== FEATURE ENGINEERING ==========
print("\n[2/5] Feature Engineering...")

df['order_date'] = pd.to_datetime(df['order_date'])

# Extract temporal features
df['hour'] = df['order_date'].dt.hour
df['day_of_week'] = df['order_date'].dt.dayofweek
df['month'] = df['order_date'].dt.month
df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
df['is_meal_time'] = ((df['hour'] >= 11) & (df['hour'] <= 14) | 
                      (df['hour'] >= 17) & (df['hour'] <= 20)).astype(int)

# Encode categorical variables
le_student = LabelEncoder()
le_stall = LabelEncoder()
le_category = LabelEncoder()

df['student_encoded'] = le_student.fit_transform(df['student_id'])
df['stall_encoded'] = le_stall.fit_transform(df['stall_id'])
df['category_encoded'] = le_category.fit_transform(df['category_id'])

# Create interaction features
df['student_stall_frequency'] = df.groupby(['student_id', 'stall_id'])['order_id'].transform('count')
df['spending_ratio'] = df['total_spending'] / (df['student_order_count'] + 1)

# Select features
feature_columns = [
    'hour', 'day_of_week', 'month', 'is_weekend', 'is_meal_time',
    'is_exam_period', 'student_encoded', 'stall_encoded', 'category_encoded',
    'total_spending', 'avg_stall_rating', 'student_order_count',
    'student_stall_frequency', 'spending_ratio'
]

X = df[feature_columns].fillna(0)
y = df['total_amount']

print(f"✓ Created {len(feature_columns)} features")
print(f"Features: {', '.join(feature_columns)}")

# ========== DATA PREPROCESSING ==========
print("\n[3/5] Data Preprocessing...")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"✓ Training set: {X_train.shape[0]} samples")
print(f"✓ Test set: {X_test.shape[0]} samples")

# ========== MODEL TRAINING ==========
print("\n[4/5] Training Models...")

# Linear Regression
print("  Training Linear Regression...")
lr_model = LinearRegression()
lr_model.fit(X_train_scaled, y_train)
lr_pred = lr_model.predict(X_test_scaled)
lr_rmse = np.sqrt(mean_squared_error(y_test, lr_pred))
lr_mae = mean_absolute_error(y_test, lr_pred)
lr_r2 = r2_score(y_test, lr_pred)

print(f"    RMSE: {lr_rmse:.2f}")
print(f"    MAE: {lr_mae:.2f}")
print(f"    R² Score: {lr_r2:.4f}")

# Random Forest
print("  Training Random Forest...")
rf_model = RandomForestRegressor(
    n_estimators=100,
    max_depth=15,
    min_samples_split=5,
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train, y_train)
rf_pred = rf_model.predict(X_test)
rf_rmse = np.sqrt(mean_squared_error(y_test, rf_pred))
rf_mae = mean_absolute_error(y_test, rf_pred)
rf_r2 = r2_score(y_test, rf_pred)

print(f"    RMSE: {rf_rmse:.2f}")
print(f"    MAE: {rf_mae:.2f}")
print(f"    R² Score: {rf_r2:.4f}")

# ========== SAVE MODELS ==========
print("\n[5/5] Saving Models...")

os.makedirs('models', exist_ok=True)

# Save models
with open('models/linear_regression_model.pkl', 'wb') as f:
    pickle.dump(lr_model, f)
print("✓ Linear Regression model saved")

with open('models/random_forest_model.pkl', 'wb') as f:
    pickle.dump(rf_model, f)
print("✓ Random Forest model saved")

with open('models/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
print("✓ Scaler saved")

with open('models/encoders.pkl', 'wb') as f:
    pickle.dump({
        'student': le_student,
        'stall': le_stall,
        'category': le_category
    }, f)
print("✓ Encoders saved")

# Feature importance
feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

print("\nTop 10 Important Features:")
print(feature_importance.head(10).to_string(index=False))

# Save metadata
metadata = {
    'training_date': datetime.now().isoformat(),
    'features': feature_columns,
    'lr_rmse': float(lr_rmse),
    'lr_mae': float(lr_mae),
    'lr_r2': float(lr_r2),
    'rf_rmse': float(rf_rmse),
    'rf_mae': float(rf_mae),
    'rf_r2': float(rf_r2),
    'training_samples': len(X_train),
    'test_samples': len(X_test)
}

with open('models/metadata.json', 'w') as f:
    json.dump(metadata, f, indent=4)
print("✓ Metadata saved")

print("\n" + "="*60)
print("✓ MODEL TRAINING COMPLETE!")
print("="*60)
print(f"\nBest Model: Random Forest (R² = {rf_r2:.4f})")
print(f"Prediction Error (MAE): ±{rf_mae:.2f} PKR")
