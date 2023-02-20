from argparse import ArgumentParser
from pathlib import Path
import jinja2

env = jinja2.Environment()

base_cmakelist_template = env.from_string(
    "cmake_minimum_required(VERSION 3.12)\n"
    "project({{project}})\n"
    "set(CMAKE_CXX_STANDARD 20)\n"
    "set(CMAKE_EXPORT_COMPILE_COMMANDS ON)\n\n"
    "find_package(SFML 2.5 COMPONENTS graphics REQUIRED)\n\n"
)

base_cmakelist_exe_modifier_template = env.from_string(
    "add_subdirectory({{exe}})\n\n"
)

build_script = \
    "#!/bin/bash\n\n\n" \
    "cmake -S . -B build\n" \
    "cmake --build build\n" \

exe_cmakelist_template = env.from_string(
    "add_executable({{exe}} main.cpp)\n\n"
    "target_link_libraries({{exe}} LINK_PUBLIC sfml-graphics)\n\n"
)

exe_main_cpp = \
    "#include <SFML/Graphics.hpp>\n\n" \
    "int main()\n" \
    "{\n" \
    "   // create the window\n" \
    "   sf::RenderWindow window(sf::VideoMode(800, 600), \"My window\");\n\n" \
    "   // run the program as long as the window is open\n" \
    "   while (window.isOpen())\n" \
    "   {\n" \
    "       // check all the window's events that were triggered since the last iteration of the loop\n" \
    "       sf::Event event;\n" \
    "       while (window.pollEvent(event))\n" \
    "       {\n" \
    "           // \"close requested\" event: we close the window\n" \
    "           if (event.type == sf::Event::Closed)\n" \
    "               window.close();\n" \
    "       }\n\n" \
    "       // clear the window with black color\n" \
    "       window.clear(sf::Color::Black);\n\n" \
    "       // draw everything here...\n" \
    "       // window.draw(...);\n\n" \
    "       // end the current frame\n" \
    "       window.display();\n" \
    "   }\n\n" \
    "   return 0;\n" \
    "}\n\n"

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

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("destination")
    parser.add_argument("--project", help="if provided, will be used as project name, otherwise destination is used.")
    parser.add_argument("--exe", help="if provided, will be used as executable folder name.")

    main(parser.parse_args())
