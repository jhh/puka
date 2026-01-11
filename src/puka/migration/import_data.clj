(ns puka.migration.import-data
  (:require
   [clojure.set :as set]
   [next.jdbc :as jdbc]
   [next.jdbc.sql :as sql]
   [next.jdbc.result-set :as rs]))

(def db-source-spec {:dbtype "postgresql" :dbname "puka"})
(def db-dest-spec {:dbtype "postgresql" :dbname "puka-test"})

(defn import-tags
  [db-source db-dest]
  (let [tags (sql/query db-source
                        ["SELECT * FROM taggit_tag"]
                        {:builder-fn rs/as-unqualified-maps})
        total (count tags)]
    (println (format "Importing %d tags..." total))
    (doseq [[idx tag] (map-indexed vector tags)]
      (sql/insert! db-dest :tag tag)
      (when (zero? (mod (inc idx) 100))
        (println (format "Progress: %d/%d tags" (inc idx) total))))
    (println "Import of tags complete!")))

(defn delete-tags
  [_ db-dest]
  (let [count (jdbc/execute-one! db-dest ["SELECT count(*) FROM tag"])]
    (println (format "Deleting %d tags..." (:count count))))
  (jdbc/execute! db-dest ["TRUNCATE TABLE tag RESTART IDENTITY CASCADE"])
  (println "Deletion of tags complete!"))

(defn import-bookmarks
  [db-source db-dest]
  (let [bookmarks (sql/query db-source
                             ["SELECT * FROM bookmarks_bookmark"]
                             {:builder-fn rs/as-unqualified-maps})
        total (count bookmarks)]
    (println (format "Importing %d bookmarks" total))
    (doseq [[idx bookmark] (map-indexed vector bookmarks)]
      (sql/insert! db-dest :bookmark bookmark)
      (when (zero? (mod (inc idx) 100))
        (println (format "Progress: %d/%d bookmarks" (inc idx) total))))
    (println "Import of bookmarks complete!")))

(defn delete-bookmarks
  [_ db-dest]
  (let [count (jdbc/execute-one! db-dest ["SELECT count(*) FROM bookmark"])]
    (println (format "Deleting %d bookmarks..." (:count count))))
  (jdbc/execute! db-dest ["TRUNCATE TABLE bookmark RESTART IDENTITY CASCADE"])
  (println "Deletion of bookmarks complete!"))

(defn import-taggings
  [db-source db-dest]
  (let [taggings (sql/query db-source
                            ["SELECT * FROM taggit_taggeditem"]
                            {:builder-fn rs/as-unqualified-maps})
        total (count taggings)]
    (println (format "Importing %d taggings" total))
    (doseq [[idx tagging] (map-indexed vector taggings)]
      (let [tagging (dissoc tagging :content_type_id)
            tagging (assoc tagging :taggable_type (name :bookmark))
            tagging (set/rename-keys tagging {:object_id :taggable_id})]
        (sql/insert! db-dest :tagging tagging))
      (when (zero? (mod (inc idx) 100))
        (println (format "Progress: %d/%d taggings" (inc idx) total))))
    (println "Import of taggings complete!")))

(defn delete-taggings
  [_ db-dest]
  (let [count (jdbc/execute-one! db-dest ["SELECT count(*) FROM tagging"])]
    (println (format "Deleting %d taggings..." (:count count))))
  (jdbc/execute! db-dest ["TRUNCATE TABLE tagging RESTART IDENTITY CASCADE"])
  (println "Deletion of taggings complete!"))

(defn bookmarks-up
  [_]
  (let [db-source (jdbc/get-datasource db-source-spec)
        db-dest (jdbc/get-datasource db-dest-spec)]
    (import-tags db-source db-dest)
    (import-bookmarks db-source db-dest)
    (import-taggings db-source db-dest)))

(defn bookmarks-down
  [_]
  (let [db-dest (jdbc/get-datasource db-dest-spec)]
    (delete-tags nil db-dest)
    (delete-bookmarks nil db-dest)
    (delete-taggings nil db-dest)))

(comment
  (bookmarks-up nil)
  (bookmarks-down nil)
  ;
  (let [db-source (jdbc/get-datasource db-source-spec)
        db-dest (jdbc/get-datasource db-dest-spec)]
    (import-taggings db-source db-dest))
  ;
  )
