# PyGnip - Gnip Client Library for Python

## Historical powertrack

Historical Jobs consist of three distinct phases:

`Phase 1`: The customer creates a new job, and an estimate is run for that returns the expected volumes and time required.

API Methods:

* Create a New Historical Job
* Monitor the Progress of the Estimate

`Phase 2`: The customer either accepts or rejects the job based on the values returned in the estimate.

API Methods:

* Accept Job 
* Reject Job

`Phase 3`: If the customer accepted the job, the data is collected into files, which are then made available for download by the customer.

API Methods:

* Monitor the Progress of the running job
* Download the Completed Job
* The API Methods and their requirements for each phase are described in the documentation below.


### API Methods 

#### Create a new rule

``` python
from pygnip.utils import RuleAPI
from pygnip.historical import GnipBasicAuth

# set basic auth
auth = GnipBasicAuth(user="", pass="", account="")

# api handler
rule_api = RuleAPI(auth)

# add a new rule
rule_1 = {
	"tag":"rule_1", "value":"(airwoot OR woot)"
}

>>rule_api.add_rule(rule_1)
>>True
```


#### Create a new Historical Job

``` python
from pygnip.historical import HistoricalAPI
from pygnip.historical import GnipBasicAuth

# set basic auth
auth = GnipAuth(user="", pass="", account="")

# create api endpoint
historical_api = HistoricalAPI(auth)

# create job
historical_job = historical_api.create_job(
		publisher="twitter",
		streamType="track",
		dataFormat= "original",
  		fromDate= "201309010000",
  		toDate= "201309020000",
  		title= "airwoot_hist_Job1",
  		serviceUsername= "airwoot",
  		rules=rule_list
)

# get the job id
historical_job.id

# create a job class using job_id
historical_job = HistoricalAPI(auth, job_id)
historical_job.job_id

```

#### Review the created job

```
historical_job.review()
```

#### Accept a job

```
historical_job.accept()
```

#### Reject a job

```
historical_job.reject()
```

#### Monitor the progress of job

```
historical_job.ready()
```

#### Download the S3 urls

```
historical_job.download_urls()
```

#### Dump the data from urls to `mongodb` or `redis`

```
historical_job.dump_to_db(db='mongo_or_redis', collection_name="mentions")
```


== Copyright and License ==

(c) 2014 Airwoot.

MIT License

