# AGENTS.md - Coding Agent Guidelines for puka-clojure

## Project Overview

Puka is a home management web application built with:

- **Clojure 1.12.4** (JVM, not ClojureScript)
- **Component** - Stuart Sierra's dependency injection/lifecycle library
- **Ring/Reitit** - HTTP server and routing
- **next.jdbc** - Modern JDBC wrapper for PostgreSQL
- **borkdude/html** - Hiccup-style HTML templating

When you need to search docs, use `context7` tools.

## Build/Run Commands

```bash
# Run the application
clojure -M -m puka.main

# Run all tests
clojure -T:build test

# Run a single test namespace
clojure -X:test cognitect.test-runner.api/test :nses '[puka.main-test]'

# Run a single test by name
clojure -X:test cognitect.test-runner.api/test :vars '[puka.main-test/a-test]'

# Build uberjar (includes tests)
clojure -T:build ci

# Lint with clj-kondo
clj-kondo --lint src test
```

### REPL Development

```clojure
(require 'puka.main)
(in-ns 'puka.main)
(def system (new-system 8888))
(alter-var-root #'system component/start)
;; To stop: (alter-var-root #'system component/stop)
```

## Project Structure

```text
src/puka/
├── main.clj              # Entry point, Component system, web server
├── controllers/core.clj  # HTTP request handlers
├── layouts/core.clj      # HTML views (hiccup-style)
└── models/
    ├── core.clj          # Database component
    └── bookmark.clj      # Bookmark model/queries
test/puka/
└── main_test.clj         # Tests (clojure.test)
```

## Code Style Guidelines

### Namespace Declarations

```clojure
(ns puka.example
  (:require [com.stuartsierra.component :as component]
            [next.jdbc :as jdbc]
            [next.jdbc.result-set :as rs]
            [honey.sql :as hsql]
            [puka.models.core :refer [database-component]])
  (:import [com.zaxxer.hikari HikariDataSource]
           [org.postgresql.util PGobject]))
```

- Prefer `:as` for aliasing, use `:refer` sparingly
- Never use `:use`
- Only add `:gen-class` in main namespace
- Put `:import` after `:require` for Java classes
- Align require clauses for readability

### Naming Conventions

| Type | Convention | Example |
| ----------- | ---------- | -------- |
| Functions | kebab-case | `get-bookmarks`, `render-page` |
| Records | PascalCase | `Application`, `Database` |
| Keywords | kebab-case | `:database`, `:builder-fn` |
| Namespaces | kebab-case | `puka.models.bookmark` |

### Function Visibility

```clojure
;; Public - use defn
(defn application-component [config]
  (component/using (map->Application {:config config}) [:database]))

;; Private - use defn- or ^:private
(defn- helper-fn [x] (process x))
(def ^:private internal-config {:setting "value"})
```

### Component Pattern

```clojure
(defrecord MyComponent [config dependency state]
  component/Lifecycle
  (start [this] (assoc this :state (initialize config)))
  (stop [this] (cleanup state) (assoc this :state nil)))

(defn my-component [config]
  (component/using (map->MyComponent {:config config}) [:dependency]))
```

### Database Access

```clojure
;; Direct SQL queries with next.jdbc
(defn get-items [db limit]
  (jdbc/execute! (db)
                 ["SELECT * FROM items LIMIT ?" limit]
                 {:builder-fn rs/as-unqualified-maps}))

;; HoneySQL for complex queries
(defn get-items-complex [db & {:keys [active offset limit]
                                :or {offset 0 limit 25}}]
  (let [query {:select [:*]
               :from [:items]
               :where [:= :active active]
               :offset offset
               :limit limit}]
    (jdbc/execute! (db) (hsql/format query) {:builder-fn rs/as-unqualified-maps})))
```

Note: Database component is callable - use `(db)` to get datasource.

**Builder functions:**
- `rs/as-unqualified-maps` - column names without table prefix
- `rs/as-kebab-maps` - converts snake_case to kebab-case keys

### HTML/Views

```clojure
;; Using borkdude/html with hiccup syntax
(defn render-page [title content]
  (html [:html [:head [:title title]] [:body content]]))

;; Reader literal syntax for inline HTML
(defn view [request]
  (assoc-in request [:params :content] 
            #html [:p [:strong "Hello!"]]))
```

### Error Handling

```clojure
;; Use ex-info for structured errors
(when-not (valid? input)
  (throw (ex-info "Validation failed" {:input input :reason "..."})))

;; Defensive checks in lifecycle methods
(defn start [this]
  (if http-server
    this  ; already started, return as-is
    (assoc this :http-server (start-server config))))

;; Safe cleanup with when/some->
(defn stop [this]
  (when datasource
    (.close datasource))
  (assoc this :datasource nil))
```

### REPL Comment Blocks

```clojure
(comment
  (require '[puka.main])
  (def db (-> puka.main/system :application :database))
  (get-bookmarks db 5))
```

### File Organization (top-down)

1. Namespace declaration
2. Private definitions
3. Records/Protocols
4. Component constructors
5. Public API functions
6. Rich comment blocks
7. `-main` function (if applicable)

### Testing

```clojure
(ns puka.feature-test
  (:require [clojure.test :refer [deftest is testing]]
            [puka.feature :as sut]))

(deftest feature-works-test
  (testing "feature does expected thing"
    (is (= expected (sut/feature-fn input)))))
```

- Use `sut` alias for system-under-test
- File naming: `*_test.clj` (underscore in filename, hyphen in namespace)
- Keep tests simple and focused on one thing

### Common Patterns

**Threading macros:**
```clojure
;; Thread-first for data transformation
(-> request
    (assoc :key value)
    layout/render-view
    str
    resp/response
    (resp/content-type "text/html"))

;; Thread-last for collections
(->> items
     (filter active?)
     (map transform)
     (take 10))

;; Some-> for nil-safe chaining
(some-> value transform maybe-nil-fn process)
```

**Keyword arguments:**
```clojure
(defn query-items [db & {:keys [active offset limit]
                          :or {offset 0 limit 25}}]
  ;; Use keyword args for optional parameters
  (fetch-data db active offset limit))

;; Call with: (query-items db :active true :limit 50)
```

## Key Patterns

### System Assembly

```clojure
(defn new-system [port & [repl?]]
  (component/system-map
    :database (database-component)
    :application (application-component {:port port})
    :web-server (web-server-component {:port port :join? (not repl?)})))
```

### Middleware Composition

```clojure
;; Threading macros for middleware composition
(defn application-middleware [handler application]
  (fn [request]
    (handler (assoc request :application/component application))))

;; Chaining middleware with ->
(defn wrap-all [handler]
  (-> handler
      render-middleware
      (wrap-middleware-fn arg)))

;; Reitit routing with per-route middleware
(ring/router
  ["/" #'controller/default]
  {:data {:middleware [[render-middleware]
                       [application-middleware app]]}})
```

## Dependencies (deps.edn aliases)

- `:test` - Test paths and cognitect test-runner
- `:build` - Build tooling with tools.build
