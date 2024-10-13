import os
import subprocess


def run_main():
    os.chdir("frontend")

    subprocess.run(["python", "main.py"])


if __name__ == "__main__":
    run_main()
