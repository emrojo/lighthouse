from lighthouse.config.defaults import *  # noqa: F403, F401

# setting here will overwrite those in 'defaults.py'

# APScheduler config
SCHEDULER_RUN = False

# Eve config
# MONGO_HOST = "127.0.0.1"
# MONGO_DBNAME = "lighthouseDevelopmentDB"

MONGO_HOST = "vm-mg-psd-uat1.internal.sanger.ac.uk"
MONGO_DBNAME = "lighthouseUATDB"
MONGO_URI = "mongodb://lighthouse_owner:ora7gepe7@vm-mg-psd-uat1.internal.sanger.ac.uk/lighthouseUATDB"
# MLWH_CONN_STRING: "mlwhd_admin:jEbRepuJe7@mlwh-db:3436"
MLWH_CONN_STRING: "mlwh_admin:pESatUpr8S@mlwh-db:3435"
ML_WH_DB = "mlwhd_mlwarehouse_devdata"
EVENTS_WH_DB = "mlwhd_mlwh_events_proddata"

# logging config
LOGGING["loggers"]["lighthouse"]["level"] = "DEBUG"  # noqa: F405
LOGGING["loggers"]["lighthouse"]["handlers"] = ["colored_stream"]  # noqa: F405

MLWH_CONN_STRING = "root@localhost"
