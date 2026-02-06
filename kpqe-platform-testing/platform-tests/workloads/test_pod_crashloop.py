from kubernetes import client, config

def test_no_pods_in_crashloop():
    """
    Platform Quality Rule:
    No pod should be in CrashLoopBackOff
    """
    config.load_kube_config()
    v1 = client.CoreV1Api()

    bad_pods = []

    pods = v1.list_pod_for_all_namespaces().items
    for pod in pods:
        statuses = pod.status.container_statuses or []
        for status in statuses:
            state = status.state
            if state.waiting and state.waiting.reason == "CrashLoopBackOff":
                bad_pods.append(f"{pod.metadata.namespace}/{pod.metadata.name}")

    assert not bad_pods, f"CrashLoopBackOff pods found: {bad_pods}"
