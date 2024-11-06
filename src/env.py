import os

SQLDEF = "localhost:5432"
SQLHOST = os.environ.get("SQLHOST",SQLDEF)

DBUSER = os.environ.get("DBUSER",'postgres')
DBPASS = os.environ.get("DBPASS",'mysecretpassword')
DBTABLE = os.environ.get("DBTABLE",'sysml2')

WINDRUNNERHOST = os.environ.get(
    "WINDRUNNERHOST",
    "http://windrunner-webhook-eventsource-svc.argo-events:12000/windrunner"
)

WINDSTORMAPIHOST = os.environ.get(
    "WINDSTORMAPIHOST",
    "http://windstorm-api-service.windstorm:8000/"
)
