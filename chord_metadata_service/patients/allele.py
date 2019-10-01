ALLELE_SCHEMA = {
	"$schema": "http://json-schema.org/draft-07/schema#",
	"$id": "todo",
	"title": "Allele schema",
	"description": "Variant allele types",
	"type": "object",
	"properties": {
		"id": {"type": "string"},

		"hgvs": {"type": "string"},

		"genome_assembly": {"type": "string"},
		"chr": {"type": "string"},
		"pos": {"type": "integer"},
		"re": {"type": "string"},
		"alt": {"type": "string"},
		"info": {"type": "string"},

		"seq_id": {"type": "string"},
		"position": {"type": "integer"},
		"deleted_sequence": {"type": "string"},
		"inserted_sequence": {"type": "string"},

		"iscn": {"type": "string"}
	},
	"oneOf": [
		{
		"required": ["hgvs"]
		},
		{
		"required": ["genome_assembly"]
		},
		{
		"required": ["seq_id"]
		},
		{
		"required": ["iscn"]
		}

	],
	"dependencies": {
	"genome_assembly": ["chr", "pos", "re", "alt", "info"],
	"seq_id": ["position", "deleted_sequence", "inserted_sequence"]

	}
}
