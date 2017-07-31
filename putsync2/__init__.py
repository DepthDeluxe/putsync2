def renderdownload(download):
    return {
        'remote_file_id': download.remote_file_id,
        'filepath': download.filepath,
        'size': download.size,
        'status':  'x'
    }
