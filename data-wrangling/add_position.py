#!user/bin/python
import campaign_mongo_client
import csv
path = '../csv/ocf_contributions.csv'

ocf_contributions_field_name = ['committee_name','candidate_name','contributor','address','city','state','zip','contributor_type','contribution_type','employer_name','employer_address','amount','date_of_receipt','office','election_year']

candidate_collection = campaign_mongo_client.get_collection('candidates')

rows = csv.DictReader(open(path), fieldnames=ocf_contributions_field_name)
next(rows)
for row in rows:
    if row['office'] != '':
        name = row['candidate_name'].split(' ')
        candidate = candidate_collection.find({'_id.last_name':name[-1].replace('.', ''), '_id.first_name': name[0].replace('.','')})

        if candidate.count() == 1:
            candidate = candidate[0]
        elif candidate.count() > 1:
            for possibility in candidate:
                    print possibility['_id']
                    correct = raw_input('Correct: ')
                    if correct == 'y':
                        candidate = possibility
                        break
            
        else:
            print row['candidate_name'] + ' was not found'
            continue
 
        campaign = {'position':row['office'],'year':row['election_year']}

        if 'campaigns' in candidate and not campaign in candidate['campaigns']:
            candidate['campaigns'].append(campaign)
        else:
             candidate['campaigns'] = [campaign]

        candidate_collection.save(candidate)
