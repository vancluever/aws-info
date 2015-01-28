#!/usr/bin/env python
"""aws-info: Parse select info from AWS (ec2, rds, elasticache, elb, cloudformation)"""

# CHANGES: Header functionality has been DEPRECATED.
# This has been moved to the /index.html page, which calls this script for 
# the tables and appropraite other output. That's it.
# Code is retained here but is currently disabled, and will probably
# fail if used since the template no longer exists.

import sys
import subprocess
import json

class MyError(Exception):
	def __init__(self, value):
		print "ERROR:", value
		sys.exit(1)

class AWSInfo:
	"""AWSInfo: main script workhorse for aws-info script"""

	# some very small template bits - these are itmes that I do want to create separate
	# template files at this point in time, but may be useful to do so later.
	template_table_greenstatus = '<td class="statusgreen">'
	template_table_redstatus = '<td class="statusred">'
	
	# Heading of webpage
	template_page_heading = '<h1 class="pagetop">AWS Infrastructure Display</h1>'

	# location for template files
	template_header_file = "../templates/header.html.template"

	# path to JSON grabber
	json_shell_path = './get-aws-info.sh'
	awsinfo_raw_data = ''
	awsinfo_raw_parsed = {}
	awsinfo_parsed_data = {}
	

	def __init__(self, **kwargs):
		# init by getting JSON
		self.get_json()

	def get_json(self):
		"""Call shell script to get JSON, and parse"""
		self.awsinfo_raw_data = subprocess.check_output(self.json_shell_path)
		self.awsinfo_raw_parsed = json.loads(self.awsinfo_raw_data)
		for item in self.awsinfo_raw_parsed['aws-info']:
			# populate awsinfo_parsed_data with a simple dictionary of the data we need.
			# saves having to deal with a ton of nesting/iterating later
			self.awsinfo_parsed_data[item['entity']] = item['data']

	def render(self):
		"""Renders AWSInfo in HTML"""
		sys.stdout.write("Content-Type: text/html\n\n")
		# render_header disabled as functionality has been moved
		#self.render_header()
		self.render_body()

	def render_table(self, headers, rows):
		"""Renders a table in page, renders headers along with status fields highlighted"""
		#
		# NOTE: This function expects the table data in a specific format:
		# Headers: Tuple of table header names, in the order they are to be displayed
		# rows: an array of a dict of dicts:
		#    parent (row) dict: is an index of all the rows that can be looked up by item
		#    we are specifically rendering
		#    child (item) dicts: each child dict has 2 key->value pairs currently:
		#        data: text to be displayed
		#        status: flag to highlight status data (0 = off 1 = green 2 = red)
		
		# render <table> and header data
		sys.stdout.write("<table>\n\t<tr>")
		for header in headers:
			sys.stdout.write("<th>{0}</th>".format(header))
		sys.stdout.write("</tr>\n")
		# render rows
		for row in rows:
			sys.stdout.write("\t<tr>")
			for header in headers:
				if row[header]['status'] == 1:
					# green status
					sys.stdout.write("{0}{1}</td>".format(self.template_table_greenstatus, row[header]['data']))
				elif row[header]['status'] == 2:
					# red status
					sys.stdout.write("{0}{1}</td>".format(self.template_table_redstatus, row[header]['data']))
				else:
					# regular column
					sys.stdout.write("<td>{0}</td>".format(row[header]['data']))
			# row finished
			sys.stdout.write("</tr>\n")
		# table finished
		sys.stdout.write("</table>\n")
	
	def render_preformatted(self, text):
		"""Renders a paragraph."""
		sys.stdout.write("<pre>{0}</pre>".format(text))
	
	def render_header(self):
		"""Renders the HTML header, includes include links to any CSS and JS"""
		
		# open the header template
		try:
			handle_template_header = open(self.template_header_file, 'r')
		except IOError as e:
			raise MyError(''.join([e.strerror, ': ', e.filename], ''))
		# load template data and render
		data = handle_template_header.readlines()
		sys.stdout.write(''.join(data))
		handle_template_header.close()
	
	def render_ec2(self):
		"""Renders the EC2 section of the report - prepares data, prints heading and table"""

		# ec2 table items: Name, Zone, Status, DNS, IP Address
		table_header = ('Name', 'Zone', 'Status', 'DNS', 'IPAddr')
		table_rows = []
		for reservation in self.awsinfo_parsed_data['ec2'][0]['Reservations']:
			for instance in reservation['Instances']:
				row={}
				for table_header_item in table_header:
					row[table_header_item] = {}
				# name - have to dig for it in tags
				for tag in instance['Tags']:
					if tag['Key'] == 'Name':
						row['Name']['data'] = tag['Value']
						row['Name']['status'] = 0
				# if there was no name tag
				if not row['Name'].has_key('data'):
					row['Name']['data'] = "unspecified"
					row['Name']['status'] = 0
				# zone - availability zone
				row['Zone']['data'] = instance['Placement']['AvailabilityZone']
				row['Zone']['status'] = 0
				# status - status of instance
				row['Status']['data'] = instance['State']['Name']
				if instance['State']['Code'] == 16:
					row['Status']['status'] = 1
				elif instance['State']['Code'] == 80:
					row['Status']['status'] = 2
				else:
					# can possibly use amber here or some other color
					row['Status']['status'] = 0
				# DNS
				# Use external if on, internal if off (ie: check for values)
				if instance.has_key('PublicDnsName'):
					row['DNS']['data'] = instance['PublicDnsName']
				else:
					row['DNS']['data'] = instance['PrivateDnsName']
				row['DNS']['status'] = 0
				# IP Address - same as DNS - fall back to private if no public
				if instance.has_key('PublicIpAddress'):
					row['IPAddr']['data'] = instance['PublicIpAddress']
				else:
					row['IPAddr']['data'] = instance['PrivateIpAddress']
				row['IPAddr']['status'] = 0
				# row done
				table_rows.append(row)
		# finished
		# render heading
		sys.stdout.write("<h3>EC2 Instances - {0} Items</h3>\n".format(len(table_rows)))
		self.render_table(table_header, table_rows)

	def render_rds(self):
		"""Renders the RDS section of the report - prepares data, prints heading and table"""
		
		# rds table items: Name, Zone, State, DNS, Engine
		table_header = ('Name', 'Zone', 'Status', 'DNS', 'Engine')
		table_rows = []
		for instance in self.awsinfo_parsed_data['rds'][0]['DBInstances']:
			row={}
			for table_header_item in table_header:
				row[table_header_item] = {}
			# name
			row['Name']['data'] = instance['DBInstanceIdentifier']
			row['Name']['status'] = 0
			# zone - availability zone
			row['Zone']['data'] = instance['AvailabilityZone']
			row['Zone']['status'] = 0
			# status - status of instance
			row['Status']['data'] = instance['DBInstanceStatus']
			if instance['DBInstanceStatus'] == 'available':
				row['Status']['status'] = 1
			else:
				row['Status']['status'] = 2
			# DNS
			row['DNS']['data'] = instance['Endpoint']['Address']
			row['DNS']['status'] = 0
			# engine
                        row['Engine']['data'] = instance['Engine']
                        row['Engine']['status'] = 0
			# row done
			table_rows.append(row)
		# finished
		# render heading
		sys.stdout.write("<h3>RDS Instances - {0} Items</h3>\n".format(len(table_rows)))
		self.render_table(table_header, table_rows)
		

	def render_elasticache(self):
		"""Renders the ElastiCache section of the report - prepares data, prints heading and table"""
		
		# elasticache table items: Name, Zone, State, Engine
		table_header = ('Name', 'Zone', 'Status', 'Engine')
		table_rows = []
		for instance in self.awsinfo_parsed_data['elasticache'][0]['CacheClusters']:
			row={}
			for table_header_item in table_header:
				row[table_header_item] = {}
			# name - have to dig for it in tags
			row['Name']['data'] = instance['CacheClusterId']
			row['Name']['status'] = 0
			# zone - availability zone
			row['Zone']['data'] = instance['PreferredAvailabilityZone']
			row['Zone']['status'] = 0
			# status - status of instance
			row['Status']['data'] = instance['CacheClusterStatus']
			if instance['CacheClusterStatus'] == 'available':
				row['Status']['status'] = 1
			else:
				row['Status']['status'] = 2
			# engine
                        row['Engine']['data'] = instance['Engine']
                        row['Engine']['status'] = 0
			# row done
			table_rows.append(row)
		# finished
		# render heading
		sys.stdout.write("<h3>ElastiCache Instances - {0} Items</h3>\n".format(len(table_rows)))
		self.render_table(table_header, table_rows)

	def render_elb(self):
		"""Renders the ELB section of the report - prepares data, prints heading and table"""
		
		# elb table items: Name, Zones, DNS
		table_header = ('Name', 'Zones', 'DNS')
		table_rows = []
		for instance in self.awsinfo_parsed_data['elb'][0]['LoadBalancerDescriptions']:
			row={}
			for table_header_item in table_header:
				row[table_header_item] = {}
			# name
			row['Name']['data'] = instance['LoadBalancerName']
			row['Name']['status'] = 0
			# zone - availability zone
			row['Zones']['data'] = ','.join(instance['AvailabilityZones'])
			row['Zones']['status'] = 0
			# DNS
			row['DNS']['data'] = instance['CanonicalHostedZoneName']
			row['DNS']['status'] = 0
			# row done
			table_rows.append(row)
		# finished
		# render heading
		sys.stdout.write("<h3>Elastic Load Balancers - {0} Items</h3>\n".format(len(table_rows)))
		self.render_table(table_header, table_rows)

	def render_cloudformation(self):
		"""Renders the CloudFormation section of the report - prepares data, prints heading and table"""
		
		# cloudformation table items: Name, CreatedDate, Status, Description (trunced at 30 chars)
		table_header = ('Name', 'CreatedDate', 'Status', 'Description')
		table_rows = []
		for instance in self.awsinfo_parsed_data['cloudformation'][0]['Stacks']:
			row={}
			for table_header_item in table_header:
				row[table_header_item] = {}
			# name
			row['Name']['data'] = instance['StackName']
			row['Name']['status'] = 0
			# created date
			row['CreatedDate']['data'] = instance['CreationTime']
			row['CreatedDate']['status'] = 0
			# Stack Status
			row['Status']['data'] = instance['StackStatus']
			if instance['StackStatus'] == 'CREATE_COMPLETE':
				row['Status']['status'] = 1
			else:
				row['Status']['status'] = 2
			# Description (truncated at 30 chars)
			row['Description']['data'] = "{0}".format(instance['Description'])
			row['Description']['status'] = 0
			# row done
			table_rows.append(row)
		# finished
		# render heading
		sys.stdout.write("<h3>CloudFormation Stacks - {0} Items</h3>\n".format(len(table_rows)))
		self.render_table(table_header, table_rows)
		

	def render_json(self):
		"""Renders the original JSON looking all pretty like"""
		# not much to this function.
		sys.stdout.write("<h3>Original JSON</h3>\n")
		self.render_preformatted(json.dumps(self.awsinfo_raw_parsed, indent=4, separators=(',', ': ')))

	def render_body(self):
		"""Renders the body - provides outer body, invokes jQuery accordion and calls sub-renderers"""

		# Disable header and initial body functionality - content has been moved
		#sys.stdout.write("{0}\n".format(self.template_page_heading))
		#sys.stdout.write("<div><p>Click an item to expand a section.<br></div>\n")

		# jQuery UI accordion element
		sys.stdout.write('<div id="accordion">\n')
		
		# Call out to each specific template function
		self.render_ec2()
		#self.render_rds()
		#self.render_elasticache()
		#self.render_elb()
		#self.render_cloudformation()
		self.render_json()
		
		# footer, end of document
		sys.stdout.write("</div>\n</body>\n</html>\n")


if __name__ == "__main__":
	# init object
	aws_info = AWSInfo()
	# render
	aws_info.render()
	# profit?

