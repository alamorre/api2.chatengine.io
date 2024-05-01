Connecting to EKS with Kubectl

```
aws eks --region us-east-1 update-kubeconfig --name ce-cluster
kubectl get nodes
kubectl get pods --all-namespaces
```

Getting the error logs:

```
kubectl get pods  # Lists all pods in the default namespace
kubectl logs <pod-name>
kubectl get pods --selector=app=<app-label>
```

Run the ws.chatengine.io image

```
docker build -t wschatengine:latest .
docker run -p 9001:9001 \
  -e API_URL=http://127.0.0.1:8000 \
  -e REDIS_HOST=localhost \
  -e REDIS_PORT=6379 \
  wschatengine:latest
```
