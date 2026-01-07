(ns puka.main
  (:require [com.stuartsierra.component :as component]
            [reitit.ring :as ring]
            [ring.adapter.jetty :refer [run-jetty]]
            [puka.models.core :refer [setup-database]])
  (:gen-class))

(defrecord Application [config    ; config
                        database  ; dependency
                        state]    ; state
  component/Lifecycle
  (start [this]
    (assoc this :state "Running"))
  (stop [this]
    (assoc this :state "Stopped")))

(defn my-application
  [config]
  (component/using (map->Application {:config config})
                   [:database]))

(defn hello [_]
  {:status 200
   :headers {"Content-Type" "text/plain"}
   :body "Hello, Jeff!"})

(defn my-handler [_application]
  (ring/ring-handler
   (ring/router
    ["/" {:get {:handler #'hello}}])
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

(defn web-server
  [handler-fn port]
  (component/using (map->WebServer {:handler-fn handler-fn :port port})
                   [:application]))

(defn new-system
  ([port] (new-system port true))
  ([port repl]
   (component/system-map :application (my-application {:repl repl})
                         :database (setup-database)
                         :web-server (web-server #'my-handler port))))
(comment
  (def system (new-system 8888))
  (alter-var-root #'system component/start)
  (alter-var-root #'system component/stop))

(defn -main
  [& [port]]
  (let [port (or port (get (System/getenv) "PORT" 8080))
        port (cond-> port (string? port) Integer/parseInt)]
    (println "Starting up on port" port)
    (-> (component/start (new-system port false))
        :web-server :shutdown deref))) ; wait "forever" on the promise created:

(comment
  (def db (-> system :application :database :datasource))
  (require '[next.jdbc :as jdbc])
  (jdbc/execute! db ["select * from bookmarks_bookmark limit 3"]))
