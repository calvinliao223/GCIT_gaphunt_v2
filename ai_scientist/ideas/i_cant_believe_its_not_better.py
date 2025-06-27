import warnings
from datetime import datetime
import numpy as np
import time
import os
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from PIL import Image
import requests

warnings.filterwarnings("ignore", category=UserWarning)

from datasets import load_dataset
from huggingface_hub import login

# Only login if HF_TOKEN is available
if "HF_TOKEN" in os.environ:
    login(token=os.environ["HF_TOKEN"])

## DATASET REFERENCE

# If you want to use med mnist, you can refer to the following code:
medmnist = load_dataset("albertvillanova/medmnist-v2", "pathmnist")
# >>> medmnist.shape
# {'train': (89996, 2), 'validation': (10004, 2), 'test': (7180, 2)}

# If you want to use EuroSAT, you can refer to the following code:
eurosat = load_dataset("tanganke/eurosat")
# >>> eurosat.shape
# {'train': (21600, 2), 'test': (2700, 2), 'contrast': (2700, 2), 'gaussian_noise': (2700, 2), 'impulse_noise': (2700, 2), 'jpeg_compression': (2700, 2), 'motion_blur': (2700, 2), 'pixelate': (2700, 2), 'spatter': (2700, 2)}

# For MNIST, you can refer to the following code:
mnist = load_dataset("ylecun/mnist")
# >>> mnist.shape
# {'train': (60000, 2), 'test': (10000, 2)}

# For Fashion MNIST, you can refer to the following code:
fashion_mnist = load_dataset("zalando-datasets/fashion_mnist")
# >>> fashion_mnist.shape
# {'train': (60000, 2), 'test': (10000, 2)}

# For CIFAR10, you can refer to the following code:
cifar = load_dataset("uoft-cs/cifar10")
# >>> cifar.shape
# {'train': (50000, 2), 'test': (10000, 2)}

# For IMDB, you can refer to the following code:
imdb = load_dataset("stanfordnlp/imdb")
# >>> imdb.shape
# {'train': (25000, 2), 'test': (25000, 2), 'unsupervised': (50000, 2)}

# For Amazon Polarity Dataset, you can refer to the following code:
amazon_polarity = load_dataset("fancyzhx/amazon_polarity")
# >>> amazon_polarity.shape
# {'train': (3600000, 3), 'test': (400000, 3)}

# For Emotion, you can refer to the following code:
emotion = load_dataset("dair-ai/emotion")
# >>> emotion.shape
# {'train': (16000, 2), 'validation': (2000, 2), 'test': (2000, 2)}

# For silicone, you can refer to the following code:
silicone = load_dataset("eusip/silicone", "dyda_da", trust_remote_code=True)
# >>> silicone.shape
# {'train': (87170, 5), 'validation': (8069, 5), 'test': (7740, 5)}

# For DeepMind Math dataset, you can refer to the following code:
math_examples = load_dataset(
    "deepmind/math_dataset", "algebra__linear_1d", trust_remote_code=True
)
# >>> math_examples.shape
# {'train': (1999998, 2), 'test': (10000, 2)}

## MACHINE LEARNING MODELS REFERENCE

## Example: Simple image feature extraction using basic image statistics
def extract_image_features(image_path_or_url):
    """Extract basic statistical features from an image"""
    if image_path_or_url.startswith('http'):
        image = Image.open(requests.get(image_path_or_url, stream=True).raw).convert("RGB")
    else:
        image = Image.open(image_path_or_url).convert("RGB")

    # Convert to numpy array
    img_array = np.array(image)

    # Extract basic statistical features
    features = []
    for channel in range(3):  # RGB channels
        channel_data = img_array[:, :, channel].flatten()
        features.extend([
            np.mean(channel_data),
            np.std(channel_data),
            np.median(channel_data),
            np.min(channel_data),
            np.max(channel_data)
        ])

    return np.array(features)

# Example usage for image similarity
img_urls = [
    "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/cats.png",
    "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/cats.jpeg",
]

try:
    features1 = extract_image_features(img_urls[0])
    features2 = extract_image_features(img_urls[1])

    # Calculate cosine similarity using sklearn
    from sklearn.metrics.pairwise import cosine_similarity
    similarity_score = cosine_similarity([features1], [features2])[0][0]
    print(f"Image similarity score: {similarity_score}")
except Exception as e:
    print(f"Could not load images: {e}")
    # Use dummy features for demonstration
    features1 = np.random.rand(15)
    features2 = np.random.rand(15)

## Example: extract features from text using TF-IDF
def extract_text_features(texts, max_features=1000):
    """Extract TF-IDF features from text"""
    vectorizer = TfidfVectorizer(max_features=max_features, stop_words='english')
    if isinstance(texts, str):
        texts = [texts]
    features = vectorizer.fit_transform(texts)
    return features.toarray(), vectorizer

# Example usage
text = "Transformers is an awesome library!"
text_features, vectorizer = extract_text_features([text])
print(f"Text feature shape: {text_features.shape}")
embed = text_features[0]  # Get features for the first (and only) text


## MACHINE LEARNING CLASSIFICATION EXAMPLE

# Configuration for CPU-based machine learning
IMAGE_SIZE = 84
DATASET_NAME = "mini-imagenet"
DATASET = "timm/mini-imagenet"
TEST_SIZE = 0.2
RANDOM_STATE = 42

