"""
Vercel serverless function entry point
"""
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.api.main import app

# This is the entry point for Vercel
handler = app
