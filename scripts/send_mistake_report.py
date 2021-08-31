class MistakeReport:
    instances = []

    def __init__(self, file_download_path):
        self.instances.append(self)
        self.file_download_path = file_download_path

    def clear_instances(self):
        self.instances.clear()
