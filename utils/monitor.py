from kubernetes import client, config

class Monitor:
    def __init__(self, cfg=None, sched=None):
        # Load the Kubernetes configuration
        if cfg is None:
            self.config = config.load_kube_config()
        else:
            self.config = cfg

        self.sched = sched

        # Load the Kubernetes API client
        self.core_api = client.CoreV1Api()

    def get_pending_pods(self, debug=False):
        if debug:
            print("Get pending pods")
        pending_pods = []
        pods = self.core_api.list_namespaced_pod(namespace="default")


        for pod in pods.items:
            # Check if the spec.schedulerName is equal to the scheduler name if self.sched is not None
            if self.sched is not None:
                if pod.spec.scheduler_name == self.sched and pod.status.phase == "Pending":
                    if pod.status.phase == "Pending":
                        pending_pods.append(pod)
            else:
                if pod.status.phase == "Pending":
                    pending_pods.append(pod)

        # Ordering the pending pods by the creation time
        pending_pods = sorted(pending_pods, key=lambda x: x.metadata.creation_timestamp)

        pending_pods_names = [pod.metadata.name for pod in pending_pods]
        return (pending_pods_names, pending_pods)
    
    def get_pods(self, status="Running", debug=False):
        if debug:
            print("Get pods with status: " + status)
        return_pods = []
        pods = self.core_api.list_namespaced_pod(namespace="default")
        for pod in pods.items:
            if pod.status.phase == status:
                return_pods.append(pod)
        return_pods_names = [pod.metadata.name for pod in return_pods]
        return (return_pods_names, return_pods)


    def get_pod(self, pod_name, debug=False):
        if debug:
            print("Get pod: " + pod_name)
        return self.core_api.read_namespaced_pod(name=pod_name, namespace="default")
    
    def get_pod_rqsts(self, pod_name, debug=False):
        pod = self.get_pod(pod_name)
        if debug:
            print("Get pod requests: " + pod.metadata.name)
        pod_rqsts = {}
        pod_rqsts["name"] = pod.metadata.name
        rqsts = pod.spec.containers[0].resources.requests
        pod_rqsts["cpu"] = rqsts["cpu"] if rqsts else "500m"
        pod_rqsts["memory"] = rqsts["memory"] if rqsts else "500Mi"
        return pod_rqsts
    
    def get_nodes(self, debug=False):
        if debug:
            print("Get nodes")
        nodes = self.core_api.list_node()
        node_names = [node.metadata.name for node in nodes.items]
        return (node_names, nodes.items)
    
    def get_node(self, node_name, debug=False):
        if debug:
            print("Get node: " + node_name)
        return self.core_api.read_node(name=node_name)
    
    def get_nodes_rsrc(self, debug=False):
        if debug:
            print("Get nodes resources")

        # Get the Usage metrics
        metrics_api = client.CustomObjectsApi()
        metrics = metrics_api.list_cluster_custom_object(group="metrics.k8s.io", version="v1beta1", plural="nodes")
        metrics = metrics["items"]
        usage_metrics = {}
        for metric in metrics:
            usage_metric = {
                "cpu": metrics["usage"]["cpu"],
                "memory": metrics["usage"]["memory"]
            }
            usage_metrics[metric["metadata"]["name"]] = usage_metric

        # Get the number of pods running on each node
        pods = self.core_api.list_namespaced_pod(namespace="default")
        pods = pods.items
        pods_per_node = {}
        for pod in pods:
            node_name = pod.spec.node_name
            if node_name in pods_per_node:
                pods_per_node[node_name] += 1
            else:
                pods_per_node[node_name] = 1

        nodes_rsrc = {}
        for node in self.get_nodes()[0]:
            node_rsrc = {
                "cpu": (usage_metrics[node]["cpu"], self.get_node(node).status.allocatable["cpu"]),
                "memory": (usage_metrics[node]["memory"], self.get_node(node).status.allocatable["memory"]),
                "pod_cap": (pods_per_node[node], self.get_node(node).status.allocatable["pods"])
            }
            nodes_rsrc[node] = node_rsrc

        return nodes_rsrc
    
    def get_node_rsrc(self, node_name, debug=False):
        if debug:
            print("Get node resources: " + node_name)
        
        nodes_rsrc = self.get_nodes_rsrc()
        return nodes_rsrc[node_name]