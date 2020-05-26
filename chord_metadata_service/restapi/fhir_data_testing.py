FHIR_PATIENT = {
    "address": [
        {
            "city": "Carver",
            "country": "US",
            "extension": [
                {
                    "extension": [
                        {
                            "url": "latitude",
                            "valueDecimal": 41.875179
                        },
                        {
                            "url": "longitude",
                            "valueDecimal": -70.74671500000002
                        }
                    ],
                    "url": "http://hl7.org/fhir/StructureDefinition/geolocation"
                }
            ],
            "line": [
                "1087 Halvorson Light"
            ],
            "postalCode": "02330",
            "state": "Massachusetts"
        }
    ],
    "birthDate": "1991-02-10",
    "communication": [
        {
            "language": {
                "coding": [
                    {
                        "code": "pt",
                        "display": "Portuguese",
                        "system": "urn:ietf:bcp:47"
                    }
                ],
                "text": "Portuguese"
            }
        }
    ],
    "extension": [
        {
            "extension": [
                {
                    "url": "ombCategory",
                    "valueCoding": {
                        "code": "2106-3",
                        "display": "White",
                        "system": "urn:oid:2.16.840.1.113883.6.238"
                    }
                },
                {
                    "url": "text",
                    "valueString": "White"
                }
            ],
            "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race"
        },
        {
            "extension": [
                {
                    "url": "ombCategory",
                    "valueCoding": {
                        "code": "2186-5",
                        "display": "Not Hispanic or Latino",
                        "system": "urn:oid:2.16.840.1.113883.6.238"
                    }
                },
                {
                    "url": "text",
                    "valueString": "Not Hispanic or Latino"
                }
            ],
            "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity"
        },
        {
            "url": "http://hl7.org/fhir/StructureDefinition/patient-mothersMaidenName",
            "valueString": "Krysta658 Terry864"
        },
        {
            "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex",
            "valueCode": "M"
        },
        {
            "url": "http://hl7.org/fhir/StructureDefinition/birthPlace",
            "valueAddress": {
                "city": "Lisbon",
                "country": "PT",
                "state": "Estremadura"
            }
        },
        {
            "url": "http://synthetichealth.github.io/synthea/disability-adjusted-life-years",
            "valueDecimal": 0
        },
        {
            "url": "http://synthetichealth.github.io/synthea/quality-adjusted-life-years",
            "valueDecimal": 27
        }
    ],
    "gender": "male",
    "id": "6f7acde5-db81-4361-82cf-886893a3280c",
    "identifier": [
        {
            "system": "https://github.com/synthetichealth/synthea",
            "value": "a238ebf2-392b-44be-9a17-da07a15220e2"
        },
        {
            "system": "http://hospital.smarthealthit.org",
            "type": {
                "coding": [
                    {
                        "code": "MR",
                        "display": "Medical Record Number",
                        "system": "http://hl7.org/fhir/v2/0203"
                    }
                ],
                "text": "Medical Record Number"
            },
            "value": "a238ebf2-392b-44be-9a17-da07a15220e2"
        },
        {
            "system": "http://hl7.org/fhir/sid/us-ssn",
            "type": {
                "coding": [
                    {
                        "code": "SB",
                        "display": "Social Security Number",
                        "system": "http://hl7.org/fhir/identifier-type"
                    }
                ],
                "text": "Social Security Number"
            },
            "value": "999-99-7515"
        },
        {
            "system": "urn:oid:2.16.840.1.113883.4.3.25",
            "type": {
                "coding": [
                    {
                        "code": "DL",
                        "display": "Driver's License",
                        "system": "http://hl7.org/fhir/v2/0203"
                    }
                ],
                "text": "Driver's License"
            },
            "value": "S99942098"
        },
        {
            "system": "http://standardhealthrecord.org/fhir/StructureDefinition/passportNumber",
            "type": {
                "coding": [
                    {
                        "code": "PPN",
                        "display": "Passport Number",
                        "system": "http://hl7.org/fhir/v2/0203"
                    }
                ],
                "text": "Passport Number"
            },
            "value": "X19416767X"
        }
    ],
    "maritalStatus": {
        "coding": [
            {
                "code": "M",
                "display": "M",
                "system": "http://hl7.org/fhir/v3/MaritalStatus"
            }
        ],
        "text": "M"
    },
    "meta": {
        "lastUpdated": "2019-04-09T12:25:36.451316+00:00",
        "versionId": "MTU1NDgxMjczNjQ1MTMxNjAwMA"
    },
    "multipleBirthBoolean": False,
    "name": [
        {
            "family": "Hettinger594",
            "given": [
                "Gregg522"
            ],
            "prefix": [
                "Mr."
            ],
            "use": "official"
        }
    ],
    "resourceType": "Patient",
    "telecom": [
        {
            "system": "phone",
            "use": "home",
            "value": "555-282-3544"
        }
    ],
    "text": {
        "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">Generated by <a href=\"https://github.com/synthetichealth/synthea\">Synthea</a>.Version identifier: v2.2.0-56-g113d8a2d\n .   Person seed: 8417064283020065324  Population seed: 5</div>",
        "status": "generated"
    }
}

