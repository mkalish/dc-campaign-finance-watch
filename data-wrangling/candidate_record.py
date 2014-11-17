#!user/bin/python
import campaign_mongo_client

candidate_collection = campaign_mongo_client.get_collection('candidates')

def get_or_create_candidate(name, committee_name):
    candidate = candidate_collection.find_one({"$or":[{'_id':name},{'committee_name':committee_name}]})
    candidate = candidate_collection.find_one({'_id':name})
    if candidate and committee_name:
        candidate['committee_name'] = committee_name
    else:
        candidate = candidate_collection.find_one({'committee_name':committee_name})
        if candidate and name:
            candidate['_id'] = name

    if candidate:
        return candidate
    else:
        candidate = {}
        candidate['_id'] = name
        candidate['committee_name'] = committee_name
        candidate['contributor_quality'] = 0
        candidate['corporate_donor_count'] = 0
        candidate['individual_donor_count'] = 0
        candidate['other_donor_count'] = 0
        return candidate

def save_candidate(candidate):
    candidate_collection.save(candidate, candidate)

