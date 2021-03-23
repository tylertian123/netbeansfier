# netbeansifier

Simple and dumb Python script that packages up Java files into a basic NetBeans project for ICS4U.

```text
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
```

## Installation

`netbeansifier` can be installed through `pip` with `pip install netbeansifier`.
Alternatively, clone this repository and run `python3 setup.py install` (`py setup.py install` on Windows).

## Usage

Once installed, the program can be invoked through `python3 -m netbeansifier` (`py -m netbeansifier` on Windows),
or directly using `netbeansify`.

### Basic Usage

For the bare minimum, you need to specify an input directory and an output directory:
```sh
netbeansify project_directory --out output_directory
```
This will generate a NetBeans project in `output_directory`, with all your files in `project_directory` in the project.

Often, you might also want to specify a project name and main class (entry point):
```sh
netbeansify project_directory --out output_directory --name MyProject --mainclass MyEntryPointClass
```

Finally, passing the `--zip` option will generate a project zip, which you can directly submit:
```sh
netbeansify project_directory --name MyProject --mainclass MyEntryPointClass --zip
```
When `--zip` is used, you can omit the output directory to only generate a zip (the output will use a temporary directory and deleted after generation).
Alternatively, if both `--out` and `--zip` are specified, both the zip and the normal project directory will be generated.

### Advanced Usage

You can use the `--precommand` and `--postcommand` options to specify a command to execute before and after the files are generated.
This can be used for purposes such as removing old archives before generation, or moving files around.

For example, suppose we want to remove the project zip before generating.
Suppose we also have an `input.txt`, which we wish to place in the project root (by default, it will be placed in the `src` folder with all the Java sources).
We can use the following command:
```shell
netbeansify project_directory --precommand "rm -f ProjectName.zip" --postcommand "mv src/input.txt ./"
```
Please note that the pre-command is executed in the **input directory**, while the post-command is executed in the **output directory**.

For more arguments, see the help message at the beginning.

## `.nbignore`

By default, `netbeansifier` will copy over all the files and directories in your input directory (excluding `.nbignore`s and `netbeansifierfile`s).
To ignore certain files, `netbeansifier` supports ignore files with `gitignore` syntax.
Files and directories matching the patterns in a `.nbignore` file will not be copied.

For example, the following `.nbignore` file ignores a Git repository and build output:
```gitignore
.git/
bin/
```

## `netbeansifierfile`

To avoid typing in all the arguments every time you run the command, you can set up a `netbeansifierfile` for your project.
When you run `netbeansify` in a directory, it will look for a file named `netbeansifierfile` in the current directory to use.
Each line in the file is a command-line argument.
The these arguments come before the arguments you specify manually on the command-line, so you can override them manually by specifying an argument again if desired.

Example `netbeansifierfile`:
```shell
# This is a comment (only works at the beginning of the line)
# Each line is a new command-line option
--name ProjectName
--mainclass MyMainClass
--sourcepath .
# Example pre-command to clean up old archives and make fresh Javadocs
# Pre-commands are executed in the source directory
--precommand rm -rf ProjectName.zip doc/ && javadoc -d doc *.java
# Example post-command to move the doc folder and other files into the correct location
# Post-commands are executed in the destination directory (project root)
--postcommand mv src/doc src/input1.txt src/input2.txt .
# Generate a zip
--zip
```

With such a setup, you can simply run `netbeansify` without giving it any arguments, since it will read them from the `netbeansifierfile`.
