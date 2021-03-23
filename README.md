# netbeansifier

Simple and dumb Python script that packages up Java files into a basic Netbeans project for ICS4U.

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
    --zip                   Create a Netbeans project zip named ProjectName.zip in the current
                                directory; if this is set, --out is optional.
    --nologo                Do not include netbeanz.png in the output.

netbeansifier also supports gitignore-style ignore files.
Files named .nbignore contain patterns for files/directories that are excluded during copying.
The file itself is also ignored.

You can also make a netbeansifierfile. Each line will be treated as a command-line option.
Note: Because of the --precommand and --postcommand options, running an untrusted netbeansifierfile
could result in malicious commands being executed!
```

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
--zip
```
