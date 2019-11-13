from .. import __version__

# Service info according to spec https://github.com/ga4gh-discovery/ga4gh-service-info

SERVICE_INFO = {
	"id": "ca.c3g.chord:metadata",  # TODO: Globally unique
	"name": "Metadata Service",  # TODO: Globally unique?
	"type": "ca.c3g.chord:metadata:{}".format(__version__),
	"description": "Metadata service implementation based on Phenopackets schema",
	"organization": {
		"name": "C3G",
		"url": "http://www.computationalgenomics.ca"
	},
	"contactUrl": "mailto:ksenia.zaytseva@mcgill.ca",
	"version": __version__
}
