import subprocess
import sys

def install_pyngrok():
    """Install pyngrok using pip programmatically."""
    print("⬇️ Installing pyngrok...")

    try:
        # Run the pip install command
        subprocess.check_call([sys.executable, "-m", "pip", "install", "waitress"])
        print("\n✅ pyngrok installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Installation failed: {e}")
        print("Try running this script as Administrator or check your internet connection.")
    except Exception as e:
        print(f"\n⚠️ Unexpected error: {e}")

if __name__ == "__main__":
    install_pyngrok()
