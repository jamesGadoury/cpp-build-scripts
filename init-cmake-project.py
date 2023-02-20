from argparse import ArgumentParser
from pathlib import Path
import jinja2

env = jinja2.Environment()

base_cmakelist_template = env.from_string(
    "cmake_minimum_required(VERSION 3.12)\n"
    "project({{project}})\n"
    "set(CMAKE_CXX_STANDARD 20)\n"
    "set(CMAKE_EXPORT_COMPILE_COMMANDS ON)\n"
)

base_cmakelist_exe_modifier_template = env.from_string(
    "add_subdirectory({{exe}})\n"
)

exe_cmakelist_template = env.from_string(
    "add_executable({{exe}} main.cpp)\n"
)

exe_main_cpp = "#include <iostream>\n\n" \
               "using namespace std;\n\n" \
               "int main() {\n" \
               "    cout << \"hello world\" << endl;\n" \
               "}\n"

def main(args):
    destination = Path(args.destination)
    project = args.project if args.project is not None else destination.name

    if destination.exists():
        print("Can't initialize a project in a folder that already exists!")
        return

    destination.mkdir(parents=True)

    base_cmakelist = destination / "CMakeLists.txt"

    with open(base_cmakelist, "w") as f:
        f.write(base_cmakelist_template.render(project=project))

    exe = args.exe if args.exe else "src"
    exe_dir = destination / exe
    exe_dir.mkdir(parents=True)

    with open(base_cmakelist, "a") as f:
        f.write(base_cmakelist_exe_modifier_template.render(exe=exe))

    with open(exe_dir / "CMakeLists.txt", "w") as f:
        f.write(exe_cmakelist_template.render(exe=exe))
    
    with open(exe_dir / "main.cpp", "w") as f:
        f.write(exe_main_cpp)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("destination")
    parser.add_argument("--project", help="if provided, will be used as project name, otherwise destination is used.")
    parser.add_argument("--library", help="if provided, it will initialize a library subfolder.")
    parser.add_argument("--exe", help="if provided, it will initialize an executable subfolder.")

    main(parser.parse_args())
