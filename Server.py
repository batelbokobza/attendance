import os
import re
import pysftp


def get_unique_file_name(file_path):
    unique_file_name = re.split('[\t. ]', file_path)
    return unique_file_name[0] + '.csv'

class Server:
    """
    Server class:
            The class contains a function that connects to a virtual machine and downloads the files found in
            the received path.
            To connect to the virtual machine, three strings must be passed to the class constructor:
            ip address, username, and password.
            And two additional strings containing the requested remote path the virtual machine,
            and a local path to create a directory that will contain the files after the download.
    """

    def __init__(self, remote_directory_path, local_directory_path):
        self.ip = '185.164.16.144'  # Connection to server via ip address username and password.
        self.user_name = 'batelb'
        self.password = '123456'
        self.files_list = set()
        self.remote_dir_path = remote_directory_path
        self.local_dir_path = local_directory_path

    def get_csv_file_names_list_from_remote_host(self):
        """Getting a list of the files names located in the requested path in the virtual machine.
            * The function considers and handles cases where there is a duplicate file.
                    :return:
                        file_names_list: (list)"""
        self.create_local_directory()
        self.download_csv_files_from_server()
        temp_dict = dict()
        file_names_list = set()
        for file_name in os.listdir(self.local_dir_path):
            file_name_unique = get_unique_file_name(file_name)  # To not read duplicate files.
            name, extension = os.path.splitext(self.local_dir_path + '/' + file_name)
            if file_name_unique not in temp_dict.keys() and extension == '.csv':
                temp_dict[file_name_unique] = True
                file_names_list.add(file_name)
        return file_names_list

    def download_csv_files_from_server(self):
        """Connecting to the virtual machine with the updated details in the constructor,
            and downloading the files in the requested path."""
        # downloads the files from the remote server into the local path received as a parameter in the constructor.
        conn_options = pysftp.CnOpts()
        conn_options.hostkeys = None  # To disable host key checking.
        with pysftp.Connection(self.ip, username=self.user_name, password=self.password, cnopts=conn_options) as sftp:
            sftp.cwd(self.remote_dir_path)  # Transposing typed commands at sftp to pysftp.
            directory_attribute_list = sftp.listdir_attr()  # Returns sorted files list by SFTPAttribute.filename.
            for attr in directory_attribute_list:
                file_name = attr.filename
                remote_file_path = self.remote_dir_path + file_name
                local_file_path = self.local_dir_path + file_name
                sftp.get(remote_file_path, local_file_path)

    def create_local_directory(self):
        if not os.path.exists(self.local_dir_path):
            try:
                os.mkdir(self.local_dir_path)
            except OSError as error:
                print(error)

    def get_local_directory_name_from_path(self):
        split_path = re.split('[/]', self.local_dir_path)
        return split_path[len(split_path) - 2]


