import os
import json
import re

# Function to format lists in a single line
def format_list_in_line(json_string, key):
    # Pattern to match the list for the given key
    pattern = f'"{key}": \\[\n( +)([^\]]+)\n +\\]'

    # Replace function to format the list in a single line
    def replacer(match):
        indent = match.group(1)  # The current indentation
        list_content = match.group(2).replace('\n' + indent, '')  # Remove newlines and indentation inside the list
        return f'"{key}": [{list_content}]'

    return re.sub(pattern, replacer, json_string)

num_items = len(os.listdir("../155"))
radius = []
d1 = []
d2 = []
d3 = []

nodes_order = ["Domain", "IP", "Cert", "Whois", "ASN"]
industries_order = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
edges_order = ["r_cert", "r_subdomain", "r_request_jump", "r_dns_a", "r_whois_name", 
               "r_whois_email", "r_whois_phone", "r_cert_chain", "r_cname", "r_asn", "r_cidr"]

for i in range(0, num_items):
    file_path = "../155/"+str(i)+"/stat.json"
    with open(file_path, 'r') as file:
        data = json.load(file)
    radius.append(sum(data['nodes'].values()))

    sorted_d1 = [data['nodes'][key] if key in data['nodes'] else "0" for key in nodes_order]
    sorted_d2 = [data['industries'][key] if key in data['industries'] else "0" for key in industries_order]
    sorted_d3 = [data['edges'][key] if key in data['edges'] else "0" for key in edges_order]

    d1.append(sorted_d1)
    d2.append(sorted_d2)
    d3.append(sorted_d3)

pie_data = []
for i in range(0, num_items):
    item = {
        "id": i,
        "radius": radius[i],
        "d1": d1[i],
        "d2": d2[i],
        "d3": d3[i]
    }
    pie_data.append(item)
    
pretty_json = json.dumps(pie_data, indent=4)

# Adjust the formatting of d1, d2, and d3
for key in ["d1", "d2", "d3"]:
    pretty_json = format_list_in_line(pretty_json, key)

pie_file_path = "../pie_data.json"

with open(pie_file_path, 'w') as file:
    file.write(pretty_json)