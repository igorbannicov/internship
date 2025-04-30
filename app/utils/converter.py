import subprocess
import os

def convert_pptx_to_pdf(input_path, output_dir):
    try:
        subprocess.run([
            "libreoffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir,
            input_path
        ], check=True)
        filename = os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
        return filename
    except Exception as e:
        print("Conversion failed:", e)
        return None
