import re

def database_url(url):
    regex = re.compile("(?P<schema>.*?)://(?P<user>.*?):(?P<password>.*?)@(?P<host>.*?)/(?P<database>.*)")
    dic = {}
    match = regex.match(url)
    user = match.group(2)
    host = match.group(4)
    hostname = host.split(':')[0]
    port = None if ':' not in host else host.split(':')[1]
    database = match.group(5)
    dic.update({
        "user": user,
        "password": match.group(3),
        "host": hostname,
        "port": port,
        "database": database,
    })

    return dic