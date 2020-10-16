import superdesk.editor_utils as editor_utils


def atomic_filter(block):
    return block.type == "ATOMIC"


def clean_text_macro(item, **kwargs):
    editor_utils.filter_blocks(item, "body_html", atomic_filter)
    return item


name = "Clean text"
label = "Clean text"
callback = clean_text_macro
access_type = "frontend"
action_type = "direct"
# replace_type = 'simple-replace'
replace_type = "keep-style-replace"
