# Kubernetes Platform Quality Policy

## Platform Readiness Rules

1. Kubernetes cluster must be reachable
2. All nodes must be in Ready state
3. kube-system critical pods must be running
4. No pod should be in CrashLoopBackOff
5. Excessive pod restarts indicate instability
6. Kubernetes API server must report ready
7. Any rule violation blocks release

## Quality Philosophy

Kubernetes is treated as a release-critical platform.
Application releases are allowed only if the platform is stable and healthy.
