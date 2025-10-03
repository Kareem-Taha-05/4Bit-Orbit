#!/usr/bin/env python3
"""
Aurora Prediction Script
Takes latitude and longitude as input and predicts aurora probability (0-100)
using the trained ML model (ONNX or PKL format).
"""

import sys
import json
import os
import numpy as np

def predict_aurora(latitude, longitude):
    """
    Predict aurora probability at given coordinates.
    
    Args:
        latitude (float): Latitude (-90 to 90)
        longitude (float): Longitude (-180 to 180)
    
    Returns:
        dict: Prediction results with intensity, color, and description
    """
    
    onnx_model_path = os.path.join(os.path.dirname(__file__), '..', 'ml', 'aurora_model.onnx')
    pkl_model_path = os.path.join(os.path.dirname(__file__), '..', 'ml', 'aurora_model_temp.pkl')
    
    print(f"[v0] Python script location: {os.path.abspath(__file__)}", file=sys.stderr)
    print(f"[v0] Looking for ONNX model at: {os.path.abspath(onnx_model_path)}", file=sys.stderr)
    print(f"[v0] ONNX model exists: {os.path.exists(onnx_model_path)}", file=sys.stderr)
    print(f"[v0] Looking for PKL model at: {os.path.abspath(pkl_model_path)}", file=sys.stderr)
    print(f"[v0] PKL model exists: {os.path.exists(pkl_model_path)}", file=sys.stderr)
    
    # Try ONNX model first (preferred for production)
    if os.path.exists(onnx_model_path):
        try:
            import onnxruntime as ort
            print(f"[v0] Loading ONNX model...", file=sys.stderr)
            
            session = ort.InferenceSession(onnx_model_path)
            
            input_array = np.array([[longitude, latitude]], dtype=np.float32)
            print(f"[v0] Input array shape: {input_array.shape}, dtype: {input_array.dtype}", file=sys.stderr)
            print(f"[v0] Input values: longitude={longitude}, latitude={latitude}", file=sys.stderr)
            
            # Run inference
            result = session.run(None, {"float_input": input_array})
            probability = float(result[0][0])
            
            print(f"[v0] ONNX prediction successful: {probability}", file=sys.stderr)
            
            # Ensure probability is in valid range
            probability = max(0, min(100, probability))
            
            # Generate description based on probability and location
            description = generate_description(probability, latitude)
            color = get_aurora_colors(probability)
            
            return {
                'success': True,
                'prediction': {
                    'intensity': round(probability, 2),
                    'color': color,
                    'description': description,
                    'latitude': latitude,
                    'longitude': longitude
                },
                'model_type': 'ONNX'
            }
            
        except ImportError:
            print(f"[v0] onnxruntime not installed, trying PKL model...", file=sys.stderr)
        except Exception as e:
            print(f"[v0] Error loading ONNX model: {str(e)}, trying PKL model...", file=sys.stderr)
    
    # Try PKL model as backup
    if os.path.exists(pkl_model_path):
        try:
            import pickle
            print(f"[v0] Loading PKL model...", file=sys.stderr)
            
            with open(pkl_model_path, 'rb') as f:
                model = pickle.load(f)
            
            # Prepare input features [latitude, longitude]
            features = np.array([[latitude, longitude]])
            
            # Make prediction (0-100 scale)
            probability = model.predict(features)[0]
            
            print(f"[v0] PKL prediction successful: {probability}", file=sys.stderr)
            
            # Ensure probability is in valid range
            probability = max(0, min(100, probability))
            
            # Generate description based on probability and location
            description = generate_description(probability, latitude)
            color = get_aurora_colors(probability)
            
            return {
                'success': True,
                'prediction': {
                    'intensity': round(probability, 2),
                    'color': color,
                    'description': description,
                    'latitude': latitude,
                    'longitude': longitude
                },
                'model_type': 'PKL'
            }
            
        except Exception as e:
            print(f"[v0] Error loading PKL model: {str(e)}, using fallback...", file=sys.stderr)
    
    # Fallback if no models available
    print(f"[v0] No models found, using fallback prediction", file=sys.stderr)
    return fallback_prediction(latitude, longitude)

def fallback_prediction(latitude, longitude):
    """
    Fallback prediction when model is not available.
    Uses simple latitude-based heuristic.
    """
    abs_lat = abs(latitude)
    
    # Aurora probability increases with latitude
    if abs_lat > 65:
        probability = 60 + (abs_lat - 65) * 2
    elif abs_lat > 55:
        probability = 30 + (abs_lat - 55) * 3
    elif abs_lat > 45:
        probability = 10 + (abs_lat - 45) * 2
    else:
        probability = max(0, abs_lat / 5)
    
    # Add some randomness for realism
    probability = min(100, probability + np.random.uniform(-5, 5))
    
    description = generate_description(probability, latitude)
    color = get_aurora_colors(probability)
    
    return {
        'success': True,
        'prediction': {
            'intensity': round(probability, 2),
            'color': color,
            'description': description,
            'latitude': latitude,
            'longitude': longitude
        },
        'note': 'Using fallback prediction - ML model not found',
        'model_type': 'Fallback'
    }

def generate_description(probability, latitude):
    """Generate human-readable description of aurora visibility."""
    abs_lat = abs(latitude)
    hemisphere = "Northern" if latitude >= 0 else "Southern"
    
    if probability > 70:
        return f"Excellent! Very high chance of seeing bright auroras in the {hemisphere} sky!"
    elif probability > 50:
        return f"Great! Strong aurora activity expected in the {hemisphere} hemisphere!"
    elif probability > 30:
        return f"Good chance of seeing auroras if skies are clear in the {hemisphere} regions!"
    elif probability > 15:
        return f"Moderate chance - auroras may be visible on the {hemisphere} horizon!"
    elif probability > 5:
        return f"Low probability - auroras unlikely but possible during strong storms!"
    else:
        return f"Very low chance from this location. Try locations closer to the poles!"

def get_aurora_colors(probability):
    """Determine aurora colors based on intensity."""
    if probability > 70:
        return "Green, Pink, Purple, and Red"
    elif probability > 50:
        return "Green, Pink, and Purple"
    elif probability > 30:
        return "Green and Pink"
    elif probability > 15:
        return "Pale Green"
    else:
        return "Faint Green (if visible)"

def main():
    """Main entry point for the script."""
    if len(sys.argv) != 3:
        print(json.dumps({
            'success': False,
            'error': 'Usage: python aurora_prediction.py <latitude> <longitude>'
        }))
        sys.exit(1)
    
    try:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
        
        # Validate coordinates
        if not (-90 <= latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        
        # Make prediction
        result = predict_aurora(latitude, longitude)
        
        # Output JSON result
        print(json.dumps(result))
        
    except ValueError as e:
        print(json.dumps({
            'success': False,
            'error': f'Invalid input: {str(e)}'
        }))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': f'Prediction failed: {str(e)}'
        }))
        sys.exit(1)

if __name__ == '__main__':
    main()
