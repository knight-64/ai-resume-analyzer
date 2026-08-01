#!/usr/bin/env python3
"""
AI Resume Analyzer Pro - Setup Helper
Helps with configuration and dependency installation
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class SetupHelper:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend"
        self.env_file = self.backend_dir / ".env"
    
    def print_header(self, text):
        print("\n" + "="*60)
        print(f"  {text}")
        print("="*60 + "\n")
    
    def print_step(self, num, text):
        print(f"[{num}] {text}")
    
    def print_success(self, text):
        print(f"✅ {text}")
    
    def print_warning(self, text):
        print(f"⚠️  {text}")
    
    def print_error(self, text):
        print(f"❌ {text}")
    
    def check_python(self):
        """Check Python version"""
        self.print_step("1", "Checking Python version...")
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            self.print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
            return True
        else:
            self.print_error(f"Python 3.8+ required, found {version.major}.{version.minor}")
            return False
    
    def check_venv(self):
        """Check or create virtual environment"""
        self.print_step("2", "Checking virtual environment...")
        venv_path = self.backend_dir / "venv"
        
        if venv_path.exists():
            self.print_success("Virtual environment found")
            return True
        
        print("Creating virtual environment...")
        try:
            subprocess.run(
                [sys.executable, "-m", "venv", str(venv_path)],
                check=True
            )
            self.print_success("Virtual environment created")
            return True
        except subprocess.CalledProcessError as e:
            self.print_error(f"Failed to create virtual environment: {e}")
            return False
    
    def install_dependencies(self):
        """Install Python dependencies"""
        self.print_step("3", "Installing dependencies...")
        
        req_file = self.backend_dir / "requirements.txt"
        if not req_file.exists():
            self.print_error("requirements.txt not found")
            return False
        
        # Determine pip command based on OS
        if sys.platform == "win32":
            pip_cmd = [str(self.backend_dir / "venv" / "Scripts" / "pip.exe")]
        else:
            pip_cmd = [str(self.backend_dir / "venv" / "bin" / "pip")]
        
        try:
            subprocess.run(
                pip_cmd + ["install", "-r", str(req_file)],
                check=True
            )
            self.print_success("Dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            self.print_error(f"Failed to install dependencies: {e}")
            return False
    
    def check_env_file(self):
        """Check .env file and provide guidance"""
        self.print_step("4", "Checking .env configuration...")
        
        if not self.env_file.exists():
            self.print_error(".env file not found")
            return False
        
        self.print_success(".env file found")
        
        # Check for required fields
        with open(self.env_file, 'r') as f:
            content = f.read()
        
        required_fields = [
            "SUPABASE_URL",
            "SUPABASE_KEY",
            "JWT_SECRET",
            "STRIPE_PUBLIC_KEY",
            "STRIPE_SECRET_KEY"
        ]
        
        missing_fields = []
        for field in required_fields:
            if f"{field}=" in content:
                value = content.split(f"{field}=")[1].split('\n')[0].strip()
                if value.startswith("your_") or value.startswith("pk_test_") or not value:
                    missing_fields.append(field)
        
        if missing_fields:
            self.print_warning(f"Missing or placeholder values for: {', '.join(missing_fields)}")
            return False
        
        self.print_success("All required .env fields are configured")
        return True
    
    def test_imports(self):
        """Test if all imports are available"""
        self.print_step("5", "Testing imports...")
        
        required_packages = [
            "fastapi",
            "uvicorn",
            "pydantic",
            "dotenv",
            "supabase",
            "stripe",
            "jwt",
            "bcrypt",
            "pypdf",
        ]
        
        failed = []
        for package in required_packages:
            try:
                __import__(package)
                print(f"  ✓ {package}")
            except ImportError:
                print(f"  ✗ {package}")
                failed.append(package)
        
        if failed:
            self.print_error(f"Missing packages: {', '.join(failed)}")
            return False
        
        self.print_success("All imports successful")
        return True
    
    def generate_jwt_secret(self):
        """Generate a new JWT secret"""
        print("\nGenerating JWT secret...")
        try:
            import secrets
            secret = secrets.token_urlsafe(32)
            self.print_success(f"New JWT secret: {secret}")
            
            # Offer to save to .env
            response = input("\nSave to .env? (y/n): ").strip().lower()
            if response == 'y':
                with open(self.env_file, 'r') as f:
                    content = f.read()
                
                # Replace or add JWT_SECRET
                if "JWT_SECRET=" in content:
                    content = content.replace(
                        content.split("JWT_SECRET=")[1].split('\n')[0],
                        secret
                    )
                else:
                    content += f"\nJWT_SECRET={secret}"
                
                with open(self.env_file, 'w') as f:
                    f.write(content)
                
                self.print_success("JWT_SECRET saved to .env")
        except Exception as e:
            self.print_error(f"Failed to generate JWT secret: {e}")
    
    def show_next_steps(self):
        """Show next steps"""
        self.print_header("🎉 Setup Complete!")
        
        print("Next steps:")
        print("1. Update backend/.env with your Supabase credentials:")
        print("   - SUPABASE_URL")
        print("   - SUPABASE_KEY")
        print()
        print("2. Update backend/.env with Stripe credentials:")
        print("   - STRIPE_PUBLIC_KEY")
        print("   - STRIPE_SECRET_KEY")
        print("   - STRIPE_STARTER_PRICE_ID")
        print("   - STRIPE_PRO_PRICE_ID")
        print("   - STRIPE_WEBHOOK_SECRET")
        print()
        print("3. Start the backend server:")
        print("   cd backend")
        if sys.platform == "win32":
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        print("   python run.py")
        print()
        print("4. Update index.html with your Stripe public key")
        print()
        print("5. Open http://127.0.0.1:8888 in your browser")
        print()
        print("📚 For detailed setup: Read SETUP_GUIDE.md")
        print("⚡ For quick reference: Read QUICK_REFERENCE.md")
    
    def run(self):
        """Run all setup checks"""
        self.print_header("AI Resume Analyzer Pro - Setup Helper")
        
        print("This script will:")
        print("1. Check Python version")
        print("2. Create/check virtual environment")
        print("3. Install dependencies")
        print("4. Check .env configuration")
        print("5. Test imports")
        print()
        
        if not input("Continue? (y/n): ").strip().lower() == 'y':
            print("Setup cancelled")
            return
        
        # Run checks
        checks = [
            ("Python", self.check_python),
            ("Virtual Environment", self.check_venv),
            ("Dependencies", self.install_dependencies),
            (".env Configuration", self.check_env_file),
            ("Imports", self.test_imports),
        ]
        
        passed = 0
        for name, check_fn in checks:
            try:
                if check_fn():
                    passed += 1
                else:
                    self.print_warning(f"{name} check incomplete")
            except Exception as e:
                self.print_error(f"{name} check failed: {e}")
        
        print(f"\n{passed}/{len(checks)} checks passed")
        
        # Ask about JWT secret
        if passed >= 3:
            response = input("\nGenerate new JWT secret? (y/n): ").strip().lower()
            if response == 'y':
                self.generate_jwt_secret()
        
        # Show next steps
        if passed >= 4:
            self.show_next_steps()
        else:
            self.print_warning("Setup incomplete. Please check errors above.")


if __name__ == "__main__":
    helper = SetupHelper()
    helper.run()
