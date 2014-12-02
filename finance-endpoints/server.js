var restify = require('restify');
var pmongo = require('promised-mongo');
var openCorporateApi = require('./searchOpenCorporate');

/** set up bunyan logging */
var logger =  require('bunyan').createLogger({
    name: 'finance-endpoints',
    streams: [
        {
            path: './endpoints.log',
            type: 'rotating-file',
            period: '1d',
            count: 3,
            level: 'trace'
        },
        {
            level: 'info',
            stream: process.stdout    
        }]
});


var db = require('./campaignFinanceDb')();

var server = restify.createServer({name: 'dc-campaign-finance'});
server.use(restify.queryParser());

function calculateCorporateToGrassRootRatio(corporateDonors, individualDonors) {
    var ratio = null;
    if(corporateDonors == 0){
        ratio = 1;
    } else if(individualDonors == 0){
        ratio = 0;
    } else {
        ratio = corporateDonors/individualDonors;
    }

    return ratio;
};

function calculateContributorQuality(numberOfDonors, quality){
    return quality/(numberOfDonors*8);
};

function constructResourceUrl(endpoint, id, queryParams) {
    var url = '/dc-campaign-finance/api/' + endpoint + '/' + id + '?';
    for(key in queryParams) {
        url = url + key + '=' + queryParams[key] + '&';
    }

    return url;    
    
}

server.get('/test', function(req, res, next) {
    res.json({message:'this is a test endpoint'});
});

server.get('/dc-campaign-finance/api/candidate', function(req, res, next) {
    logger.debug('getting all candidates');
    db.candidates.find({},{'_id':1}).toArray().then(function(candidate_docs){
        candidates = candidate_docs.map(function(candidate){
            var id = candidate._id.last_name;
            delete candidate._id.last_name;
            return {
                candidate: candidate._id,
                resourceUrl: constructResourceUrl('candidate', id, candidate._id)
            }
        });
        res.send(candidates);
    });
});

server.get('/dc-campaign-finance/api/candidate/:name', function(req, res, next){
    logger.debug('retrieving candidate information for %s', req.params.name);
    var id = {'_id.last_name': req.params.name};
    if(req.query.first_name) {
        id['_id.first_name'] = req.query.first_name;
    }
    if(req.query.middle_initial){
        id['_id.middle_initial'] = req.query.middle_initial;
    }
    logger.info(id);
    db
        .candidates
        .findOne(id)
        .then(function(candidate){
            if(!candidate) res.json({'message':'unable to find the candidate'});
            
            var candidateResponse = {};
            candidateResponse.name = candidate._id;
            var corporateDonors = candidate.corporate_donor_count;
            var individualDonors = candidate.individual_donor_count;
            var otherDonors = candidate.other_donor_count;
            var totalDonors = corporateDonors + individualDonors + otherDonors;
            candidateResponse.numberOfDonors = totalDonors;
            candidateResponse.corporateToGrassRootRatio = calculateCorporateToGrassRootRatio(corporateDonors, individualDonors);
            candidateResponse.contributorQuality = calculateContributorQuality(totalDonors, candidate.contributor_quality);
            return candidateResponse;
        })
        .then(function(candidate){
            db.contributions
                .find({'candidate':candidate.name})
                .limit(50)
                .toArray()
                .then(function(contributions) {
                    console.log(candidate.name);
                    candidate.contributions = contributions;
                    db
                        .contributions
                        .find({'candidate':candidate.name})
                        .count(function(err, count){
                            if(count <= 50) {
                                candidate.moreContributions = false;
                            } else {
                                candidate.moreContributions = true;
                            }
                            res.send(candidate);
                    });
        }, function(err){
            console.log(err);       
        });
    });    
});

server.get('/dc-campaign-finance/api/position/:position/:year', function(req, res, next){
    logger.info('retrieving information for %s race in %s', req.params.position, req.params.year);
    db.candidates
        .find({campaigns:{position:req.params.position, year:req.params.year}})
        .toArray()
        .then(function(candidates, err){
            if(err) res.json({'message':'unable to find the requested year'});
            res.json({
                position: req.params.position,
                year: req.params.year,
                candidates: candidates
            });      
        });
});     

server.get('/dc-campaign-finance/api/positions/:year', function(req, res, next) {
    logger.info('gathering all races for %s', req.params.year);
    db
        .candidates
        .distinct('campaigns.position', {'campaigns.year':req.params.year})
        .then(function(races, err) {
            if(err) logger.error(err);
            res.send(races);
        });
});

server.get('/dc-campaign-finance/api/candidate/:name/contributions/:page', function(req, res, next){
    var skipAmount = req.params.page * 50;
    logger.debug(skipAmount);
    db.contributions.find({'candidate':req.params.name})
        .skip(skipAmount)
        .limit(50).toArray()
        .then(function(contributions){
            response = {};
            response.contributions = contributions;
            db.contributions.find({'candidate':req.params.name})
                .count(function(err, count){
                    console.log(count);
                    if(count <= (skipAmount+50)) {
                        response.moreContributions = false
                    } else {
                        response.moreContributions = true;
                    }
                    res.send(response);
                });
        });
});

server.listen(process.env.PORT || 3000, function(){
    console.log('%s listening at %s', server.name, server.url);
});
