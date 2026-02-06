from kubernetes import client, config

def test_all_nodes_ready():
    """
    Platform Quality Rule:
    All nodes must be in Ready state
    """
    config.load_kube_config()
    v1 = client.CoreV1Api()
    nodes = v1.list_node().items

    not_ready = []
    for node in nodes:
        for condition in node.status.conditions:
            if condition.type == "Ready" and condition.status != "True":
                not_ready.append(node.metadata.name)

    assert not not_ready, f"NotReady nodes found: {not_ready}"
