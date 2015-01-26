#!/usr/bin/env bash

# get-aws-info.sh - describes multiple AWS resource units in a single JSON
# requires aws-cli to be installed on the system, and functional ~/.aws config files:
# 
# aws-cli binaries need to be properly accessible in $PATH.
# 
# note that this produces "compressed" JSON - if you want to look at this output raw,
# it might be better to use a javascript beautifier - ie: http://jsbeautifier.org/


# AWS credentials
export AWS_ACCESS_KEY_ID=ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=ACCESS_SECRET
# region
export AWS_DEFAULT_REGION=us-east-1

# commands to run
COMMANDS=`cat<<EOS
ec2 describe-instances
elb describe-load-balancers
elasticache describe-cache-clusters
rds describe-db-instances
cloudformation describe-stacks
EOS
`

# Basic JSON output functions
DELIM=""
json_open() {
        echo -n $DELIM"{"
        DELIM=""
}

json_close() {
        echo -n "}"
}

json_strval() {
        # print a properly formatted key/string value pair
        local KEY=$1
        local VALUE=$2
        
        echo -n $DELIM\"$KEY\": \"$VALUE\"
        DELIM=","
}

json_numval() {
        # print a properly formatted key/numeric value pair (value is printed w/o quotes)
        local KEY=$1
        local VALUE=$2
        
        echo -n $DELIM\"$KEY\": $VALUE
        DELIM=","
        
}

json_array_open() {
        # open an array with key
        local KEY=$1
        
        echo -n $DELIM\"$KEY\":[
        DELIM=""
}

json_array_close() {
        # close an arrayo
        echo -n ]
}

json_open
json_array_open aws-info
# small hack - add extra delim here as my output functions don't handle lists of objects
DELIM2=""
while read LINE ; do
	set -- $LINE
	echo -n $DELIM2
	json_open
	json_strval entity "$1"
	json_strval awscli_command "$LINE"
	json_array_open data
	aws $LINE | while read CMDOUT ; do
		echo -n $CMDOUT
	done
	json_array_close
	json_close
	# set hack delim2
	DELIM2=","
done<<EOS
$COMMANDS
EOS
#done
json_array_close
json_close
