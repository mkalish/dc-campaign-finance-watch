
#!user/bin/python
import campaign_mongo_client

contribution_collection = campaign_mongo_client.get_collection('contributions')

candidate_collection = campaign_mongo_client.get_collection('candidates')

for contribution in contribution_collection.find({'_id.last_name':{'$exists':False}}, timeout=False):
    if contribution['candidate'] != '' and not isinstance(contribution['candidate'], dict):
        name_split = contribution['candidate'].split(' ')
        candidate = candidate_collection.find({'_id.last_name':name_split[-1].replace('.', ''), '_id.first_name':name_split[0].replace('.', '')})
        if candidate.count() > 1:
            for possibility in candidate:
                print possibility['_id']
                print contribution['committee_name']
                correct = raw_input('Correct: ')
                if correct == 'y':
                    candidate = possibility
                    break
        elif candidate.count() == 1:
            candidate = candidate[0]
        else:
            print contribution['candidate']

        contribution['candidate'] = candidate['_id']
        contribution_collection.save(contribution)
        
