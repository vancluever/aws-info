aws-info
========

This is a proof of concept script that contains the following:

 * A shell script that queries AWS for EC2, RDS, ElastiCache, ELB, 
 and CloudFormation information, and outputs the text in a JSON
 * A python script that parses that JSON, and displays some summarized
 data, along with the original JSON made pretty.

The script displays the info in a very primitive HTML format, however 
some attempts are made at reducing clutter by using the jQuery UI 
Accordion element.

**THIS IS FOR DEMONSTRATION PURPOSES ONLY - RUN AT YOUR OWN RISK**

Requirements
-----------

 * Python (2.7 recommended)
 * awscli (https://github.com/aws/aws-cli)

jQuery UI elements are contained within this repo.

Usage
-----

This script has been tested both on a local machine (running OS X Yosemite)
and a Debian webserver running apache. In its currently configured form,
it should be able to be run out of a website simply by uploading it to the
document root.

### Shell Script Configuration

Make sure that you edit the bin/get-aws-info.sh and update the AWS
authentication information:

    export AWS_ACCESS_KEY_ID=ACCESSKEY
    export AWS_SECRET_ACCESS_KEY=ACCESSSECRET

### Apache Configuration

Copy the script in its entirety to your document root, and set up the
following alias in your apache config:

    ScriptAlias /bin /path/to/root/bin

Ensure that both binaries in the bin/ directory are executable.

You can then run the script by navigating to http://HTTPHOST/bin/aws-info.py.

### Running locally

The script can be run locally too - just simply navigate to the bin/ 
directory and run:

    ./aws-info.py > output.html

This will redirect the output to output.html, which can then be viewed
locally. Note that you may have to slightly edit the HTML to get the JS
to work properly (make sure you update the JS links to the appropriate
locations).

Questions? Comments?
--------------------

If you found this script at all useful, feel free to email me at
inbox@vancluevertech.com.

Thanks and enjoy!

--Chris
