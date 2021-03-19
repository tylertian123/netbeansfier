import sys
import os
import re
import shutil
import tempfile
import subprocess
from distutils import dir_util
from typing import Any, List
import pathspec

pattern = re.compile(r"#\[(\w+)\]#")

HELP = """
Usage: python3 netbeansify.py <input directory> [options]

Available Options:
    --help
    --sourcepath    <input directory> (optional if already specified)    
    --name          <project name> (default: input directory name)
    --mainclass     <main class incl. package> (default: project name)
    --out           <output dir> (optional if using --zip)
    --template      <template dir> (default: "template/" in the Python file's directory)
    --sourcever     <source compat. java version> (default: 11)
    --targetver     <target compat. java version> (default: 11)
    --jvmargs       <additional jvm args>
    --javacargs     <additional javac args>
    --precommand    <command to run before generating the files (in the source dir)>
    --postcommand   <command to run after generating the files (in the dest dir)>
    --zip

netbeansifier supports gitignore-style ignore files.
Files named .nbignore contain patterns for files/directories that are excluded during copying.
The file itself is also ignored.

You can also make a netbeansifierfile. Each line will be treated as a command-line option.
Note: Because of the --precommand and --postcommand options, running an untrusted netbeansifierfile
could result in malicious commands being executed!
""".strip()

args = {
    "project_name": None,
    "javac_source": "11",
    "javac_target": "11",
    "main_class": None,
    "#out": None,
    "#template": os.path.join(os.path.dirname(__file__), "template/"),
}

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
}

cmdargs = []
try:
    with open("./netbeansifierfile", "r") as nbconfig:
        for line in nbconfig:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("--"):
                try:
                    i = line.index(" ")
                    option = line[:i]
                    arg = line[i + 1:]
                    cmdargs.append(option)
                    cmdargs.append(arg)
                except ValueError:
                    cmdargs.append(line)
            else:
                cmdargs.append(line)
except OSError:
    pass
cmdargs.extend(sys.argv[1:])

makezip = False
source_path = None
it = iter(cmdargs)
for s in it:
    if s.startswith("--"):
        if s == "--help":
            print(HELP)
            sys.exit(0)
        if s == "--zip":
            makezip = True
            continue
        if s == "--sourcepath":
            source_path = next(it)
            continue
        if s == "--config":
            config_path = next(it)
            continue
        try:
            opt = long_opts[s[2:]]
            args[opt] = next(it)
        except KeyError:
            print("Invalid option:", s, file=sys.stderr)
            sys.exit(1)
        except StopIteration:
            print("Option", s, "needs a value", file=sys.stderr)
            sys.exit(1)
    else:
        source_path = s

if source_path is None or not os.path.isdir(source_path):
    print("Source path not provided", file=sys.stderr)
    sys.exit(1)

if args["#out"] is None and not makezip:
    print("Destination path not provided", file=sys.stderr)
    sys.exit(1)

# Default values
args["project_name"] = args["project_name"] or os.path.basename(source_path)
args["main_class"] = args["main_class"] or args["project_name"]

def netbeansify():
    global source_path
    # Make sure these paths are absolute
    source_path = os.path.abspath(source_path)
    args["#out"] = os.path.abspath(args["#out"])
    if args.get("#pre_command"):
        print("Running pre-command...")
        old_workdir = os.getcwd()
        os.chdir(source_path)
        subprocess.run(args["#pre_command"], shell=True, check=True)
        os.chdir(old_workdir)
    # Copy over the template
    dir_util.copy_tree(args["#template"], args["#out"])

    for dirpath, _, files in os.walk(args["#out"]):
        for file in files:
            file = os.path.join(dirpath, file)
            print("Generating", file)
            try:
                with open(file, "r") as f:
                    text = f.read()
                with open(file, "w") as f:
                    f.write(pattern.sub(lambda match: args.get(match.group(1), ""), text))
            except UnicodeDecodeError:
                print("File", file, "is a binary, skipping...")

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

    print("Copying files...")
    copy_dir(source_path, os.path.join(args["#out"], "src"), [])
    try:
        shutil.copy(os.path.join(os.path.dirname(__file__), "netbeanz.png"), args["#out"])
    except OSError:
        print("Warning: Logo not found! This is very important!", file=sys.stderr)
    
    if args.get("#post_command"):
        print("Running post-command...")
        old_workdir = os.getcwd()
        os.chdir(args["#out"])
        subprocess.run(args["#post_command"], shell=True, check=True)
        os.chdir(old_workdir)


if args["#out"] is None:
    with tempfile.TemporaryDirectory() as tempdir:
        out_path = os.path.join(tempdir, args["project_name"])
        args["#out"] = out_path
        netbeansify()
        print("Making zip file...")
        shutil.make_archive(args["project_name"], "zip", tempdir, args["project_name"])
else:
    netbeansify()
    if makezip:
        print("Making zip file...")
        shutil.make_archive(args["project_name"], "zip", os.path.dirname(os.path.abspath(args["#out"])), os.path.basename(args["#out"]))


print("Done.")
