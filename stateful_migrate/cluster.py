from base import Base
import yaml


class Cluster(Base):
    kubeconfig = ""
    name = ""

    def __init__(self, name, kubeconfig):
        self.kubeconfig = kubeconfig
        self.name = name

    def config(self):
        with open(self.kubeconfig, 'r') as fp:
            data = yaml.safe_load(fp)

            config = {
                'context': self.config_section(
                    data,
                    'contexts',
                    data['current-context']
                )['context']
            }

            config['cluster'] = self.config_section(
                data,
                'clusters',
                config['context']['cluster']
            )['cluster']

            config['user'] = self.config_section(
                data,
                'users',
                config['context']['user']
            )['user']

            return config

    def config_section(self, data, ctype, name):
        for elem in data[ctype]:
            if elem['name'] == name:
                break
        else:
             raise ValueError(
                 "%s '%s' not found" % (ctype, name)
             )
        return elem

    def pods(self):
        print("pods")

    def nodes(self):
        print(self.config())
        print("nodes")
    pass
