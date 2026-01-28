(ns puka.controllers.bookmark
  (:require [puka.models.bookmark :as bookmark]))

(def ^:const page-size 25)

(defn default
  [request]
  (let [{:keys [tag page]} (-> request :parameters :query)
        page (or page 0)
        offset (* page page-size)
        htmx? (:htmx? request)
        db (-> request :application/component :database)
        data (bookmark/get-bookmarks db :active true :tag tag :offset offset :limit page-size)]
    (-> request
        (assoc :application/data (assoc data :page page :tag tag :htmx? htmx?))
        (assoc :application/view :bookmark/list)
        (doto tap>))))
