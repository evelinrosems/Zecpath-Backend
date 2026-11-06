from core.models import Job


def get_all_jobs():
    return Job.objects.all()


def get_job_by_id(job_id):
    return Job.objects.filter(id=job_id).first()
