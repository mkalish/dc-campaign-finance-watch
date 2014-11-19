
#!user/bin/python
import campaign_mongo_client

candidate_collection = campaign_mongo_client.get_collection('candidates')

for candidate in candidate_collection.find():
        if not isinstance(candidate['_id'], dict):
            old_id = candidate['_id']
        
            name_doc = {}
            name_split = candidate['_id'].split(' ')
            if candidate['_id'] == '':
                print 'committee is: ' + candidate['committee_name']
                name_doc['first_name'] = raw_input('First Name: ')
                middle_initial = raw_input('Middle Name: ')
                if middle_initial != '':
                    name_doc['middle_initial'] = middle_initial
                name_doc['last_name'] = raw_input('Last Name: ')
                candidate['_id'] = name_doc
            else:
                name_split = candidate['_id'].split(' ')
                name_doc['first_name'] = name_split[0].replace('.', '')
                name_doc['last_name'] = name_split[-1].replace('.', '')
                if len(name_split) == 3:
                    name_doc['middle_initial'] = name_split[1].replace('.', '')


            existing_entry = candidate_collection.find({'_id.last_name':name_doc['last_name'], '_id.first_name':name_doc['first_name']})
            if existing_entry.count() > 1:
                for entry in existing_entry:
                    print entry['_id']
                    correct = raw_input('Correct: ')
                    if correct == 'y':
                        existing_entry = entry
                        break

            if existing_entry.count() == 0:
                candidate['_id'] = name_doc
                candidate['committee_name'] = [candidate['committee_name']]
                candidate_collection.save(candidate)
            else:
                existing_entry = existing_entry[0]
                if not candidate['committee_name'] in existing_entry['committee_name']:
                    existing_entry['committee_name'].append(candidate['committee_name'])
                
                existing_entry['other_donor_count'] += candidate['other_donor_count']
                existing_entry['contributor_quality'] += candidate['contributor_quality']
                existing_entry['individual_donor_count'] += candidate['individual_donor_count']
                existing_entry['corporate_donor_count'] += candidate['corporate_donor_count']
                candidate_collection.save(existing_entry)
            
            candidate_collection.remove({'_id':old_id})
