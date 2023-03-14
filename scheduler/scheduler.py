from kubernetes import client, config
from utils.monitor import Monitor
from utils.filter import Filter

import random

class Scheduler:
    def __init__(self, cfg=None):
        # Load the Kubernetes configuration
        if cfg is None:
            self.config = config.load_kube_config()
        else:
            self.config = cfg

        # Load the Kubernetes API client
        self.core_api = client.CoreV1Api()
        self.monitor = Monitor(cfg=self.config)
        self.filter = Filter()
    
    def scheduling(self, pod_name, node_name, debug=False):
        pod = self.monitor.get_pod(pod_name)
        if debug:
            print(f"Pod: {pod_name}, status: {pod.status.phase}")
        # Check if the pod is already scheduled
        if pod.status.phase == "Pending":
            print(f"Pod [{pod_name}] is scheduled to node [{node_name}]")
            try:
                # Binding the pod to the node
                body = client.V1Binding(
                    metadata=client.V1ObjectMeta(
                        name=pod_name,
                        namespace="default"
                    ),
                    target=client.V1ObjectReference(
                        api_version="v1",
                        kind="Node",
                        name=node_name,
                        namespace="default"
                    )
                )
                self.core_api.create_namespaced_binding(
                    body=body,
                    namespace="default"
                )
            except Exception as e:
                # print(f"Exception when calling CoreV1Api->create_namespaced_binding: {e}")
                pass
        else:
            print(f"Pod {pod_name} is already scheduled to node {pod.spec.node_name}")
