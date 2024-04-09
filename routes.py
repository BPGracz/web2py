routers = dict(
    BASE  = dict(default_application='blog2'),
    # reroute favicon and robots, use exable for lack of better choice
    #('/favicon.ico', '/blog2/static/images/favicon.ico')
)
routes_out = ()