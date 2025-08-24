# ============================================================================
# QUICK TRAINING DATA SETUP
# ============================================================================
# Installs dependencies and generates training data
# ============================================================================

import subprocess
import sys
import os

def install_faker():
    """Install Faker package if not available"""
    try:
        import faker
        print("✅ Faker already installed")
        return True
    except ImportError:
        print("📦 Installing Faker package...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'faker'])
            print("✅ Faker installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install Faker")
            return False

def main():
    print("🚀 Setting up training data for Smart Attendance AI...")
    print("=" * 60)
    
    # Install dependencies
    if not install_faker():
        print("❌ Cannot proceed without Faker package")
        return
    
    # Generate training data
    print("\n📊 Generating training data...")
    try:
        from generate_training_data import TrainingDataGenerator
        generator = TrainingDataGenerator()
        generator.generate_all_training_data()
        
        print("\n🎉 Training data setup complete!")
        print("🤖 You can now train AI models with realistic data")
        
    except Exception as e:
        print(f"❌ Error generating training data: {e}")

if __name__ == '__main__':
    main()