def preprocess_image_for_ml(image, size=(IMAGE_SIZE, IMAGE_SIZE)):
    """Convert PIL image to feature vector for traditional ML"""
    if isinstance(image, str):
        # If it's a path, load the image
        image = Image.open(image)

    # Resize and convert to RGB
    image = image.convert("RGB").resize(size)

    # Convert to numpy array and flatten
    img_array = np.array(image)

    # Extract features: flatten + basic statistics
    flattened = img_array.flatten()

    # Add statistical features
    stats = []
    for channel in range(3):
        channel_data = img_array[:, :, channel]
        stats.extend([
            np.mean(channel_data),
            np.std(channel_data),
            np.median(channel_data),
            np.min(channel_data),
            np.max(channel_data)
        ])

    # Combine flattened pixels with statistical features
    features = np.concatenate([flattened, stats])
    return features

# Load dataset (using a smaller, more manageable dataset for CPU processing)
try:
    # Try to load the dataset, but handle gracefully if not available
    print("Loading dataset...")
    train_dataset_hf = load_dataset(DATASET, split="train", trust_remote_code=True)
    val_dataset_hf = load_dataset(DATASET, split="validation", trust_remote_code=True)
    test_dataset_hf = load_dataset(DATASET, split="test", trust_remote_code=True)
    print(f"Dataset loaded successfully")
except Exception as e:
    print(f"Could not load dataset {DATASET}: {e}")
    print("Using CIFAR-10 as fallback...")
    # Fallback to CIFAR-10 which is more commonly available
    train_dataset_hf = load_dataset("uoft-cs/cifar10", split="train")
    test_dataset_hf = load_dataset("uoft-cs/cifar10", split="test")
    val_dataset_hf = None


# 4. Prepare data for scikit-learn
def prepare_sklearn_data(dataset, max_samples=5000):
    """Convert HuggingFace dataset to sklearn format"""
    print(f"Processing dataset with {len(dataset)} samples...")

    # Limit samples for computational efficiency
    n_samples = min(len(dataset), max_samples)
    indices = np.random.choice(len(dataset), n_samples, replace=False)

    X = []
    y = []

    for i, idx in enumerate(indices):
        if i % 1000 == 0:
            print(f"Processed {i}/{n_samples} samples...")

        sample = dataset[int(idx)]
        image = sample["image"]
        label = sample["label"]

        # Extract features from image
        features = preprocess_image_for_ml(image)
        X.append(features)
        y.append(label)

    return np.array(X), np.array(y)

# Prepare training data
print("Preparing training data...")
X_train, y_train = prepare_sklearn_data(train_dataset_hf, max_samples=5000)

# Prepare test data
print("Preparing test data...")
X_test, y_test = prepare_sklearn_data(test_dataset_hf, max_samples=1000)

# If validation set exists, use it; otherwise split training data
if val_dataset_hf is not None:
    print("Preparing validation data...")
    X_val, y_val = prepare_sklearn_data(val_dataset_hf, max_samples=1000)
else:
    # Split training data
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y_train
    )

print(f"Training data shape: {X_train.shape}")
print(f"Validation data shape: {X_val.shape}")
print(f"Test data shape: {X_test.shape}")

# 5. Normalize features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)
X_test_scaled = scaler.transform(X_test)

# 6. Define and train multiple models
start_time = time.time()

# Initialize different classifiers
models = {
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE, n_jobs=-1),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=RANDOM_STATE),
    'Logistic Regression': LogisticRegression(random_state=RANDOM_STATE, max_iter=1000),
    'SVM': SVC(random_state=RANDOM_STATE, probability=True)
}

# Train and evaluate models
results = {}
best_model = None
best_score = 0

print("Training models...")
for name, model in models.items():
    print(f"\nTraining {name}...")

    # Train the model
    model.fit(X_train_scaled, y_train)

    # Evaluate on validation set
    val_pred = model.predict(X_val_scaled)
    val_accuracy = accuracy_score(y_val, val_pred)

    # Cross-validation score
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='accuracy')

    results[name] = {
        'validation_accuracy': val_accuracy,
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std(),
        'model': model
    }

    print(f"{name} - Validation Accuracy: {val_accuracy:.4f}")
    print(f"{name} - CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")

    if val_accuracy > best_score:
        best_score = val_accuracy
        best_model = model

print(f"\nBest model validation accuracy: {best_score:.4f}")


# 7. Final evaluation on test set
print("\nEvaluating on test set...")
test_pred = best_model.predict(X_test_scaled)
test_accuracy = accuracy_score(y_test, test_pred)

print(f"\nFinal Test Accuracy: {test_accuracy:.4f}")
print("\nDetailed Classification Report:")
print(classification_report(y_test, test_pred))

# 8. Save results and model performance summary
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
results_file = f"{DATASET_NAME}_results_{timestamp}.json"

# Prepare results for saving
final_results = {
    "timestamp": timestamp,
    "dataset": DATASET_NAME,
    "test_accuracy": test_accuracy,
    "best_model": type(best_model).__name__,
    "model_results": {}
}

for name, result in results.items():
    final_results["model_results"][name] = {
        "validation_accuracy": result["validation_accuracy"],
        "cv_mean": result["cv_mean"],
        "cv_std": result["cv_std"]
    }

# Save results
import json
with open(results_file, 'w') as f:
    json.dump(final_results, f, indent=2)

print(f"\nResults saved to {results_file}")

# 9. Performance summary
training_time = time.time() - start_time
print(f"\nTotal training time: {training_time:.2f} seconds")
print(f"Best model: {type(best_model).__name__}")
print(f"Best validation accuracy: {best_score:.4f}")
print(f"Final test accuracy: {test_accuracy:.4f}")

# 10. Feature importance (if available)
if hasattr(best_model, 'feature_importances_'):
    print(f"\nTop 10 most important features:")
    feature_importance = best_model.feature_importances_
    top_indices = np.argsort(feature_importance)[-10:][::-1]
    for i, idx in enumerate(top_indices):
        print(f"{i+1}. Feature {idx}: {feature_importance[idx]:.4f}")

print("\nTraining completed successfully!")
