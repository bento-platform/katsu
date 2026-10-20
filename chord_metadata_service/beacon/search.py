


# permitted entities are 
# individuals   (phenopackets)
# biosamples    (biosamples)
# analyses?     (experiments)
#               (files?)

# ... this is currently what we can read from discovery search

async def beacon_search(beacon_entity, request, permissions):

    # 1 parse out filters, do discovery search, get biosample ids
    # 2 parse out variants, gohan search, get biosample ids 
    # 3 intersect 3 & 4
    # 4 somehow return the correct entity from a list of biosamples 



    ...