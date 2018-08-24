# coding: utf8
import magic


def get_file_extension(file_header):
    mime_dict = {
        'application/epub+zip': 'epub',
        'application/zip': 'zip',
        'application/x-tar': 'tar',
        'application/x-rar-compressed': 'rar',
        'application/gzip': 'gz',
        'application/x-gzip': 'gz',
        'application/x-bzip2': 'bz2',
        'application/x-7z-compressed': '7z',
        'application/x-xz': 'xz',
        'application/pdf': 'pdf',
        'application/x-msdownload': 'exe',
        'application/x-shockwave-flash': 'swf',
        'application/rtf': 'rtf',
        'application/octet-stream': 'eot',
        'application/postscript': 'ps',
        'application/x-sqlite3': 'sqlite',
        'application/x-nintendo-nes-rom': 'nes',
        'application/x-google-chrome-extension': 'crx',
        'application/vnd.ms-cab-compressed': 'cab',
        'application/x-deb': 'deb',
        'application/x-unix-archive': 'ar',
        'application/x-compress': 'Z',
        'application/x-lzip': 'lz',
    }
    mime_type = magic.from_buffer(
        file_header,
        mime=True
    )
    try:
        if mime_dict[mime_type] == 'gz':
            magic_tools = magic.Magic(mime=True, uncompress=True)
            mime_type_in_gz = magic_tools.from_buffer(file_header)
            file_extension = '%s.%s' % (
                mime_dict[mime_type_in_gz], mime_dict[mime_type]
            )
        else:
            file_extension = mime_dict[mime_type]
    except KeyError:
        file_extension = None
    return {'file_extension': file_extension, 'mime_type': mime_type}
