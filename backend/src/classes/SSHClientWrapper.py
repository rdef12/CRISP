import paramiko

class SSHClientWrapper:
    def __init__(self, hostname, username, password=None, key_filename=None):
        """Initialize SSH connection."""
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(hostname, username=username, password=password, key_filename=key_filename)

    def execute_command(self, command, timeout=10):
        """Executes a command on the remote server and handles errors properly."""
        stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=timeout)

        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        stdin.close()  # Prevents potential SSH issues

        # Get the command's exit status
        exit_status = stdout.channel.recv_exit_status()

        if exit_status != 0:  # Only raise an error if the command failed
            raise Exception(f"Command '{command}' failed with exit status {exit_status}:\n{error}")

        return output, error  # Return both stdout and stderr for debugging

    def close(self):
        """Closes the SSH connection."""
        self.ssh_client.close()
