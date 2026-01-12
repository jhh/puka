(ns puka.models.bookmark
  (:require
   [honey.sql :as hsql]
   [next.jdbc :as jdbc]
   [next.jdbc.result-set :as rs]
   [clojure.data.json :as json])
  (:import [org.postgresql.util PGobject]))

(def <-json #(json/read-str % :key-fn keyword))

(defn <-pgobject
  "Transform PGobject containing `json` or `jsonb` value to Clojure data."
  [^PGobject v]
  (let [type  (.getType v)
        value (.getValue v)]
    (if (#{"jsonb" "json"} type)
      (some-> value <-json (with-meta {:pgtype type}))
      value)))

(extend-protocol rs/ReadableColumn
  org.postgresql.util.PGobject
  (read-column-by-label [^org.postgresql.util.PGobject v _]
    (<-pgobject v))
  (read-column-by-index [^org.postgresql.util.PGobject v _2 _3]
    (<-pgobject v)))

(defn get-bookmarks
  [db & {:keys [active offset limit]
         :or {offset 0
              limit 25}}]
  (let [base-query {:select [:b.id
                             :b.title
                             :b.url
                             :b.description
                             :b.created
                             :b.active
                             [[:coalesce
                               [:raw "JSON_AGG(JSON_BUILD_OBJECT('id', t.id, 'name', t.name, 'slug', t.slug) ORDER BY t.name) FILTER (WHERE t.id IS NOT NULL)"]
                               [:cast [:inline "[]"] :json]]
                              :tags]]
                    :from [[:bookmark :b]]
                    :left-join [[:tagging :ti] [:= :ti.taggable_id :b.id]
                                [:tag :t] [:= :t.id :ti.tag_id]]
                    :group-by [:b.id :b.title :b.url :b.description :b.created :b.modified]
                    :order-by [[:b.created :desc]]
                    :offset offset
                    :limit limit}
        query (if (some? active)
                (assoc base-query :where [:= :b.active active])
                base-query)]
    (jdbc/execute! (db) (hsql/format query) {:builder-fn rs/as-unqualified-maps})))

(comment
  (defn db [] (jdbc/get-datasource {:dbtype "postgresql" :dbname "puka-test"}))
  (time (get-bookmarks db :active true :offset 0 :limit 25))
  (time (jdbc/execute! (db) ["select * from bookmark limit 3"]))

  ;; Benchmark: run get-bookmarks 10 times and average (with paging)
  (let [iterations 20
        times (doall
               (for [i (range iterations)]
                 (let [start (System/nanoTime)
                       _ (doall (get-bookmarks db :active true :offset (* i 25) :limit 25))
                       end (System/nanoTime)]
                   (/ (- end start) 1000000.0))))
        avg (/ (reduce + times) iterations)]
    (println "Times (ms):" times)
    (println "Average:" avg "ms"))
  ;
  )

