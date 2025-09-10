#!/usr/bin/env python
"""
Setup script for Stationery Tracker Django application
"""
import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error in {description}: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    print("Setting up Stationery Tracker Django Application")
    print("=" * 50)
    
    # Check if Python is available
    if not run_command("python --version", "Checking Python version"):
        print("Python is not available. Please install Python 3.8 or higher.")
        return False
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing requirements"):
        print("Failed to install requirements. Please check your internet connection.")
        return False
    
    # Run migrations
    if not run_command("python manage.py makemigrations", "Creating migrations"):
        print("Failed to create migrations.")
        return False
    
    if not run_command("python manage.py migrate", "Running migrations"):
        print("Failed to run migrations.")
        return False
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("\nNext steps:")
    print("1. Create a superuser: python manage.py createsuperuser")
    print("2. Run the server: python manage.py runserver")
    print("3. Open http://127.0.0.1:8000/ in your browser")
    print("4. Access admin panel at http://127.0.0.1:8000/admin/")
    print("\nFor detailed instructions, see README.md")

if __name__ == "__main__":
    main()
