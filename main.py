import subprocess

if __name__ == "__main__":

    # Run all preparation stages
    subprocess.run(["dvc", "repro"])