FHIR_OBSERVATION = {
    "category": [
        {
            "coding": [
                {
                    "code": "laboratory",
                    "display": "laboratory",
                    "system": "http://hl7.org/fhir/observation-category"
                }
            ]
        }
    ],
    "code": {
        "coding": [
            {
                "code": "785-6",
                "display": "MCH [Entitic mass] by Automated count",
                "system": "http://loinc.org"
            }
        ],
        "text": "MCH [Entitic mass] by Automated count"
    },
    "context": {
        "reference": "Encounter/2a0e0f6c-493f-4c5b-bf89-5f98aee24f21"
    },
    "effectiveDateTime": "2014-03-02T10:12:53-05:00",
    "id": "1c8d2ee3-2a7e-47f9-be16-abe4e9fa306b",
    "issued": "2014-03-02T10:12:53.714-05:00",
    "meta": {
        "lastUpdated": "2019-04-09T12:25:36.531997+00:00",
        "versionId": "MTU1NDgxMjczNjUzMTk5NzAwMA"
    },
    "resourceType": "Observation",
    "status": "final",
    "subject": {
        "reference": "Patient/6f7acde5-db81-4361-82cf-886893a3280c"
    },
    "valueQuantity": {
        "code": "pg",
        "system": "http://unitsofmeasure.org",
        "unit": "pg",
        "value": 27.035236044041877
    }
}

