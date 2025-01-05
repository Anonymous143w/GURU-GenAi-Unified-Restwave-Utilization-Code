def format_chat_history(messages):
    return [(m["content"], "") for m in messages[:-1]]

def validate_file_type(file):
    allowed_types = ['txt', 'pdf']
    return file.name.split('.')[-1].lower() in allowed_types

