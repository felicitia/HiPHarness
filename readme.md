## Paper

**Assessing the Feasibility of Web-Request Prediction Models on Mobile Platforms**. 
Yixue Zhao, Siwei Yin, Adriana Sejfia, Marcelo Schmitt Laser, Haoyu Wang, Nenad Medvidovic.
Accepted at MOBILESoft 2021.

Link to the paper: https://arxiv.org/abs/2011.04654


## Source Code

All of HipHarness’s components are implemented in Python, totaling 1,424 SLOC. [[Link]](https://figshare.com/s/f26f63e80df4f729a752)

## Test Results
The results of each of the 7.3 million prediction models are stored as `HIPHarness-Dataset.RData` file, including the following information. [[Link]](https://figshare.com/s/73897e1955fdef3285c8)
- the anonymized user ID
- the number of requests sent by the user
- the number and percentage of the repeated requests
- the prediction algorithm used
- the data pruning strategy used
- the statistics of the Test Result (i.e., the output of the Test Engine as shown in Algorithm 1): *cache.size*, the number of requests in the *hit set*, the number of requests in the *miss set*, the number of *prefetched* requests, the number of *hit* requests, the number of *miss* requests
- the accuracy results: static precision, static recall, dynamic recall
- the runtime of training the prediction model and evaluating the model

## Data Analysis R Script
All the data analyses are performed through R scripts based on the Test Results stored in `HIPHarness-Dataset.RData`, totaling 1,036 SLOC. [[Link]](https://figshare.com/s/a500916aab317cc785b5)