FHIR_OBSERVATION_BUNDLE = {
    "entry": [
        {
            "fullUrl": "https://syntheticmass.mitre.org/v1/fhir/Observation/97684895-3a6e-4d46-9edd-31984bc7c3a6",
            "resource": {
                "category": [
                    {
                        "coding": [
                            {
                                "code": "laboratory",
                                "display": "laboratory",
                                "system": "http://hl7.org/fhir/observation-category"
                            }
                        ]
                    }
                ],
                "code": {
                    "coding": [
                        {
                            "code": "718-7",
                            "display": "Hemoglobin [Mass/volume] in Blood",
                            "system": "http://loinc.org"
                        }
                    ],
                    "text": "Hemoglobin [Mass/volume] in Blood"
                },
                "context": {
                    "reference": "Encounter/2a0e0f6c-493f-4c5b-bf89-5f98aee24f21"
                },
                "effectiveDateTime": "2014-03-02T10:12:53-05:00",
                "id": "97684895-3a6e-4d46-9edd-31984bc7c3a6",
                "issued": "2014-03-02T10:12:53.714-05:00",
                "meta": {
                    "lastUpdated": "2019-04-09T12:25:36.531998+00:00",
                    "versionId": "MTU1NDgxMjczNjUzMTk5ODAwMA"
                },
                "resourceType": "Observation",
                "status": "final",
                "subject": {
                    "reference": "Patient/6f7acde5-db81-4361-82cf-886893a3280c"
                },
                "valueQuantity": {
                    "code": "g/dL",
                    "system": "http://unitsofmeasure.org",
                    "unit": "g/dL",
                    "value": 17.14301557752162
                }
            },
            "search": {
                "mode": "match"
            }
        },
        {
            "fullUrl": "https://syntheticmass.mitre.org/v1/fhir/Observation/1c8d2ee3-2a7e-47f9-be16-abe4e9fa306b",
            "resource": {
                "category": [
                    {
                        "coding": [
                            {
                                "code": "laboratory",
                                "display": "laboratory",
                                "system": "http://hl7.org/fhir/observation-category"
                            }
                        ]
                    }
                ],
                "code": {
                    "coding": [
                        {
                            "code": "785-6",
                            "display": "MCH [Entitic mass] by Automated count",
                            "system": "http://loinc.org"
                        }
                    ],
                    "text": "MCH [Entitic mass] by Automated count"
                },
                "context": {
                    "reference": "Encounter/2a0e0f6c-493f-4c5b-bf89-5f98aee24f21"
                },
                "effectiveDateTime": "2014-03-02T10:12:53-05:00",
                "id": "1c8d2ee3-2a7e-47f9-be16-abe4e9fa306b",
                "issued": "2014-03-02T10:12:53.714-05:00",
                "meta": {
                    "lastUpdated": "2019-04-09T12:25:36.531997+00:00",
                    "versionId": "MTU1NDgxMjczNjUzMTk5NzAwMA"
                },
                "resourceType": "Observation",
                "status": "final",
                "subject": {
                    "reference": "Patient/6f7acde5-db81-4361-82cf-886893a3280c"
                },
                "valueQuantity": {
                    "code": "pg",
                    "system": "http://unitsofmeasure.org",
                    "unit": "pg",
                    "value": 27.035236044041877
                }
            },
            "search": {
                "mode": "match"
            }
        },
        {
            "fullUrl": "https://syntheticmass.mitre.org/v1/fhir/Observation/b0598af4-8ffe-43ba-84e5-b7fb49d3dcd7",
            "resource": {
                "category": [
                    {
                        "coding": [
                            {
                                "code": "laboratory",
                                "display": "laboratory",
                                "system": "http://hl7.org/fhir/observation-category"
                            }
                        ]
                    }
                ],
                "code": {
                    "coding": [
                        {
                            "code": "777-3",
                            "display": "Platelets [#/volume] in Blood by Automated count",
                            "system": "http://loinc.org"
                        }
                    ],
                    "text": "Platelets [#/volume] in Blood by Automated count"
                },
                "context": {
                    "reference": "Encounter/2a0e0f6c-493f-4c5b-bf89-5f98aee24f21"
                },
                "effectiveDateTime": "2014-03-02T10:12:53-05:00",
                "id": "b0598af4-8ffe-43ba-84e5-b7fb49d3dcd7",
                "issued": "2014-03-02T10:12:53.714-05:00",
                "meta": {
                    "lastUpdated": "2019-04-09T12:25:36.530961+00:00",
                    "versionId": "MTU1NDgxMjczNjUzMDk2MTAwMA"
                },
                "resourceType": "Observation",
                "status": "final",
                "subject": {
                    "reference": "Patient/6f7acde5-db81-4361-82cf-886893a3280c"
                },
                "valueQuantity": {
                    "code": "10*3/uL",
                    "system": "http://unitsofmeasure.org",
                    "unit": "10*3/uL",
                    "value": 306.49607523265786
                }
            },
            "search": {
                "mode": "match"
            }
        }
    ],
    "resourceType": "Bundle"
}

