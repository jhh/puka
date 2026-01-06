# Puka

Puka is a home management app.

## Usage

Clone the repo, cd into it, then follow below to *Run the Application* or *Run
the application in REPL* or *Run the tests* or *Build an Uberjar*.

### Run the Application

```bash
clojure -M -m puka.main
```

### Run the Application in REPL

Start REPL

```bash
clj
```

Once REPL starts, start the server as an example on port 8888:

```clj
user=> (require 'puka.main)                             ; load the code
user=> (in-ns 'puka.main)                               ; move to the namespace
puka.main=> (def system (new-system 8888))              ; specify port
puka.main=> (alter-var-root #'system component/start)   ; start the server
```

### Run the Tests

```bash
clojure -T:build test
```

## Build an Uberjar

For production deployment, you typically want to build an "uberjar" -- a `.jar`
file that contains Clojure itself and all of the code from your application and
its dependencies, so that you can run it with the `java -jar` command.

The `build.clj` file -- mentioned above -- contains a `ci` task that:

* runs all the tests
* cleans up the `target` folder
* compiles the application (sometimes called "AOT compilation")
* produces a standalone `.jar` file

```bash
clojure -T:build ci
```
