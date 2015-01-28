aws-info
========

This is a proof of concept script that contains the following:

 * A shell script that queries AWS for EC2, RDS, ElastiCache, ELB, 
 and CloudFormation information, and outputs the text in a JSON
 * A python script that parses that JSON, and displays some summarized
 data, along with the original JSON made pretty.
 * An HTML/JS/jQuery application for the above that works to streamline
 the user experience.

**THIS IS FOR DEMONSTRATION PURPOSES ONLY - RUN AT YOUR OWN RISK**

Requirements
-----------

 * Python (2.7 recommended)
 * awscli (https://github.com/aws/aws-cli)

JavaScript is required to use the webpage (currently).

Usage
-----

Download the content from the repository (ie: git clone, zip, etc)
and follow the steps below:

### Shell Script Configuration

Make sure that you edit the bin/get-aws-info.sh and update the AWS
authentication information:

    export AWS_ACCESS_KEY_ID=ACCESSKEY
    export AWS_SECRET_ACCESS_KEY=ACCESSSECRET

### Apache Configuration

Copy the script in its entirety to your document root, or a directory
therein, and set up the following alias in your apache config:

    ScriptAlias /bin /path/to/content/bin

Don't forget to restart apache.

Ensure that both binaries in the bin/ directory are executable.

You can then run the script by navigating to http://HTTPHOST/content/.

### Running locally

Since some of the recent changes, the role the python script plays
directly have been reduced, but you can still see raw table output
rendered by running the python script locally:

    ./aws-info.py > output.html

Questions? Comments?
--------------------

If you found this script at all useful, feel free to email me at
inbox@vancluevertech.com.

Thanks and enjoy!

--Chris
