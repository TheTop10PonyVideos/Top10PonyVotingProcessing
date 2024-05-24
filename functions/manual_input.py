from classes.printers import err


def input_duration():        
    mins = None
    seconds = None

    while True:
        try:
            if mins is None:
                mins = int(input("Minutes: "))
            seconds = int(input("Seconds: "))
            break
        except:
            continue

    return mins * 60 + seconds


def input_string():
    return input(">> ")

def input_date():
    raise NotImplementedError()

n = {
    "title": input_string,
    "uploader": input_string,
    "upload_date": input_date,
    "duration": input_duration
}

def resolve(video_data: dict):
    for key, value in video_data.items():
        if value is None:
            err(f"Please manually enter the {key}:")
            video_data[key] = n[key]()