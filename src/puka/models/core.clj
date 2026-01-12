(ns puka.models.core
  (:require [com.stuartsierra.component :as component]
            [next.jdbc.connection :as connection])
  (:import [com.zaxxer.hikari HikariDataSource]))

(def ^:private puka-db
  {:dbtype "postgresql"
   :dbname "puka-test"
   ;; HikariCP uses :username instead of :user
   ;; :username (System/getenv "PUKA_DB_USER")
   ;; :password (System/getenv "PUKA_DB_PASSWORD")
   ;; Connection pool settings
   :maximumPoolSize 10
   :minimumIdle 2
   :connectionTimeout 30000  ; 30 seconds
   :idleTimeout 600000       ; 10 minutes
   :maxLifetime 1800000})    ; 30 minutes

(defrecord Database [db-spec     ; configuration
                     datasource] ; state
  component/Lifecycle

  (start [this]
    (if datasource
      this
      (let [pool (connection/->pool HikariDataSource db-spec)]
        (assoc this :datasource pool))))

  (stop [this]
    (when datasource
      (.close datasource))
    (assoc this :datasource nil))

  ;; allow the Database component to be "called" with no arguments
  ;; to produce the underlying datasource object
  clojure.lang.IFn
  (invoke [_] datasource))

(defn database-component [] (map->Database {:db-spec puka-db}))
