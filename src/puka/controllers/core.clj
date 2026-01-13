(ns puka.controllers.core
  (:require [puka.layouts.core :as layout]))

(defn render-page
  [request]
  (layout/render-page (-> request :params :message)))

(defn default [request] (assoc-in request [:params :message] "Hello, Jeff!"))

