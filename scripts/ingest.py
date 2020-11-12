import sys
import json
import requests

project_title = "project_1"
dataset_title = "dataset_1"
table_name = "table_1"
katsu_server_url = "http://example.com:4000"
phenopackets_json_location = "/home/user/v2/CanCOGen_synthetic_data/cancogen_phenopackets.json"

print("Initializing...")
print("Warning: this script is only designed to handle the initial data ingestion of katsu service.")

# Create a new project

project_request = {"title": "", "description": "A new project."}
project_request["title"] = project_title

r = requests.post(katsu_server_url + "/api/projects", json=project_request)

if r.status_code == 201:
	project_uuid = r.json()["identifier"]
	print("Project {} with uuid {} has been created!".format(project_title, project_uuid))
elif r.status_code == 400:
	print("A project of this title exists, please choose a different title, or delete this project.")
	sys.exit()
else:
	print(r.json())
	sys.exit()


# Create a new dataset

dataset_request = {
	"project": "",
	"title": "",
	"data_use": {
		"consent_code": {
			"primary_category": {
				"code": "GRU"
			},
			"secondary_categories": [
				{
					"code": "GSO"
				}
			]
		},
		"data_use_requirements": [
			{
				"code": "COL"
			},
			{
				"code": "PUB"
			}
		]
	}
}

dataset_request["project"] = project_uuid
dataset_request["title"] = dataset_title

r2 = requests.post(katsu_server_url + "/api/datasets", json=dataset_request)

if r2.status_code == 201:
	dataset_uuid = r2.json()["identifier"]
	print("Dataset {} with uuid {} has been created!".format(dataset_title, dataset_uuid))
elif r2.status_code == 400:
	print("A dataset of this title exists, please choose a different title, or delete this project.")
	sys.exit()
else:
	print(r2.json())
	sys.exit()


# Create a new table

table_request = {
	"name": "table1",
	"data_type": "phenopacket",
	"dataset": ""
}

table_request["name"] = table_name
table_request["dataset"] = dataset_uuid

r3 = requests.post(katsu_server_url + "/tables", json=table_request)

if r3.status_code == 200 or r3.status_code == 201:
	table_id = r3.json()["id"]
	print("Table {} with uuid {} has been created!".format(table_name, table_id))
else:
	print("Something went wrong...")
	sys.exit()



# Ingest the phenopackets json

private_ingest_request = {
	"table_id": "",
	"workflow_id": "phenopackets_json",
	"workflow_params": {
		"phenopackets_json.json_document": ""
	},
	"workflow_outputs": {
		"json_document": ""
	}
}

private_ingest_request["table_id"] = table_id
private_ingest_request["workflow_params"]["phenopackets_json.json_document"] = phenopackets_json_location
private_ingest_request["workflow_outputs"]["json_document"] = phenopackets_json_location

print("Ingesting phenopackets, this may take a while...")

r4 = requests.post(katsu_server_url + "/private/ingest", json=private_ingest_request)

if r4.status_code == 200 or r4.status_code == 201 or r4.status_code == 204:
	print("Phenopackets has been ingested from source at {}".format(phenopackets_json_location))
elif r4.status_code == 400:
	print(r4.text)
	sys.exit()
else:
	print("Something else went wrong when ingesting phenopackets, possibly due to duplications.")
	print("Please remove existing individuals from the database and try again.")
	sys.exit()
