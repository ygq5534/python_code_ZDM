from oslo.config import cfg

CONF = cfg.CONF


class Module(object):
    def __init__(self, context):
        self.context = context
        self.resource_files = []

    def reload_config(self):
        CONF.reload_config_files()

    def set_type(self, type):
        self.type = type

    def set_path(self, path):
        self.path = path

    def set_name(self, name):
        self.name = name

    def set_enable(self, enable):
        self.enable = enable

    def set_load_enable(self, load_enable):
        self.load_enable = load_enable

    def set_resource_file(self, files):
        self.resource_files = files

    def add_resource_file(self, file_):
        self.resource_files.append(file_)

    def add_resource_files(self, files):
        self.resource_files.extend(files)

    def set_class_name(self, class_name):
        self.class_name = class_name

class ThriftModule(Module):

    def __init__(self, context):
        super(ThriftModule,self).__init__(context)

    def set_ip(self, ip):
        self.ip = ip

    def set_port(self, port):
        self.port = port
