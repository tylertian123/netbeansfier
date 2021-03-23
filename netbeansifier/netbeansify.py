import sys
import os
import re
import shutil
import tempfile
import subprocess
from distutils import dir_util
from typing import Any, List, Mapping, Set
import pathspec

REPLACE_PATTERN = re.compile(r"#\[(\w+)\]#")

HELP = """
Usage: netbeansify <input directory> [options]

Available Options:
    --help                  Display this help message.
    --out <dir>             Specify the output directory; if --zip is set, this is optional.
    --sourcepath <dir>      Specify the input directory (overrides the one already specified).
    --name <project_name>   Specify the project name (default: input directory name).
    --mainclass <class>     Specify the main class, including the package (default: project name).
    --sourcever <ver>       Specify the source code's compatible Java version (default: 11).
    --targetver <ver>       Specify the target's compatible Java version (default: 11).
    --jvmargs <args>        Specify additional args to pass to the JVM during execution.
    --javacargs <args>      Specify additional args to pass to javac during compilation.
    --precommand <cmd>      Specify a command to run before generating the files; the command is
                                executed in the source directory. Multiple commands can be
                                used by chaining with &&.
    --postcommand <cmd>     Specify a command to run after generating the files; the command is
                                executed in the destination directory. Multiple commands can be
                                used by chaining with &&.
    --template <dir>        Specify the template file directory (default: "template/" in the Python
                                file's directory).
    --zip                   Create a NetBeans project zip named ProjectName.zip in the current
                                directory; if this is set, --out is optional.
    --nologo                Do not include netbeanz.png in the output.

netbeansifier also supports gitignore-style ignore files.
Files named .nbignore contain patterns for files/directories that are excluded during copying.
The file itself is also ignored.

You can also make a netbeansifierfile. Each line will be treated as a command-line option.
Note: Because of the --precommand and --postcommand options, running an untrusted netbeansifierfile
could result in malicious commands being executed!
""".strip()

def main():
    """
    Main program with I/O and argument handling.
    """
    # Args to be used later
    # Items starting with # are used internally
    # Other items are used when replacing strings in the template
    args = {
        "project_name": None,
        "javac_source": "11",
        "javac_target": "11",
        "main_class": None,
        "#out": None,
        "#src": None,
        "#template": os.path.join(os.path.dirname(__file__), "template/"),
    }
    flags = set()
    # Map from long option name to arg name (in the args dict)
    long_opts = {
        "name": "project_name",
        "sourcever": "javac_source",
        "targetver": "javac_target",
        "mainclass": "main_class",
        "jvmargs": "jvm_args",
        "javacargs": "javac_args",
        "out": "#out",
        "template": "#template",
        "precommand": "#pre_command",
        "postcommand": "#post_command",
        "sourcepath": "#src",
    }
    long_flags = {"zip", "nologo"}

    # Extract command line arguments from netbeansifierfile
    cmdargs = []
    try:
        with open("./netbeansifierfile", "r") as nbconfig:
            for line in nbconfig:
                line = line.strip()
                # Comments
                if not line or line.startswith("#"):
                    continue
                # Long option
                if line.startswith("--"):
                    try:
                        # Split by space and do the two pieces separately
                        # For long options with parameters
                        i = line.index(" ")
                        option = line[:i]
                        arg = line[i + 1:]
                        cmdargs.append(option)
                        cmdargs.append(arg)
                    except ValueError:
                        cmdargs.append(line)
                # Other argument
                else:
                    cmdargs.append(line)
    except OSError:
        pass
    cmdargs.extend(sys.argv[1:])

    # Parse command line arguments
    source_path = None
    it = iter(cmdargs)
    for s in it:
        if s.startswith("--"):
            if s == "--help":
                print(HELP)
                sys.exit(0)
            try:
                arg_name = s[2:]
                # Check whether it's a flag or an argument
                if arg_name in long_flags:
                    flags.add(arg_name)
                else:
                    opt = long_opts[arg_name]
                    args[opt] = next(it)
            except KeyError:
                print("Invalid option:", s, file=sys.stderr)
                sys.exit(1)
            except StopIteration:
                print("Option", s, "needs a value", file=sys.stderr)
                sys.exit(1)
        else:
            source_path = s

    if args["#src"] is not None:
        source_path = args["#src"]
    
    if source_path is None or not os.path.isdir(source_path):
        print("Source path not provided", file=sys.stderr)
        sys.exit(1)

    if args["#out"] is None and "zip" not in flags:
        print("Destination path not provided", file=sys.stderr)
        sys.exit(1)

    # Default values
    args["project_name"] = args["project_name"] or os.path.basename(source_path)
    args["main_class"] = args["main_class"] or args["project_name"]

    # No output directory is specified - must be making a zip
    if args["#out"] is None:
        # Use a temporary directory
        with tempfile.TemporaryDirectory() as tempdir:
            # Make a temp dir inside the zip to netbeansify
            out_path = os.path.join(tempdir, args["project_name"])
            args["#out"] = out_path
            netbeansify(source_path, args, flags)
            print("Files generated successfully. Making zip file...")
            shutil.make_archive(args["project_name"], "zip", tempdir, args["project_name"])
    else:
        netbeansify(source_path, args, flags)
        if "zip" in flags:
            print("Files generated successfully. Making zip file...")
            shutil.make_archive(args["project_name"], "zip", os.path.dirname(os.path.abspath(args["#out"])), os.path.basename(args["#out"]))

    print("Done.")


