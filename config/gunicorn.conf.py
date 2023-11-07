accesslog = '-'
access_log_format = '%(t)s %({x-forwarded-for}i)s %(m)s %(U)s %(s)s %(M)s "%(a)s"'
bind = 'unix:/tmp/pysecrets.sock'
capture_output = True
daemon = False
errorlog = '-'
timeout = 60
workers = 4
