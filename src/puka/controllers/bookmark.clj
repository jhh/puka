(ns puka.controllers.bookmark
  (:require [puka.models.bookmark :as bookmark]))

(defn default
  [request]
  (let [db (-> request :application/component :database)]
    (-> request
        (assoc-in [:params :data] (bookmark/get-bookmarks db :active true))
        (assoc :application/view :bookmark/list))))
