from kubernetes import client, config
from .release_gate import ReleaseDecision


RESTART_THRESHOLD = 3

def evaluate_platform():
    decision = ReleaseDecision()
    config.load_kube_config()
    v1 = client.CoreV1Api()

    # Node readiness
    for node in v1.list_node().items:
        for condition in node.status.conditions:
            if condition.type == "Ready" and condition.status != "True":
                decision.record_issue(f"Node not ready: {node.metadata.name}")

    # Pod health & restarts
    pods = v1.list_pod_for_all_namespaces().items
    for pod in pods:
        statuses = pod.status.container_statuses or []
        for status in statuses:
            if status.state.waiting and status.state.waiting.reason == "CrashLoopBackOff":
                decision.record_issue(
                    f"CrashLoop pod: {pod.metadata.namespace}/{pod.metadata.name}"
                )
            if status.restart_count > RESTART_THRESHOLD:
                decision.record_issue(
                    f"High restart pod: {pod.metadata.namespace}/{pod.metadata.name}"
                )

    return decision


if __name__ == "__main__":
    decision = evaluate_platform()
    print(decision.summary())
