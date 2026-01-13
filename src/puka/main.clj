(ns puka.main
  (:require [com.stuartsierra.component :as component]
            [reitit.ring :as ring]
            [ring.adapter.jetty :refer [run-jetty]]
            [ring.util.response :as resp]
            [puka.models.core :refer [database-component]]
            [puka.controllers.core :as controller])
  (:gen-class))

(defrecord Application [config    ; config
                        database  ; dependency
                        state]    ; state
  component/Lifecycle
  (start [this]
    (assoc this :state "Running"))
  (stop [this]
    (assoc this :state "Stopped")))

(defn application-component
  [config]
  (component/using (map->Application {:config config})
                   [:database]))

(defn render-middleware
  [handler]
  (fn [request]
    (let [resp (handler request)]
      (if (resp/response? resp)
        resp
        (#'controller/render-page resp)))))

(defn application-middleware
  [handler application]
  (fn [request]
    (handler (assoc request :application/component application))))

(defn application-handler [application]
  (ring/ring-handler
   (ring/router
    ["/"  #'controller/default]
    {:data {:middleware [[render-middleware]
                         [application-middleware application]]}})
   (ring/create-default-handler
    {:not-found (constantly {:status 404 :body "Not found"})})))

(defrecord WebServer [handler-fn port         ; parameters
                      application             ; dependencies
                      http-server shutdown]   ; state
  component/Lifecycle
  (start [this]
    (if http-server
      this
      (assoc this
             :http-server (run-jetty (handler-fn application)
                                     {:port port :join? false})
             :shutdown (promise))))

  (stop [this]
    (if http-server
      (do
        (.stop http-server)
        (deliver shutdown true)
        (assoc this :http-server nil))
      this)))

(defn web-server-component
  [handler-fn port]
  (component/using (map->WebServer {:handler-fn handler-fn :port port})
                   [:application]))

(defn new-system
  ([port] (new-system port true))
  ([port repl]
   (component/system-map :application (application-component {:repl repl})
                         :database (database-component)
                         :web-server (web-server-component #'application-handler port))))
(comment
  (def system (new-system 8888))
  (alter-var-root #'system component/start)
  (alter-var-root #'system component/stop))

(defn -main
  [& [port]]
  (let [port (or port (get (System/getenv) "PORT" 8080))
        port (cond-> port (string? port) Integer/parseInt)]
    (println (format "Listening on http://localhost:%d" port))
    (-> (component/start (new-system port false))
        :web-server :shutdown deref))) ; wait "forever" on the promise created:

