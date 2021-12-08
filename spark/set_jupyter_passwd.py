# this script sets a password to the jupyter notebook served on ec2
from IPython.lib import passwd
with open("/root/.jupyter/jupyter_notebook_config.py", "a") as f:
    f.write("\nconf.NotebookApp.password =u\"" + passwd("lotlr") + "\"\n")
