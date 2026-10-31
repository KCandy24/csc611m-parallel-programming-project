from src.ocr_manager import OCR_Manager
from src.shared import CONFIG_PATH
from util.read_config import read_config
from util.report import generate_report


def main():
    image_dir, n_workers = read_config(CONFIG_PATH)
    labels = image_dir / "labels.csv"
    print(f"image_dir={image_dir}")
    print(f"n_workers={n_workers}")

    mt_manager = OCR_Manager(image_dir= image_dir, n_workers= n_workers)
    mt_file, mt_time = mt_manager.dispatch_workers()

    st_manager = OCR_Manager(image_dir= image_dir, n_workers= 1)
    st_file, st_time = st_manager.dispatch_workers()

    generate_report(
                    st_time= st_time, mt_time= mt_time,
                    n_workers= n_workers, 
                    st_file= st_file, mt_file= mt_file, 
                    data_dir= image_dir)

if __name__ == "__main__":
    main()
