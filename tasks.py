import logging
from celery import shared_task
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    name="engine.tasks.analyse_job_application",
)
def analyse_job_application(self, job_application_id: str) -> dict:
    from engine.models import JobApplication
    from engine.services.nlp_analyzer import analyse

    try:
        job_app = JobApplication.objects.select_related("user").get(pk=job_application_id)
    except JobApplication.DoesNotExist:
        return {"error": "JobApplication not found"}

    job_app.status = JobApplication.Status.ANALYZING
    job_app.celery_task_id = self.request.id
    job_app.save(update_fields=["status", "celery_task_id", "updated_at"])

    try:
        resume_corpus = job_app.user.get_full_profile_text()
        result = analyse(resume_corpus, job_app.job_description)

        job_app.similarity_score   = result.similarity_score
        job_app.jd_keywords        = result.jd_keywords
        job_app.matching_keywords  = result.matching_keywords
        job_app.missing_keywords   = result.missing_keywords
        job_app.status             = JobApplication.Status.DONE
        job_app.save(update_fields=[
            "similarity_score", "jd_keywords",
            "matching_keywords", "missing_keywords",
            "status", "updated_at",
        ])
        return {
            "job_application_id": str(job_application_id),
            "similarity_score":   result.similarity_score,
            "missing_count":      len(result.missing_keywords),
        }
    except Exception as exc:
        logger.exception("NLP analysis failed for %s", job_application_id)
        job_app.status = JobApplication.Status.ERROR
        job_app.save(update_fields=["status", "updated_at"])
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=60,
    name="engine.tasks.generate_resume_pdf",
    soft_time_limit=120,
    time_limit=180,
)
def generate_resume_pdf(self, generated_resume_id: str) -> dict:
    from engine.models import GeneratedResume
    from engine.services.pdf_compiler import ResumeContext, compile_pdf

    try:
        gen = GeneratedResume.objects.select_related("job_application__user").get(pk=generated_resume_id)
    except GeneratedResume.DoesNotExist:
        return {"error": "GeneratedResume not found"}

    gen.status = GeneratedResume.Status.GENERATING
    gen.celery_task_id = self.request.id
    gen.save(update_fields=["status", "celery_task_id", "updated_at"])

    try:
        job_app = gen.job_application
        user    = job_app.user

        ctx = ResumeContext(
            full_name            = user.get_full_name() or user.username,
            email                = user.email,
            phone                = user.phone,
            location             = user.location,
            linkedin_url         = user.linkedin_url,
            portfolio_url        = user.portfolio_url,
            professional_summary = user.professional_summary,
            work_experience      = user.work_experience,
            education            = user.education,
            skills               = user.skills,
            certifications       = user.certifications,
            projects             = user.projects,
            awards               = user.awards,
            job_title            = job_app.job_title,
            company_name         = job_app.company_name,
            keywords_to_highlight = job_app.matching_keywords or [],
        )

        pdf_bytes = compile_pdf(ctx)
        safe_name = "".join(c if c.isalnum() else "_" for c in job_app.job_title)
        filename  = f"resume_{safe_name[:40]}_{gen.pk}.pdf"

        gen.pdf_file.save(filename, ContentFile(pdf_bytes), save=False)
        gen.status = GeneratedResume.Status.READY
        gen.error_message = ""
        gen.save(update_fields=["pdf_file", "status", "error_message", "updated_at"])

        return {"generated_resume_id": str(generated_resume_id), "filename": filename}

    except Exception as exc:
        logger.exception("PDF compilation failed for %s", generated_resume_id)
        gen.status = GeneratedResume.Status.FAILED
        gen.error_message = str(exc)
        gen.save(update_fields=["status", "error_message", "updated_at"])
        raise self.retry(exc=exc)