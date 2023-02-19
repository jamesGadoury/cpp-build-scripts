from argparse import ArgumentParser
from pathlib import Path


def main(destination):
    if destination.exists():
        print("Can't initialize a project in a folder that already exists!")
        return
    
    destination.mkdir(parents=True)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("destination")

    main(Path(parser.parse_args().destination))
