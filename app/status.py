import os


def check_progress():

    try:

        with open("last_block.txt", "r") as f:
            last_block = int(f.read().strip())

        start_block = last_block - 1000
        scanned = 1000

        print("\n--- Base Alpha Radar Status ---")
        print(f"Latest scanned block : {last_block}")
        print(f"Start block          : {start_block}")
        print(f"Estimated scanned    : {scanned} blocks")
        print("--------------------------------\n")

    except FileNotFoundError:

        print("\n⚠ No scan history found.")
        print("Run the scanner first so it creates last_block.txt\n")


if __name__ == "__main__":
    check_progress()