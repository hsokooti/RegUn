import os


def ls(server_address, server_user, folder_to_list):
    rsync_output = os.popen("rsync --list-only " + server_user + '@' + server_address + ":" + folder_to_list).read()
    file_list = []
    for line_i, line_str in enumerate(rsync_output.splitlines()):
        if line_i > 0:
            filename_str = line_str.rsplit(' ', maxsplit=1)[1]
            file_list.append(filename_str)
    return file_list
