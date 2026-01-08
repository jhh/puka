(ns puka.models.bookmark
  (:require
   [next.jdbc.sql :as sql]
   [next.jdbc.result-set :as result-set]))

(defn get-bookmarks
  [db limit]
  (sql/query (db)
             ["
  SELECT title, url, created
  FROM bookmarks_bookmark
  ORDER BY created
  "]
             {:max-rows limit
              :builder-fn result-set/as-kebab-maps}))

(comment
  (require '[puka.main])
  (def db (-> puka.main/system :application :database)) ; system must be started first
  (get-bookmarks db 5))
