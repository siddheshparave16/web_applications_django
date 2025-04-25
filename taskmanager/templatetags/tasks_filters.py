import bleach
from django import template
from django.db.models import Count, Case, When, FloatField
from markdown import markdown
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
def percent_complete(tasks):
    if tasks.exists():
        # Aggregate all count of tasks and completed tasks
        aggregation = tasks.aggregate(
            total=Count("id"), done=Count(Case(When(status="DONE", then=1)))
        )

        # Calculate the percentage
        percent_done = (aggregation["done"] / aggregation["total"]) * 100

        return percent_done

    else:
        return 0


@register.filter
def markdown_to_safe_html(markdown_text):
    # convert markdown to html
    html_content = markdown(markdown_text)

    # sanitize the html
    allowed_tags = [
        "pi",
        "strong",
        "em",
        "ul",
        "ol",
        "li",
        "a",
        "br",
        "code",
        "pre",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
    ]

    allowed_attributes = {"a": ["href", "title", "ref"]}
    allowed_protocols = ["http", "https", "mailto"]

    safe_html = bleach.clean(
        html_content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        protocols=allowed_protocols,
        strip=True,
    )
    safe_html = bleach.linkify(safe_html)
    return mark_safe(safe_html)
