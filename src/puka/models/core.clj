(ns puka.models.core
  (:require [com.stuartsierra.component :as component]
            [next.jdbc :as jdbc]))

(def ^:private puka-db
  {:dbtype "postgresql" :dbname "puka"})

(defrecord Database [db-spec     ; configuration
                     datasource] ; state
  component/Lifecycle

  (start [this]
    (if datasource
      this
      (assoc this :datasource (jdbc/get-datasource db-spec))))

  (stop [this]
    (assoc this :datasource nil))

  ;; allow the Database component to be "called" with no arguments
  ;; to produce the underlying datasource object
  clojure.lang.IFn
  (invoke [_] datasource))

(defn setup-database [] (map->Database {:db-spec puka-db}))