FHIR_CONDITION = {
    "abatementDateTime": "2018-09-21T11:12:53-04:00",
    "assertedDate": "2018-08-22T11:12:53-04:00",
    "clinicalStatus": "resolved",
    "code": {
        "coding": [
            {
                "code": "62106007",
                "display": "Concussion with no loss of consciousness",
                "system": "http://snomed.info/sct"
            }
        ],
        "text": "Concussion with no loss of consciousness"
    },
    "context": {
        "reference": "Encounter/1d91f8e0-74f1-4071-a681-9d4fa0f9b93a"
    },
    "id": "4f2c2598-7e60-4752-b603-b330ca166829",
    "meta": {
        "lastUpdated": "2019-04-09T12:25:36.531999+00:00",
        "versionId": "MTU1NDgxMjczNjUzMTk5OTAwMA"
    },
    "onsetDateTime": "2018-08-22T11:12:53-04:00",
    "resourceType": "Condition",
    "subject": {
        "reference": "Patient/6f7acde5-db81-4361-82cf-886893a3280c"
    },
    "verificationStatus": "confirmed"
}

FHIR_CONDITION_BUNDLE = {
    "entry": [
        {
            "fullUrl": "https://syntheticmass.mitre.org/v1/fhir/Condition/4f2c2598-7e60-4752-b603-b330ca166829",
            "resource": {
                "abatementDateTime": "2018-09-21T11:12:53-04:00",
                "assertedDate": "2018-08-22T11:12:53-04:00",
                "clinicalStatus": "resolved",
                "code": {
                    "coding": [
                        {
                            "code": "62106007",
                            "display": "Concussion with no loss of consciousness",
                            "system": "http://snomed.info/sct"
                        }
                    ],
                    "text": "Concussion with no loss of consciousness"
                },
                "context": {
                    "reference": "Encounter/1d91f8e0-74f1-4071-a681-9d4fa0f9b93a"
                },
                "id": "4f2c2598-7e60-4752-b603-b330ca166829",
                "meta": {
                    "lastUpdated": "2019-04-09T12:25:36.531999+00:00",
                    "versionId": "MTU1NDgxMjczNjUzMTk5OTAwMA"
                },
                "onsetDateTime": "2018-08-22T11:12:53-04:00",
                "resourceType": "Condition",
                "subject": {
                    "reference": "Patient/6f7acde5-db81-4361-82cf-886893a3280c"
                },
                "verificationStatus": "confirmed"
            },
            "search": {
                "mode": "match"
            }
        },
        {
            "fullUrl": "https://syntheticmass.mitre.org/v1/fhir/Condition/cc454676-ccdc-4792-a5c9-cfbedce2ab33",
            "resource": {
                "abatementDateTime": "2011-03-19T11:12:53-04:00",
                "assertedDate": "2011-02-26T10:12:53-05:00",
                "clinicalStatus": "resolved",
                "code": {
                    "coding": [
                        {
                            "code": "444814009",
                            "display": "Viral sinusitis (disorder)",
                            "system": "http://snomed.info/sct"
                        }
                    ],
                    "text": "Viral sinusitis (disorder)"
                },
                "context": {
                    "reference": "Encounter/ee9bd275-49c9-4e40-bc78-ebe53bbfb123"
                },
                "id": "cc454676-ccdc-4792-a5c9-cfbedce2ab33",
                "meta": {
                    "lastUpdated": "2019-04-09T12:25:36.525019+00:00",
                    "versionId": "MTU1NDgxMjczNjUyNTAxOTAwMA"
                },
                "onsetDateTime": "2011-02-26T10:12:53-05:00",
                "resourceType": "Condition",
                "subject": {
                    "reference": "Patient/6f7acde5-db81-4361-82cf-886893a3280c"
                },
                "verificationStatus": "confirmed"
            },
            "search": {
                "mode": "match"
            }
        },
        {
            "fullUrl": "https://syntheticmass.mitre.org/v1/fhir/Condition/bab430ff-5b09-4e4a-8871-6e4fcb84fa17",
            "resource": {
                "assertedDate": "2009-04-05T11:12:53-04:00",
                "clinicalStatus": "active",
                "code": {
                    "coding": [
                        {
                            "code": "38341003",
                            "display": "Hypertension",
                            "system": "http://snomed.info/sct"
                        }
                    ],
                    "text": "Hypertension"
                },
                "context": {
                    "reference": "Encounter/630a642d-0402-454c-9426-c399cf9b2aab"
                },
                "id": "bab430ff-5b09-4e4a-8871-6e4fcb84fa17",
                "meta": {
                    "lastUpdated": "2019-04-09T12:25:36.486194+00:00",
                    "versionId": "MTU1NDgxMjczNjQ4NjE5NDAwMA"
                },
                "onsetDateTime": "2009-04-05T11:12:53-04:00",
                "resourceType": "Condition",
                "subject": {
                    "reference": "Patient/6f7acde5-db81-4361-82cf-886893a3280c"
                },
                "verificationStatus": "confirmed"
            },
            "search": {
                "mode": "match"
            }
        },
        {
            "fullUrl": "https://syntheticmass.mitre.org/v1/fhir/Condition/25b86d4b-5d09-47c6-9446-b93b067e63ec",
            "resource": {
                "abatementDateTime": "2009-01-31T10:12:53-05:00",
                "assertedDate": "2009-01-10T10:12:53-05:00",
                "clinicalStatus": "resolved",
                "code": {
                    "coding": [
                        {
                            "code": "75498004",
                            "display": "Acute bacterial sinusitis (disorder)",
                            "system": "http://snomed.info/sct"
                        }
                    ],
                    "text": "Acute bacterial sinusitis (disorder)"
                },
                "context": {
                    "reference": "Encounter/051b0d30-03d3-4d6d-a070-f8d363ef277f"
                },
                "id": "25b86d4b-5d09-47c6-9446-b93b067e63ec",
                "meta": {
                    "lastUpdated": "2019-04-09T12:25:36.461769+00:00",
                    "versionId": "MTU1NDgxMjczNjQ2MTc2OTAwMA"
                },
                "onsetDateTime": "2009-01-10T10:12:53-05:00",
                "resourceType": "Condition",
                "subject": {
                    "reference": "Patient/6f7acde5-db81-4361-82cf-886893a3280c"
                },
                "verificationStatus": "confirmed"
            },
            "search": {
                "mode": "match"
            }
        },
        {
            "fullUrl": "https://syntheticmass.mitre.org/v1/fhir/Condition/33d0016b-3d90-4647-b797-49d5b874537b",
            "resource": {
                "abatementDateTime": "2009-10-27T11:12:53-04:00",
                "assertedDate": "2009-10-06T11:12:53-04:00",
                "clinicalStatus": "resolved",
                "code": {
                    "coding": [
                        {
                            "code": "444814009",
                            "display": "Viral sinusitis (disorder)",
                            "system": "http://snomed.info/sct"
                        }
                    ],
                    "text": "Viral sinusitis (disorder)"
                },
                "context": {
                    "reference": "Encounter/6956bf29-4bc2-4e41-af3d-1cd3d398eb84"
                },
                "id": "33d0016b-3d90-4647-b797-49d5b874537b",
                "meta": {
                    "lastUpdated": "2019-04-09T12:25:36.478091+00:00",
                    "versionId": "MTU1NDgxMjczNjQ3ODA5MTAwMA"
                },
                "onsetDateTime": "2009-10-06T11:12:53-04:00",
                "resourceType": "Condition",
                "subject": {
                    "reference": "Patient/6f7acde5-db81-4361-82cf-886893a3280c"
                },
                "verificationStatus": "confirmed"
            },
            "search": {
                "mode": "match"
            }
        }
    ],
    "link": [
        {
            "relation": "search",
            "url": "https://syntheticmass.mitre.org/v1/fhir/Condition/?subject%3Areference=Patient%2F6f7acde5-db81-4361-82cf-886893a3280c"
        }
    ],
    "resourceType": "Bundle",
    "total": 5,
    "type": "searchset"
}

