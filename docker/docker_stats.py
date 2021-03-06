import docker
import json
import multiprocessing

DOCKER_SOCKET = 'unix://var/run/docker.sock'
DOCKER_API_VERSION = '1.40'

class NearRealTimeRICCollector():
    
    def __init__(self, docker_socket, docker_api_version):
        self.client = docker.DockerClient(base_url=docker_socket,
                                 version=docker_api_version)
        self.NearRealTimeRIC_list = self.get_NearRealTimeRIC_instance_list()
        self.NearRealTimeRIC_scale = self.get_NearRealTimeRIC_scale()

    def get_NearRealTimeRIC_instance_list(self):
        return self.client.containers.list()

    def get_NearRealTimeRIC_scale(self):
        try:
            services = self.client.services.list(filters={'name': 'orion_orion'})
            service_inspector = self.client.api.inspect_service(services[0].id)
            scale = service_inspector['Spec']['Mode']['Replicated']['Replicas']
        except:
            return -1
        
        return scale

    def get_NearRealTimeRIC_info(self):
        if self.NearRealTimeRIC_list == None:
            return {'Message': 'No NearRealTimeRIC List available. Try running client.update_NearRealTimeRIC_instances()'}

        scale = self.get_NearRealTimeRIC_scale()
        #if scale != self.NearRealTimeRIC_scale:
        #    # if scale changed, list of services might have changed
        #    self.NearRealTimeRIC_scale = scale
        #    self.NearRealTimeRIC_list = self.get_NearRealTimeRIC_instance_list()

        self.NearRealTimeRIC_list = self.get_NearRealTimeRIC_instance_list()

        # get multiprocessing manager to return collected info
        # in a parallel fashion
        manager = multiprocessing.Manager()
        NearRealTimeRIC_info = manager.dict()

        proc_list = []
        for NearRealTimeRIC_instance in self.NearRealTimeRIC_list:
            # run in processes fashion to collect info faster
            p = multiprocessing.Process(target=self.__parse_NearRealTimeRIC_info,
                                        args=(NearRealTimeRIC_instance, NearRealTimeRIC_info))
            proc_list.append(p)
            p.start()

        for proc in proc_list:
            # join and kill the process
            proc.join()
            proc.terminate()
        
        NearRealTimeRIC_info['scale'] = scale

        return NearRealTimeRIC_info.copy()

    def __parse_NearRealTimeRIC_info(self, container, ret):

        try:
            # get container status dict
            container_stats = container.stats(stream=False)

            container_status = dict()

            container_name = container_stats['name']
            container_status[container_name] = dict()
            container_status[container_name]['id'] = container_stats['id']

            # calc cpu usage
            cur_cpu_usage = container_stats['cpu_stats']['cpu_usage']['total_usage']
            prev_cpu_usage = container_stats['precpu_stats']['cpu_usage'][
                'total_usage']
            delta_cpu_usage = cur_cpu_usage - prev_cpu_usage

            cur_system_cpu_usage = container_stats['cpu_stats']['system_cpu_usage']
            prev_system_cpu_usage = container_stats['precpu_stats']['system_cpu_usage']
            delta_system_cpu_usage = cur_system_cpu_usage - prev_system_cpu_usage

            per_cpu_usage_len = len(
                container_stats['cpu_stats']['cpu_usage']['percpu_usage'])

            perc_cpu_usage = (delta_cpu_usage /
                            delta_system_cpu_usage) * per_cpu_usage_len * 100

            container_status[container_name]['perc_cpu_usage'] = round(
                perc_cpu_usage, 2)

            # calc memory usage
            cur_mem_usage = container_stats['memory_stats']['usage'] - container_stats[
                'memory_stats']['stats']['cache']
            max_memory_available = container_stats['memory_stats']['limit']

            perc_mem_usage = (cur_mem_usage / max_memory_available) * 100

            container_status[container_name]['perc_mem_usage'] = round(
                perc_mem_usage, 2)

            # calc net traffic
            container_status[container_name]['rx_bytes'] = container_stats['networks'][
                'eth0']['rx_bytes']
            container_status[container_name]['tx_bytes'] = container_stats['networks'][
                'eth0']['tx_bytes']

            # create a entry in the return dictionary with the container name
            # and pass all info
            ret[container_name] = container_status[container_name]
        except:
            pass

'''
if __name__ == '__main__':

    NearRealTimeRIC = NearRealTimeRICCollector(DOCKER_SOCKET, DOCKER_API_VERSION)

    while True:
    
        info = NearRealTimeRIC.get_NearRealTimeRIC_info()

        print(json.dumps(info, indent=4))
'''
    
