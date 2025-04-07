import sys
import os

if __name__ == "__main__":
    dir_name = sys.argv[1] if len(sys.argv) > 1 else None

    if not dir_name or not os.path.exists(dir_name):
        print("Directory not provided or does not exist")
        exit(1)

    # Get all files in the directory
    files = os.listdir(dir_name)

    for file in files:
        with open(f"{dir_name}/{file}", "r+") as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines if line.startswith("x")]

            # Write to file again only with the lines that start with "x"
            f.seek(0)
            f.writelines([f"{line}\n" for line in lines])
            f.truncate()
