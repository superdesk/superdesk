
from datetime import datetime
from steps import then, get_json_data, parse_date


@then('next run is on monday "{time}"')
def then_next_run_is_on_monday(context, time):
    data = get_json_data(context.response)
    next_run = parse_date(data.get('next_run'))
    assert isinstance(next_run, datetime)
    assert next_run.weekday() == 0
    assert next_run.strftime('%H%M') == time


@then('last run is set')
def then_there_is_last_run(context):
    data = get_json_data(context.response)
    last_run = parse_date(data.get('last_run'))
    next_run = parse_date(data.get('next_run'))
    assert last_run < next_run
