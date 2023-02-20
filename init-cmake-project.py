from argparse import ArgumentParser
from pathlib import Path
import jinja2

env = jinja2.Environment()

base_cmakelist_template = env.from_string(
    "cmake_minimum_required(VERSION 3.12)\n"
    "project({{project}})\n"
    "set(CMAKE_CXX_STANDARD 20)\n"
    "set(CMAKE_EXPORT_COMPILE_COMMANDS ON)\n\n"
)

base_cmakelist_exe_modifier_template = env.from_string(
    "add_subdirectory({{exe}})\n\n"
)

base_cmakelist_lib_modifier_template = env.from_string(
    "add_subdirectory({{lib}})\n\n"
)

build_script = \
    "#!/bin/bash\n\n\n" \
    "cmake -S . -B build\n" \
    "cmake --build build\n" \

exe_cmakelist_template = env.from_string(
    "add_executable({{exe}} main.cpp)\n\n"
)

exe_cmakelist_lib_modifier_template = env.from_string(
    "target_link_libraries({{exe}} LINK_PUBLIC {{lib}})\n\n"
)

exe_main_cpp = \
    "#include <iostream>\n\n" \
    "using namespace std;\n\n" \
    "int main() {\n" \
    "    cout << \"hello world\" << endl;\n" \
    "}\n\n"

exe_main_cpp_for_lib_template = env.from_string(
    "#include <iostream>\n\n"
    "#include <{{lib}}.hpp>\n\n"
    "using namespace std;\n\n"
    "int main() {\n"
    "    cout << get_word() << endl;\n"
    "}\n\n"
)

lib_cmakelist_template = env.from_string(
    "add_library({{lib}} SHARED src/{{lib}}.cpp)\n\n"
    "target_include_directories ({{lib}} PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)\n\n"
)

lib_header = \
    "#pragma once\n\n" \
    "#include <string>\n\n" \
    "std::string get_word();\n\n"

lib_cpp_template = env.from_string(
    "#include \"{{lib}}.hpp\"\n\n"
    "std::string get_word() {\n" \
    "   return \"word\";\n" \
    "}\n\n"
)

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

    script = destination / "run_build"
    with open(script, "w") as f:
        f.write(build_script)
    script.chmod(0o0777)

    exe = args.exe if args.exe else project 
    exe_dir = destination / exe if args.exe else destination / "src"
    exe_dir.mkdir()

    with open(base_cmakelist, "a") as f:
        f.write(base_cmakelist_exe_modifier_template.render(exe=exe_dir.name))
    
    exe_cmakelist = exe_dir / "CMakeLists.txt"
    with open(exe_cmakelist, "w") as f:
        f.write(exe_cmakelist_template.render(exe=exe))
    
    exe_main = exe_dir / "main.cpp"
    with open(exe_main, "w") as f:
        f.write(exe_main_cpp)

    if args.lib:
        lib = args.lib
        lib_dir = destination / lib
        lib_dir.mkdir()

        include_dir = lib_dir / "include"
        include_dir.mkdir()

        src_dir = lib_dir / "src"
        src_dir.mkdir()

        with open(base_cmakelist, "a") as f:
            f.write(base_cmakelist_lib_modifier_template.render(lib=lib))

        with open(lib_dir / "CMakeLists.txt", "w") as f:
            f.write(lib_cmakelist_template.render(lib=lib))

        with open(include_dir / f"{lib}.hpp", "w") as f:
            f.write(lib_header)

        with open(src_dir / f"{lib}.cpp", "w") as f:
            f.write(lib_cpp_template.render(lib=lib))

        with open(exe_cmakelist, "a") as f:
            f.write(exe_cmakelist_lib_modifier_template.render(exe=exe, lib=lib))

        # we overwrite the main exe logic for example lib call
        with open(exe_main, "w") as f:
            f.write(exe_main_cpp_for_lib_template.render(lib=lib))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("destination")
    parser.add_argument("--project", help="if provided, will be used as project name, otherwise destination is used.")
    parser.add_argument("--lib", help="if provided, it will initialize a library subfolder.")
    parser.add_argument("--exe", help="if provided, will be used as executable folder name.")

    main(parser.parse_args())
