from kubernetes import client, config

def test_cluster_reachable():
    """
    Platform Quality Rule:
    Kubernetes cluster must be reachable
    """
    config.load_kube_config()
    v1 = client.CoreV1Api()
    nodes = v1.list_node()
    assert len(nodes.items) > 0, "No nodes found in cluster"
