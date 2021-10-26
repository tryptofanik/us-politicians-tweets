# Templates
How to use templates provided in this folder

### Nifi.json
This template creates a single EC2 instance with a new security group. The security group allows to connect via port 22 and 8080 from any ip address. The ec2 instance is by default a t2.micro instance created on ubuntu 18 AMI. Apache Nifi 13.2.1 is installed using the commands listed in the user data section.


To initiate the template, please follow the steps:
 - go to Cloudformation
 - create a new Stack
 - in Step 1 upload `nifi.json` as an existing emplate
 - in Step 2 choose `nifi` key pairs as key to the instance. You can change the instance type from t2.micro to larger (t2.micro is free of charge and sufficient for testing, t2.large is recommended in production)
 - in Step 3 choose `NifiRole` as the IAM role
 - launch the stack
 - wait a few (10) minutes
 - after about 10 minutes, you should be able to view the NiFi UI. Copy the public IP of the newly created instance, and paste `<public ip>:8080/nifi` in the browser

#### Possible problems
##### NifiRole
In case you have to create the `NifiRole` from the beginning (e.g. we switched the accounts), please attach a following policy to it:
  ```
  {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "ec2:DetachVolume",
                "ec2:AttachVolume",
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:DescribeInstances",
                "ec2:RunInstances",
                "ec2:ModifySecurityGroupRules",
                "ec2:DescribeSecurityGroups",
                "ec2:CreateVolume",
                "ec2:DescribeVolumeStatus",
                "ec2:DescribeSecurityGroupRules",
                "ec2:DescribeAvailabilityZones",
                "ec2:CreateSecurityGroup",
                "ec2:DescribeVolumes",
                "ec2:DescribeKeyPairs"
            ],
            "Resource": "*"
        }
    ]
}
  ```
##### Key-pair
If you would like to ssh into the instance, the `nifi` key-pair can be downloaded from [there](https://drive.google.com/drive/folders/1xqXe1HtXGEm3rLEWXnILUifuVz9---C_?usp=sharing).

In case we switched accounts, please reupload the .pem key-pair in [AWS](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#how-to-generate-your-own-key-and-import-it-to-aws).
  