def netbeansify(source_path: str, args: Mapping[str, Any], flags: Set[str]):
    """
    Generate the netbeansified project.
    """
    
    print("Netbeansify started.")
    # Make sure these paths are absolute
    source_path = os.path.abspath(source_path)
    args["#out"] = os.path.abspath(args["#out"])
    if args.get("#pre_command"):
        print("Running pre-command; output:\n")
        old_workdir = os.getcwd()
        os.chdir(source_path)
        subprocess.run(args["#pre_command"], shell=True, check=True)
        os.chdir(old_workdir)
        print("\nPre-command exited with success.")
    print("Copying template files...")
    # Copy over the template
    dir_util.copy_tree(args["#template"], args["#out"])

    print("Starting template file generation...")
    for dirpath, _, files in os.walk(args["#out"]):
        for file in files:
            file = os.path.join(dirpath, file)
            print("Generating", file)
            try:
                with open(file, "r") as f:
                    text = f.read()
                with open(file, "w") as f:
                    f.write(REPLACE_PATTERN.sub(lambda match: args.get(match.group(1), ""), text))
            except UnicodeDecodeError:
                print("File", file, "is a binary, skipping.")

    # Copy over the files
    def copy_dir(src_dir: str, dest_dir: str, ignores: List[Any]):
        ignore_file = os.path.join(src_dir, ".nbignore")
        has_ignore = False
        if os.path.exists(ignore_file):
            with open(ignore_file, "r") as f:
                ignores.append(pathspec.PathSpec.from_lines("gitwildmatch", f))
            has_ignore = True
        os.makedirs(dest_dir, exist_ok=True)
        with os.scandir(src_dir) as sdit:
            for entry in sdit:
                if entry.name == ".nbignore" or entry.name == "netbeansifierfile" or any(spec.match_file(entry.path) for spec in ignores):
                    continue
                if entry.is_file():
                    # copy the file over
                    shutil.copyfile(os.path.join(src_dir, entry.name), os.path.join(dest_dir, entry.name))
                elif entry.is_dir():
                    # Make sure that this directory is not the destination
                    if os.path.abspath(entry.path) == args["#out"]:
                        continue
                    copy_dir(os.path.join(src_dir, entry.name), os.path.join(dest_dir, entry.name), ignores)
        if has_ignore:
            ignores.pop()

    print("Template files generated. Copying source files...")
    copy_dir(source_path, os.path.join(args["#out"], "src"), [])
    print("Source files copied successfully.")
    if "nologo" not in flags:
        try:
            print("Copying logo...")
            shutil.copy(os.path.join(os.path.dirname(__file__), "netbeanz.png"), args["#out"])
        except OSError:
            print("Warning: Logo not found! This is very important!", file=sys.stderr)
    
    if args.get("#post_command"):
        print("Running post-command; output:\n")
        old_workdir = os.getcwd()
        os.chdir(args["#out"])
        subprocess.run(args["#post_command"], shell=True, check=True)
        os.chdir(old_workdir)
        print("\nPost-command exited with success.")
