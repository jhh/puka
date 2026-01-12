(ns puka.models.bookmark-test
  (:require [clojure.test :refer [deftest is testing]]
            [puka.models.bookmark :as sut]
            [next.jdbc :as jdbc]))

(defn mock-db
  "Creates a mock database function that returns nil (simulates db component)"
  []
  (fn [] nil))

(deftest get-bookmarks-sql-generation-test
  (testing "SQL generation with various parameter combinations"
    (let [db (mock-db)
          execute-calls (atom [])]

      ;; Mock jdbc/execute! to capture SQL instead of executing
      (with-redefs [jdbc/execute! (fn [_ sql opts]
                                    (swap! execute-calls conj {:sql sql :opts opts})
                                    [])]

        (testing "with :active true"
          (reset! execute-calls [])
          (sut/get-bookmarks db :active true)
          (let [sql (-> @execute-calls first :sql first)]
            (is (seq @execute-calls) "Should call execute!")
            (is (re-find #"WHERE b\.active = TRUE" sql)
                "Should include WHERE clause for active")))

        (testing "with :active false"
          (reset! execute-calls [])
          (sut/get-bookmarks db :active false)
          (let [sql (-> @execute-calls first :sql first)]
            (is (re-find #"WHERE b\.active = FALSE" sql)
                "Should include WHERE clause for inactive")))

        (testing "without :active parameter"
          (reset! execute-calls [])
          (sut/get-bookmarks db)
          (let [sql (-> @execute-calls first :sql first)]
            (is (nil? (re-find #"WHERE b\.active" sql))
                "Should NOT include WHERE clause when active is nil")))

        (testing "with custom offset and limit"
          (reset! execute-calls [])
          (sut/get-bookmarks db :offset 50 :limit 10)
          (let [sql-vec (-> @execute-calls first :sql)]
            (is (= 10 (second sql-vec))
                "Should use custom limit")
            (is (= 50 (nth sql-vec 2))
                "Should use custom offset")))

        (testing "with default offset and limit"
          (reset! execute-calls [])
          (sut/get-bookmarks db)
          (let [sql-vec (-> @execute-calls first :sql)]
            (is (= 25 (second sql-vec))
                "Should default to limit 25")
            (is (= 0 (nth sql-vec 2))
                "Should default to offset 0")))

        (testing "SQL structure includes all expected clauses"
          (reset! execute-calls [])
          (sut/get-bookmarks db :active true)
          (let [sql (-> @execute-calls first :sql first)]
            (is (re-find #"SELECT" sql) "Should have SELECT")
            (is (re-find #"b\.id" sql) "Should select id")
            (is (re-find #"b\.title" sql) "Should select title")
            (is (re-find #"b\.url" sql) "Should select url")
            (is (re-find #"COALESCE.*JSON_AGG" sql) "Should include JSON aggregation")
            (is (re-find #"FROM bookmark AS b" sql) "Should have FROM clause")
            (is (re-find #"LEFT JOIN tagging" sql) "Should have tagging join")
            (is (re-find #"LEFT JOIN tag" sql) "Should have tag join")
            (is (re-find #"GROUP BY" sql) "Should have GROUP BY")
            (is (re-find #"ORDER BY b\.created DESC" sql) "Should order by created desc")
            (is (re-find #"LIMIT" sql) "Should have LIMIT")
            (is (re-find #"OFFSET" sql) "Should have OFFSET")))

        (testing "JSON aggregation includes FILTER clause"
          (reset! execute-calls [])
          (sut/get-bookmarks db)
          (let [sql (-> @execute-calls first :sql first)]
            (is (re-find #"FILTER \(WHERE t\.id IS NOT NULL\)" sql)
                "Should include FILTER clause in JSON_AGG")))

        (testing "builder-fn is set correctly"
          (reset! execute-calls [])
          (sut/get-bookmarks db)
          (let [opts (-> @execute-calls first :opts)]
            (is (contains? opts :builder-fn)
                "Should pass builder-fn option")
            (is (fn? (:builder-fn opts))
                "Should be a function")))))))

(deftest get-bookmarks-parameter-combinations-test
  (testing "Various parameter combinations work without error"
    (let [db (mock-db)]
      (with-redefs [jdbc/execute! (fn [_ _ _] [])]

        (testing "no parameters (all defaults)"
          (is (= [] (sut/get-bookmarks db))
              "Should return empty result with defaults"))

        (testing "only :active"
          (is (= [] (sut/get-bookmarks db :active true))
              "Should work with only active param"))

        (testing "only :offset"
          (is (= [] (sut/get-bookmarks db :offset 10))
              "Should work with only offset param"))

        (testing "only :limit"
          (is (= [] (sut/get-bookmarks db :limit 5))
              "Should work with only limit param"))

        (testing ":active and :offset"
          (is (= [] (sut/get-bookmarks db :active true :offset 20))
              "Should work with active and offset"))

        (testing ":active and :limit"
          (is (= [] (sut/get-bookmarks db :active false :limit 50))
              "Should work with active and limit"))

        (testing "all parameters"
          (is (= [] (sut/get-bookmarks db :active true :offset 100 :limit 15))
              "Should work with all params specified"))))))
