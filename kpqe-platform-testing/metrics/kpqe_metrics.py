from prometheus_client import start_http_server, Gauge
from kubernetes import client, config
import time

# =====================
# Config
# =====================
RESTART_THRESHOLD = 3

# =====================
# Metrics Definitions
# =====================
cluster_ready = Gauge(
    "kpqe_cluster_ready",
    "Kubernetes cluster reachability (1 = ready, 0 = not ready)"
)

crashloop_pods = Gauge(
    "kpqe_crashloop_pods",
    "Number of pods in CrashLoopBackOff"
)

restart_risk = Gauge(
    "kpqe_restart_risk",
    "Pods with restart count > threshold"
)

release_allowed = Gauge(
    "kpqe_release_allowed",
    "Release decision (1 = allowed, 0 = blocked)"
)

# =====================
# Kubernetes Config Loader
# =====================
def load_k8s_config():
    """
    Loads Kubernetes config based on execution environment
    - In-cluster → ServiceAccount
    - Local → kubeconfig
    """
    try:
        config.load_incluster_config()
        print("Loaded in-cluster Kubernetes config")
    except Exception:
        config.load_kube_config()
        print("Loaded local kubeconfig")

# =====================
# Platform Evaluation
# =====================
def evaluate_platform(v1: client.CoreV1Api):
    # ---- Cluster Check ----
    cluster_ok = 0
    try:
        nodes = v1.list_node()
        cluster_ok = 1 if nodes.items else 0
    except Exception as e:
        cluster_ok = 0
        print(f"Cluster check failed: {e}")

    cluster_ready.set(cluster_ok)

    # ---- Pod Health Checks ----
    crash_count = 0
    restart_count = 0

    try:
        pods = v1.list_pod_for_all_namespaces().items
    except Exception as e:
        print(f"Pod list failed: {e}")
        pods = []

    for pod in pods:
        statuses = pod.status.container_statuses or []
        for status in statuses:
            # CrashLoop check
            if (
                status.state
                and status.state.waiting
                and status.state.waiting.reason == "CrashLoopBackOff"
            ):
                crash_count += 1

            # Restart threshold check
            if status.restart_count > RESTART_THRESHOLD:
                restart_count += 1

    crashloop_pods.set(crash_count)
    restart_risk.set(restart_count)

    # ---- Release Gate Decision ----
    # Release allowed only if:
    # 1) Cluster reachable
    # 2) No crashloop pods
    if cluster_ok == 1 and crash_count == 0:
        release_allowed.set(1)
    else:
        release_allowed.set(0)

# =====================
# Metrics Server
# =====================
def run():
    print("Starting KPQE Metrics Server...")
    start_http_server(8000)
    print("KPQE Metrics running on :8000/metrics")

    # Load config only once
    load_k8s_config()
    v1 = client.CoreV1Api()

    while True:
        evaluate_platform(v1)
        time.sleep(15)

if __name__ == "__main__":
    run()
