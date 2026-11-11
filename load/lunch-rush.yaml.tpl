# PROVIDED. setup.sh turns this into load/lunch-rush.yaml with your image. It starts at 0 replicas: nobody is hungry yet.
# Scale it to start the rush:   kubectl scale -n beanie deployment/lunch-rush --replicas=3
# Each replica runs 16 threads that ask the gateway for the menu as fast as they can.
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lunch-rush
  namespace: beanie
  labels: {app: lunch-rush}
spec:
  replicas: 0
  selector:
    matchLabels: {app: lunch-rush}
  template:
    metadata:
      labels: {app: lunch-rush}
    spec:
      containers:
        - name: rush
          image: __IMAGE__
          command: ["python", "-c"]
          args:
            - |
              import threading, urllib.request
              def w():
                  while True:
                      try:
                          urllib.request.urlopen("http://gateway:8000/api/menu", timeout=5).read()
                      except Exception:
                          pass
              for _ in range(16):
                  threading.Thread(target=w, daemon=True).start()
              threading.Event().wait()
          resources:
            requests: {cpu: 200m, memory: 64Mi}
            limits: {memory: 128Mi}
          securityContext:
            runAsNonRoot: true
            allowPrivilegeEscalation: false
