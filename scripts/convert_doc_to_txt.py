"""使用 MS Word COM 将 .doc 文件批量转换为 UTF-8 文本"""
import os
import sys
from pathlib import Path

DOC_DIR = Path(r"C:\Users\zhangsihai\Desktop\考研知识库系统\二工大804资料包\c语言各章节练习题")
OUTPUT_DIR = Path(r"C:\Users\zhangsihai\Desktop\考研知识库系统\scripts\doc_converted")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def convert_doc_to_txt(doc_path: Path, output_path: Path) -> bool:
    """Convert a single .doc file to .txt using Word COM with retries."""
    import time

    for attempt in range(3):
        try:
            import win32com.client as win32

            word = win32.Dispatch("Word.Application")
            word.Visible = False
            word.DisplayAlerts = 0

            try:
                doc = word.Documents.Open(str(doc_path), ReadOnly=True, ConfirmConversions=False)
                doc.SaveAs(str(output_path), FileFormat=7)
                doc.Close()
                return True
            except Exception as e:
                print(f"  Attempt {attempt+1} error: {e}")
                try:
                    word.Quit()
                except:
                    pass
                time.sleep(1)
            finally:
                try:
                    word.Quit()
                except:
                    pass
        except Exception as e:
            print(f"  Attempt {attempt+1} COM error: {e}")
            time.sleep(2)

    return False


def main():
    doc_files = sorted(DOC_DIR.glob("*.doc"))
    success = 0
    failed = 0

    for doc_file in doc_files:
        output_path = OUTPUT_DIR / (doc_file.stem + ".txt")
        if output_path.exists():
            print(f"SKIP (exists): {doc_file.name}")
            success += 1
            continue

        print(f"Converting: {doc_file.name} ... ", end="", flush=True)
        if convert_doc_to_txt(doc_file, output_path):
            size = output_path.stat().st_size
            print(f"OK ({size} bytes)")
            success += 1
        else:
            print("FAILED")
            failed += 1

    print(f"\nDone: {success} converted, {failed} failed")


if __name__ == "__main__":
    main()