FHIR_DIAGNOSTIC_REPORT = {
    "code": {
        "coding": [
            {
                "code": "58410-2",
                "display": "Complete blood count (hemogram) panel - Blood by Automated count",
                "system": "http://loinc.org"
            }
        ],
        "text": "Complete blood count (hemogram) panel - Blood by Automated count"
    },
    "context": {
        "reference": "Encounter/2a0e0f6c-493f-4c5b-bf89-5f98aee24f21"
    },
    "effectiveDateTime": "2014-03-02T10:12:53-05:00",
    "id": "ba93319c-3e5f-4074-ac2a-ff12e369a612",
    "issued": "2014-03-02T10:12:53.714-05:00",
    "meta": {
        "lastUpdated": "2019-04-09T12:25:36.527685+00:00",
        "versionId": "MTU1NDgxMjczNjUyNzY4NTAwMA"
    },
    "resourceType": "DiagnosticReport",
    "result": [
        {
            "display": "Leukocytes [#/volume] in Blood by Automated count",
            "reference": "Observation/324cc373-8b87-4354-bf62-afafe93a760c"
        },
        {
            "display": "Erythrocytes [#/volume] in Blood by Automated count",
            "reference": "Observation/c90d0267-b660-48b8-813c-2ef0fa46e0f7"
        },
        {
            "display": "Hemoglobin [Mass/volume] in Blood",
            "reference": "Observation/97684895-3a6e-4d46-9edd-31984bc7c3a6"
        },
        {
            "display": "Hematocrit [Volume Fraction] of Blood by Automated count",
            "reference": "Observation/f0fcb049-32da-4da0-8687-540e494a3a26"
        },
        {
            "display": "MCV [Entitic volume] by Automated count",
            "reference": "Observation/5814b42c-be27-4ceb-ba63-66e235e22b8f"
        },
        {
            "display": "MCH [Entitic mass] by Automated count",
            "reference": "Observation/1c8d2ee3-2a7e-47f9-be16-abe4e9fa306b"
        },
        {
            "display": "MCHC [Mass/volume] by Automated count",
            "reference": "Observation/6d24fd3b-f895-4f4c-a851-9b53ebd3cf49"
        },
        {
            "display": "Erythrocyte distribution width [Entitic volume] by Automated count",
            "reference": "Observation/a4e4a6d9-dfb4-4a7c-bd6b-1599e3c16ec9"
        },
        {
            "display": "Platelets [#/volume] in Blood by Automated count",
            "reference": "Observation/b0598af4-8ffe-43ba-84e5-b7fb49d3dcd7"
        },
        {
            "display": "Platelet distribution width [Entitic volume] in Blood by Automated count",
            "reference": "Observation/7a9e943a-6638-47cb-931f-18c1b9d7ba3f"
        },
        {
            "display": "Platelet mean volume [Entitic volume] in Blood by Automated count",
            "reference": "Observation/0adc582c-c620-4508-89e8-79ac134a6aa0"
        }
    ],
    "status": "final",
    "subject": {
        "reference": "Patient/6f7acde5-db81-4361-82cf-886893a3280c"
    }
}

