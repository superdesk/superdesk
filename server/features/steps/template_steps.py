
from datetime import datetime, timedelta
from steps import when, then, get_json_data, parse_date


@when('we run create content task')
def when_we_run_create_content_task(context):
    from apps.templates import create_scheduled_content
    now = datetime.now() + timedelta(days=8)
    with context.app.app_context():
        create_scheduled_content(now)


@then('next run is on monday "{time}"')
def then_next_run_is_on_monday(context, time):
    data = get_json_data(context.response)
    next_run = parse_date(data.get('next_run'))
    assert isinstance(next_run, datetime)
    assert next_run.weekday() == 0
    assert next_run.strftime('%H%M') == time
    assert next_run.strftime('%S') == '00', 'there should be no seconds, but it was %s' % (next_run.strftime('%S'), )
