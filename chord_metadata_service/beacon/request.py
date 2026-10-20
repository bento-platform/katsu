

# map vales from beacon request to discovery request format 
# 

# katsu currently has an OR format where permissions exist 
# eg:
# eg diseases=COVID-19&diseases=Glioblastoma searches for individuals matching either query (OR)
# .. this applies only within a single category
# if you query sex=FEMALE&diseases=Glioblastoma this is AND only 

# beacon does not accommodate OR queries
# there is a proposal currently which will probably be close to the final form
# so either adopt that and run with it or implement something else
# ... since we have to implement one way or the other, adopt the current proposal and can adapt later
# but the so-called current proposal is incomplete, ambiguous, and unclear how to implement in GET... is this a POST-only feature?
# this is a bit of a blocker

# for OR queries, we build a list of values 
# see DiscoveryQuery model for this 

# so we map beacon-format filters to katsu format discovery query 
# then launch a katsu discovery query 

