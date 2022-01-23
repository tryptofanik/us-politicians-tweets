# this script sets a password to the jupyter notebook served on ec2
from IPython.lib import passwd
import boto3
with open("/root/.jupyter/jupyter_notebook_config.py", "a") as f:
    f.write("\nconf.NotebookApp.password =u\"" + passwd(boto3.client("ssm", region_name="us-east-1").get_parameter(Name="jupyter-password")["Parameter"]["Value"]) + "\"\n")
