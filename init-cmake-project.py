from argparse import ArgumentParser
from pathlib import Path
import jinja2

env = jinja2.Environment()

TXT = "HELLO\n" \
      "I am blah."

base_cmakelist_template = env.from_string(
    "cmake_minimum_required(VERSION 3.12)\n"
    "project({{project}})\n"
    "set(CMAKE_CXX_STANDARD 20)\n"
    "set(CMAKE_EXPORT_COMPILE_COMMANDS ON)\n"
)


def main(args):
    destination = Path(args.destination)
    project = args.project if args.project is not None else destination.name

    if destination.exists():
        print("Can't initialize a project in a folder that already exists!")
        return

    destination.mkdir(parents=True)

    with open(destination / "CMakeLists.txt", "w") as f:
        f.write(base_cmakelist_template.render(project=project))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("destination")
    parser.add_argument("--project", help="if provided, will be used as project name, otherwise destination is used.")
    parser.add_argument("--library", help="if provided, it will initialize a library subfolder.")
    parser.add_argument("--executable", help="if provided, it will initialize an executable subfolder.")

    main(parser.parse_args())
