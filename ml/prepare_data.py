from dotenv import load_dotenv
import os
import pandas as pd

import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from multiprocessing import Pool, cpu_count

load_dotenv()

# ✅ Tesseract path
pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH")

# ✅ Paths
DATASET_PATH = "data/Resumes PDF"
OUTPUT_FILE = "data/resume_dataset.csv"
PROCESSED_FILES = "data/processed_files.csv"


# ⚡ FAST: Try PyMuPDF first
def extract_with_pymupdf(file_path):
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except:
        return ""

# 🧠 OCR fallback (only if needed)
def extract_with_ocr(file_path):
    try:
        images = convert_from_path(
            file_path,
            dpi=150,
            poppler_path=os.getenv("POPPLER_PATH")
        )
        text = ""
        for img in images:
            text += pytesseract.image_to_string(img)
        return text
    except:
        return ""

# 🔥 Smart extraction
def extract_text(file_path):
    text = extract_with_pymupdf(file_path)

    if text.strip() == "":
        text = extract_with_ocr(file_path)

    return text


# if os.path.exists(PROCESSED_FILES):
#     df = pd.read_csv(PROCESSED_FILES)
#     processed_file_list = df["file_path"].dropna().tolist()
# else:
#     processed_file_list = []

# ⚡ Process one file
def process_file(args):
    file_path, category = args

    if os.path.exists(PROCESSED_FILES):
        df = pd.read_csv(PROCESSED_FILES)
        processed_file_list = set(df["file_path"].dropna().tolist())
    else:
        processed_file_list = []


    if file_path in processed_file_list:
        # print(f"{file_path} skipped...")
        return None
    try:
        text = extract_text(file_path)

        if text.strip() == "":
            return None

        return {
            "resume_str": text,
            "category": category,
            "file_path": file_path
        }
    except:
        print(f"Error: {file_path}")
        return None
    
def process(files_number):
    print(f"started processing {files_number}")
    
    file_list = []

    # Collect all files
    for category in os.listdir(DATASET_PATH):
        category_path = os.path.join(DATASET_PATH, category)
        # print(category)

        if os.path.isdir(category_path):
            for file in os.listdir(category_path):
                if file.endswith(".pdf"):
                    file_list.append((os.path.join(category_path, file), category))

    print(f"Total files: {len(file_list)}")
    # return

    # ⚠️ TEST FIRST (change later)
    file_list = file_list[:files_number]

    # ⚡ Parallel processing
    with Pool(cpu_count()) as p:
        results = p.map(process_file, file_list)

    # Remove empty
    # data = [{"resume_str":r["resume_str"],"category": r["category"]} for r in results if r is not None]
    data = [{"resume_str": r.get("resume_str"), "category": r.get("category")} 
        for r in results if r]
    
    processed_files = [r.get("file_path") for r in results if r and r.get("file_path")]

    df_pf = pd.DataFrame(processed_files, columns=["file_path"])
    # df.to_csv(PROCESSED_FILES, index=False)

    df_pf.to_csv(
        PROCESSED_FILES,
        mode='a',                         # append mode
        header=not os.path.exists(PROCESSED_FILES),  # write header only if file not exists
        index=False
    )

    df_out = pd.DataFrame(data)

    df_out.to_csv(
        OUTPUT_FILE,
        mode='a',
        header=not os.path.exists(OUTPUT_FILE),
        index=False
    )
    print("✅ Dataset created!")
    print(df_out.tail())



# 🚀 MAIN
def main():
    # process(1310)
    for i in range(6900,6955,10):
        val = input("Enter Y to continue: ")
        if val== "Y" or val=="y":
            process(i)
        else:
            break

    # file_list = []

    # # Collect all files
    # for category in os.listdir(DATASET_PATH):
    #     category_path = os.path.join(DATASET_PATH, category)
    #     # print(category)

    #     if os.path.isdir(category_path):
    #         for file in os.listdir(category_path):
    #             if file.endswith(".pdf"):
    #                 file_list.append((os.path.join(category_path, file), category))

    # print(f"Total files: {len(file_list)}")

    # # ⚠️ TEST FIRST (change later)
    # file_list = file_list[:200]

    # # ⚡ Parallel processing
    # with Pool(cpu_count()) as p:
    #     results = p.map(process_file, file_list)

    # # Remove empty
    # # data = [{"resume_str":r["resume_str"],"category": r["category"]} for r in results if r is not None]
    # data = [{"resume_str": r.get("resume_str"), "category": r.get("category")} 
    #     for r in results if r]
    
    # processed_files = [r.get("file_path") for r in results if r and r.get("file_path")]

    # df_pf = pd.DataFrame(processed_files, columns=["file_path"])
    # # df.to_csv(PROCESSED_FILES, index=False)

    # df_pf.to_csv(
    #     PROCESSED_FILES,
    #     mode='a',                         # append mode
    #     header=not os.path.exists(PROCESSED_FILES),  # write header only if file not exists
    #     index=False
    # )

    # df_out = pd.DataFrame(data)

    # df_out.to_csv(
    #     OUTPUT_FILE,
    #     mode='a',
    #     header=not os.path.exists(OUTPUT_FILE),
    #     index=False
    # )
    # print("✅ Dataset created!")
    # print(df_out.head())


if __name__ == "__main__":
    main()