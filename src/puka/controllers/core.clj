(ns puka.controllers.core
  (:require [puka.layouts.core :as layout]))

(defn render-page
  [req]
  (layout/render-page (-> req :params :message)))

(defn send-message [req] (assoc-in req [:params :message] "Hello, Clojure!"))

