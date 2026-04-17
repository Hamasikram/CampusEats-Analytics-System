import os

DATABASE_PATH = 'database/campuseats.db'

MODELS_DIR = 'ml_models/models'
LR_MODEL_PATH = os.path.join(MODELS_DIR, 'linear_regression_model.pkl')
RF_MODEL_PATH = os.path.join(MODELS_DIR, 'random_forest_model.pkl')
SCALER_PATH = os.path.join(MODELS_DIR, 'scaler.pkl')
ENCODERS_PATH = os.path.join(MODELS_DIR, 'encoders.pkl')

PRIMARY_COLOR = "#FF6B6B"
SECONDARY_COLOR = "#4ECDC4"

LOW_RATING_THRESHOLD = 3.5
EXAM_MONTHS = [11, 12, 4, 5]
ANOMALY_THRESHOLD = 2.5
