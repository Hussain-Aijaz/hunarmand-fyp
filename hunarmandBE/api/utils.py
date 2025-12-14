from math import radians, cos, sin, acos

def calculate_distance(user_lat, user_lon, jobs, radius_km = 5 ):
    def haversine(lat1, lon1, lat2, lon2):
        return 6371 * acos(
            cos(radians(lat1)) * cos(radians(lat2)) * cos(radians(lon2) - radians(lon1)) +
            sin(radians(lat1)) * sin(radians(lat2))
        )

    # Filter out jobs with no creator or missing lat/lon
    jobs = [job for job in jobs if job.created_by and job.created_by.latitude is not None and job.created_by.langitude is not None]

    filtered_jobs = []
    # Annotate distance and filter
    for job in jobs:
        job.distance = haversine(
            user_lat,
            user_lon,
            job.created_by.latitude,
            job.created_by.langitude
        )
        if job.distance <= radius_km:  # <-- must be inside the loop
            filtered_jobs.append(job)
    
    # Sort by nearest first
    filtered_jobs.sort(key=lambda x: x.distance)
    return filtered_jobs  # <-- return filtered jobs, not all
