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
