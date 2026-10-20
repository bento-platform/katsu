"""Request and response schemas for the Beacon API."""



# response schemas for different config endpoints: /map, /config, /entry-types, /info and / (root, same as /info)
# .. usual approach here is to just serve raw.githubusercontent links for schemas 
# response for /beacon/service-info (already code in katsu, although may need beacon-specific tweaks )
# response for /filtering_terms 
# response for /aggregation_terms if this exists 

# also need schemas for entities for full response, but only a few:
# /individuals uses katsu phenopacket schema 
# /datasets uses beacon datasets model (not katsu datasets)
# /cohorts uses beacon cohorts model (is this optional? it's not super useful)
 
# but what about beacon request schema / response schema? 
# we may not need to emit those, only follow them 

# don't worry too much about schema for now
# make pydantic models for request and response
# use those for validation / response serialization
# start with count / bool only and worry about larger responses later
# always use "resultset" response for everything regardless of request granularity

# models for response from /config, /entry_types, etc? 
# note that the FastAPI models from P2GX have errors (request model in particular has multiple errors)
