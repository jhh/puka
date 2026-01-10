(ns puka.migration.import-data
  (:require
   [next.jdbc :as jdbc]
   [next.jdbc.sql :as sql]
   [next.jdbc.result-set :as rs]))

(def db-source-spec {:dbtype "postgresql" :dbname "puka"})
(def db-dest-spec {:dbtype "postgresql" :dbname "puka-test"})

(defn import-tags
  [db-source db-dest]
  (let [tags (sql/query db-source
                        ["SELECT * FROM taggit_tag"]
                        {:builder-fn rs/as-unqualified-kebab-maps})]
    (doseq [tag tags]
      (sql/insert! db-dest :tag tag))))

(defn delete-tags
  [db-dest]
  (jdbc/execute! db-dest ["TRUNCATE TABLE tag RESTART IDENTITY CASCADE"]))

(defn bookmarks-up
  [_]
  (let [db-source (jdbc/get-datasource db-source-spec)
        db-dest (jdbc/get-datasource db-dest-spec)]
    (import-tags db-source db-dest)))

(defn bookmarks-down
  [_]
  (let [db-dest (jdbc/get-datasource db-dest-spec)]
    (delete-tags db-dest)))

(comment
  (bookmarks-up nil)
  (bookmarks-down nil))
