import os
import subprocess

if __name__ == "__main__":
    """
    This approach is used to automatically add the project directory to `PYTHONPATH`.

    It is possible to add the project directory to `PYTHONPATH` manually
     and run `dvc repro` in the terminal.
    """

    # Run all preparation stages
    env = {"PYTHONPATH": os.getcwd(), **os.environ}
    subprocess.run(["dvc", "repro"], env=env)
