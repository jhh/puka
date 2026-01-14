(ns puka.layouts.base
  (:require [borkdude.html :refer [html]]))

(defn header
  [title]
  #html [:head
         [:meta {:charset "UTF-8"}]
         [:meta {:name "viewport" :content "width=device-width, initial-scale=1"}]
         [:title  title]
         [:link {:rel "icon" :href "/assets/favicon.ico" :sizes "any"}]
         [:link {:rel "icon" :href "/assets/favicon.svg" :type "image/svg+xml"}]
         [:link {:rel "apple-touch-icon" :href "/assets/icon-512.png"}]
         [:link {:rel "manifest" :href "/assets/manifest.webmanifest"}]
         [:link {:rel "preconnect" :href "https://rsms.me/"}]
         [:link {:rel "stylesheet" :href "https://rsms.me/inter/inter.css"}]
         [:link {:rel "stylesheet" :href "/assets/puka/main.css"}]
         [:script {:defer true :src "/assets/puka/main.js"}]])

(defn layout
  [{:keys [title content]
    :or {title ""
         content #html [:p [:strong "No content available!"]]}}]
  (html [:<>
         [:$ "<!DOCTYPE html>"]
         [:html {:lang "en"}
          (#'header title)
          [:body
           [:main
            (if (string? content)
              #html [:p content]
              content)]]]]))