# the example is taken from hapi fhir server
# the example is modified, subject patient added
FHIR_SPECIMEN = {
    "resourceType": "Specimen",
    "id": "1168252",
    "meta": {
        "versionId": "1",
        "lastUpdated": "2020-05-19T01:47:46.112+00:00"
    },
    "identifier": [{
        "system": "urn:ietf:rfc:3986",
        "value": "urn:uuid:bc269666-9972-11ea-a751-acde48001122"
    }],
    "accessionIdentifier": {
        "system": "http://mghpathology.org/identifiers/specimens",
        "value": "urn:id:TEST20-0002_A"
    },
    "type": {
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "445405002",
            "display": "Specimen obtained by surgical procedure"
        }]
    },
    "collection": {
        "method": {
            "coding": [{
                "system": "snowmed",
                "code": "69466000",
                "display": "Unknown procedure"
            }]
        },
        "bodySite": {
            "coding": [{
                "system": "snowmed",
                "code": "87100004",
                "display": "Topography unknown"
            }]
        }
    },
    "container": [{
        "identifier": [{
            "system": "urn:ietf:rfc:3986",
            "value": "urn:uuid:bc269918-9972-11ea-a751-acde48001122"
        }],
        "type": {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "434711009",
                "display": "Specimen container"
            }]
        }
    }],
    "subject": {
        "reference": "Patient/6f7acde5-db81-4361-82cf-886893a3280c"
    }
}
