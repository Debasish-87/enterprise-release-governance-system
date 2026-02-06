from kubernetes import client, config

RESTART_THRESHOLD = 3

def test_pod_restart_threshold():
    """
    Platform Quality Rule:
    Excessive pod restarts indicate instability
    """
    config.load_kube_config()
    v1 = client.CoreV1Api()

    risky_pods = []

    pods = v1.list_pod_for_all_namespaces().items
    for pod in pods:
        statuses = pod.status.container_statuses or []
        for status in statuses:
            if status.restart_count > RESTART_THRESHOLD:
                risky_pods.append(
                    f"{pod.metadata.namespace}/{pod.metadata.name} "
                    f"(restarts={status.restart_count})"
                )

    assert not risky_pods, f"Pods with high restart count: {risky_pods}"
