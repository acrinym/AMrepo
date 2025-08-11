#!/usr/bin/env python3
"""
suppress_warnings.py — Suppress annoying protobuf warnings from TensorFlow.
"""

import warnings
import os

def suppress_protobuf_warnings():
    """Suppress protobuf version mismatch warnings."""
    # Suppress protobuf warnings
    warnings.filterwarnings('ignore', message='.*protobuf.*')
    warnings.filterwarnings('ignore', message='.*Protobuf.*')
    
    # Set environment variable to suppress protobuf warnings
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    
    # Suppress specific protobuf warnings
    try:
        import tensorflow as tf
        tf.get_logger().setLevel('ERROR')
    except ImportError:
        pass

if __name__ == "__main__":
    suppress_protobuf_warnings()
    print("Protobuf warnings suppressed. You can now run your analysis without the annoying warnings.")
