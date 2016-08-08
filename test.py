from stateful_migrate import Cluster,StatefulApp
import os.path

def main():
    base_path = os.path.expanduser(
        '~/git/github.com/pearsontechnology/bitesize'
    )
    clusterA = Cluster('jetstack-a', os.path.join(
        base_path,
        'instances/jetstack/kubeconfig-a',
    ))
    clusterB = Cluster('jetstack-b', os.path.join(
        base_path,
        'instances/jetstack/kubeconfig-a',
    ))

    clusterA.nodes()
    clusterB.nodes()

if __name__ == "__main__":
        main()
