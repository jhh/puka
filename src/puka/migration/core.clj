(ns puka.migration.core
  (:require [migratus.core :as migratus]))

(def config {:store :database
             :migration-dir "migrations/"
             :db {:dbtype "postgresql"
                  :dbname "puka-test"}})

(comment
; apply pending migrations
  (migratus/migrate config)

; rollback the migration with the latest timestamp
  (migratus/rollback config)

; create migration files
  (migratus/create config "create-bookmarks")
  (migratus/create config "import-bookmarks" :edn)
;
  )
