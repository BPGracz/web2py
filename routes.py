routers = dict(
    BASE  = dict(default_application='blog'),
    # reroute favicon and robots, use exable for lack of better choice
    #('/favicon.ico', '/blog/static/images/favicon.ico')
)
routes_out = ()