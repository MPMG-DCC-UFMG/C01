import numpy as np

class Estimator:
    '''Implement some regular visit estimators. More details: https://oak.cs.ucla.edu/~cho/papers/cho-thesis.pdf
    '''
    
    @staticmethod
    def estimate_by_changes(num_changes: int, num_visits: int, crawl_interval: float) -> float:
        ''' Estimates the frequency of changes in seconds based on the average changes detected in visits

        Args:
            num_changes: Number of changes detected in crawls
            num_visits: Number of visits made
            crawl_interval: Interval between crawls in seconds previously used
        
        Returns:
            Returns the estimated frequency of changes in seconds

        '''
        
        r = num_changes / num_visits
        return crawl_interval / r

    @staticmethod
    def estimate_by_nochanges(num_changes: int, num_visits: int, crawl_interval: float) -> float:
        ''' Estimates the frequency of changes in seconds based on visits that have not changed

        Args:
            num_changes: Number of changes detected in crawls
            num_visits: Number of visits made
            crawl_interval: Interval between crawls in seconds previously used
        
        Returns:
            Returns the estimated frequency of changes in seconds
            
        '''

        r = - np.log(((num_visits - num_changes) + .5) / (num_visits + .5))
        return crawl_interval / r
