# netbeansifier

Simple and dumb Python script that packages up Java files into a basic Netbeans project for ICS4U.

```text
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
