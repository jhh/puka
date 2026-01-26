(ns puka.controllers.bookmark
  (:require [puka.models.bookmark :as bookmark]))

(def ^:const page-size 25)

(defn default
  [request]
  (let [{:keys [tag page]} (-> request :parameters :query)
        page (or page 0)
        offset (* page page-size)
        db (-> request :application/component :database)
        bookmarks (bookmark/get-bookmarks db :active true :tag tag :offset offset :limit page-size)]
    (-> request
        (assoc :application/data bookmarks)
        (assoc :application/view :bookmark/list)
        #_(doto tap>))))
