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
    --zip

netbeansifier supports gitignore-style ignore files.
Files named .nbignore contain patterns for files/directories that are excluded during copying.
The file itself is also ignored.

You can also make a netbeansifierfile. Each line will be treated as a command-line option.
```
