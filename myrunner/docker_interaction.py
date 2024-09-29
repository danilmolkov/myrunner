import docker
import tarfile
import io
import docker.errors
import logging

# Initialize the Docker client
client = docker.from_env()
api = docker.APIClient()


class DockerInteraction:
    def __init__(self, container_id):
        self.container = client.containers.get(container_id)

    def get_runlist_from_container(self):
        # Get the labels of the container
        container_labels = self.container.labels
        if 'myrunner' in container_labels.keys():
            logging.debug('runlist label is found for %s', self.container.name)
            try:
                archive_stream, _ = self.container.get_archive(container_labels['myrunner'])
            except docker.errors.NotFound as e:
                print(e.explanation)
                return
            # Read the archive into a bytes object
            file_data = io.BytesIO()
            for chunk in archive_stream:
                file_data.write(chunk)

            # Reset the pointer of the BytesIO object
            file_data.seek(0)

            # Extract the file content from the tar archive
            with tarfile.open(fileobj=file_data) as tar:
                # Extract the file (there should be only one file in the tar)
                extracted_file = tar.extractfile(tar.getmembers()[0])
                file_bytes = extracted_file.read()

            # file_bytes now contains the content of the file in bytes
            return file_bytes

    def command(self, command: str, envs):
        print(command)
        # Execute the command inside the container
        exit_code, output = self.container.exec_run(command)

        # Print the command's output
        print(f"Exit Code: {exit_code}")
        print(f"Output: {output.decode('utf-8')}")
