**To download the data from the correct S3 bucket and test whether it works properly start the EMR cluster and add step with the following arguments**:

**Step type**: Custom JAR 

**Name**: S3DistCp 

**JAR location**: command-runner.jar 

**Arguments**: s3-dist-cp --src=s3://hadoop-data2/ --dest=hdfs:///data-trial 

After the step completes, you should be able to access the HDFS node interface and see new files, as well as see the finished application on the YARN timeline server.
