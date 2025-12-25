from math import radians, cos, sin, acos

from hmusers.models import Users
from .models import Jobs, Bids

def calculate_distance(user_lat, user_lon, jobs, radius_km = 5 ):
    def haversine(lat1, lon1, lat2, lon2):
        return 6371 * acos(
            cos(radians(lat1)) * cos(radians(lat2)) * cos(radians(lon2) - radians(lon1)) +
            sin(radians(lat1)) * sin(radians(lat2))
        )

    # Filter out jobs with no creator or missing lat/lon
    jobs = [job for job in jobs if job.created_by and job.created_by.latitude is not None and job.created_by.longitude is not None]

    filtered_jobs = []
    # Annotate distance and filter
    for job in jobs:
        job.distance = haversine(
            float(user_lat),
            float(user_lon),
            float(job.created_by.latitude),
            float(job.created_by.longitude)
        )
        if job.distance <= radius_km:  # <-- must be inside the loop
            filtered_jobs.append(job)
    
    # Sort by nearest first
    filtered_jobs.sort(key=lambda x: x.distance)
    return filtered_jobs  # <-- return filtered jobs, not all

def count_jobs(user_id):
    user = Users.objects.get(id=user_id)
    if user.role == 'seeker':
        started_jobs = Jobs.objects.filter(created_by=user_id, status='Started').count()
        waiting_jobs = Jobs.objects.filter(created_by=user_id, status='Waiting').count()
        ended_jobs = Jobs.objects.filter(created_by=user_id, status='Ended').count()
        bids_arr = []
        B_Jobs = Jobs.objects.filter(created_by=user_id)
        all_Bids = Bids.objects.all()
        for bid in all_Bids:
            if bid.job in B_Jobs:    
             bids_arr.append(bid.job.id)
        total_bids = len(set(bids_arr))
        approved_bids = 0
        rejected_bids = 0
        return started_jobs, waiting_jobs, ended_jobs, total_bids,approved_bids, rejected_bids
    
    elif user.role == 'provider':
        started_jobs = Jobs.objects.filter(assigned_to=user_id, status='Started').count()
        ended_jobs = Jobs.objects.filter(assigned_to=user_id, status='Ended').count()
        approved_bids = Bids.objects.filter(bidder=user_id, status='Approved').count()
        rejected_bids = Bids.objects.filter(bidder=user_id, status='Rejected').count()
        waiting_jobs = 0  # Providers don't have waiting jobs in this context
        total_bids = 0    # Providers don't have total bids in this context
        return started_jobs, waiting_jobs,ended_jobs, total_bids, approved_bids, rejected_bids
    
def count_bids(job_id):
    job_id = Jobs.objects.get(id=job_id)
    job_bids = Bids.objects.filter(job=job_id)

    total_bids = Bids.objects.filter(job=job_id).count()
    minimum_bid_value = job_bids.order_by('bid_amount').values_list('bid_amount', flat=True).first()
    
    return total_bids, minimum_bid_value

def job_status_update(job_id, new_status):
    try:
        job = Jobs.objects.get(id=job_id)
        job.status = new_status
        job.save()
        return True
    except Jobs.DoesNotExist:
        return False
    
def bid_status_update(job_id, new_status, bid_id):
    try:
        for bid in Bids.objects.filter(job=job_id):
            if bid.id == bid_id:
                continue
            bid.status = new_status
            bid.save()
        return True
    except Bids.DoesNotExist:
        return False
def approved_bid_check(job_id):
    try:
        approved_bid = Bids.objects.get(job=job_id, status='Approved')
        if approved_bid:
            return True
    except Bids.DoesNotExist:
        return False
    
def rejected_bid_check(job_id, user_id):
    try:
        user_bids = Bids.objects.filter(job=job_id, bidder=user_id)
        user_bids_count = user_bids.count()
        rejected_bids_count = user_bids.filter(status='Rejected').count()

        if user_bids_count > 0 and rejected_bids_count == user_bids_count:
            return True
        else:
            return False
       
    except Bids.DoesNotExist:
        return False