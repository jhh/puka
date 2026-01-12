(ns puka.models.core-test
  (:require [clojure.test :refer [deftest is testing]]
            [puka.models.core :as sut]
            [com.stuartsierra.component :as component])
  (:import [com.zaxxer.hikari HikariDataSource]))

(deftest database-component-test
  (testing "Database component lifecycle"
    (let [db-component (sut/database-component)]

      (testing "initial state"
        (is (nil? (:datasource db-component))
            "Datasource should be nil before start"))

      (testing "after start"
        (let [started (component/start db-component)]
          (try
            (is (some? (:datasource started))
                "Datasource should be present after start")
            (is (instance? HikariDataSource (:datasource started))
                "Datasource should be a HikariDataSource")
            (is (not (.isClosed (:datasource started)))
                "Connection pool should not be closed")

            (testing "component is callable"
              (is (= (:datasource started) (started))
                  "Calling component should return datasource"))

            (testing "idempotent start"
              (let [restarted (component/start started)]
                (is (= (:datasource started) (:datasource restarted))
                    "Starting again should not create new datasource")))

            (finally
              (component/stop started)))))

      (testing "after stop"
        (let [started (component/start db-component)
              stopped (component/stop started)]
          (is (nil? (:datasource stopped))
              "Datasource should be nil after stop")
          (is (.isClosed (:datasource started))
              "Connection pool should be closed after stop"))))))

(deftest database-component-pool-configuration-test
  (testing "HikariCP pool configuration"
    (let [db-component (sut/database-component)
          started (component/start db-component)]
      (try
        (let [^HikariDataSource datasource (:datasource started)
              config (.getHikariConfigMXBean datasource)]
          (testing "pool size settings"
            (is (= 10 (.getMaximumPoolSize config))
                "Maximum pool size should be 10")
            (is (= 2 (.getMinimumIdle config))
                "Minimum idle connections should be 2"))

          (testing "timeout settings"
            (is (= 30000 (.getConnectionTimeout config))
                "Connection timeout should be 30 seconds")
            (is (= 600000 (.getIdleTimeout config))
                "Idle timeout should be 10 minutes")
            (is (= 1800000 (.getMaxLifetime config))
                "Max lifetime should be 30 minutes")))
        (finally
          (component/stop started))))))
